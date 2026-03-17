import json
import logging
import time
import numpy as np
import websocket
from config import (
    DERIV_API_TOKEN,
    DERIV_SERVER,
    ACCOUNT_TYPE,
    TRADING_PAIR,
    STAKE,
    RISK_REWARD_RATIO,
    RSI_PERIOD,
    RSI_OVERBOUGHT,
    RSI_OVERSOLD,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def calculate_rsi(prices: list, period: int = 14) -> float | None:
    """Calculate RSI using Wilder's smoothing (EMA-based) method."""
    if len(prices) < period + 1:
        return None

    deltas = np.diff(prices)
    gains = np.where(deltas > 0, deltas, 0.0)
    losses = np.where(deltas < 0, -deltas, 0.0)

    # Seed with simple average over the first `period` bars
    avg_gain = float(np.mean(gains[:period]))
    avg_loss = float(np.mean(losses[:period]))

    # Apply Wilder's smoothing for any subsequent bars
    for gain, loss in zip(gains[period:], losses[period:]):
        avg_gain = (avg_gain * (period - 1) + gain) / period
        avg_loss = (avg_loss * (period - 1) + loss) / period

    if avg_loss == 0:
        return 100.0

    rs = avg_gain / avg_loss
    return 100.0 - (100.0 / (1.0 + rs))


class DerivTradingBot:
    def __init__(self):
        self.prices: list[float] = []
        self.active_trade: dict | None = None
        self.profit_loss: float = 0.0
        self.trade_count: int = 0
        self.ws: websocket.WebSocketApp | None = None

    # ------------------------------------------------------------------
    # WebSocket handlers
    # ------------------------------------------------------------------

    def on_open(self, ws):
        logger.info("Connected to Deriv API")
        ws.send(json.dumps({"authorize": DERIV_API_TOKEN}))

    def on_message(self, ws, message: str):
        data = json.loads(message)

        if "error" in data:
            logger.error("API error: %s", data["error"].get("message", data["error"]))
            return

        msg_type = data.get("msg_type")

        if msg_type == "authorize":
            logger.info("✓ Authorization successful")
            self._subscribe_ticks(ws)

        elif msg_type == "tick":
            self._handle_tick(ws, data["tick"])

        elif msg_type == "buy":
            self._handle_buy(data["buy"])

        elif msg_type == "proposal_open_contract":
            self._handle_contract_update(data["proposal_open_contract"])

    def on_error(self, ws, error):
        logger.error("WebSocket error: %s", error)

    def on_close(self, ws, close_status_code, close_msg):
        logger.warning("Connection closed (code=%s). Reconnecting in 30 s…", close_status_code)
        time.sleep(30)
        self.run()

    # ------------------------------------------------------------------
    # API helpers
    # ------------------------------------------------------------------

    def _subscribe_ticks(self, ws):
        ws.send(json.dumps({"ticks": TRADING_PAIR, "subscribe": 1}))
        logger.info("Subscribed to %s ticks", TRADING_PAIR)

    def _handle_tick(self, ws, tick: dict):
        price = float(tick["quote"])
        self.prices.append(price)

        rsi = calculate_rsi(self.prices, RSI_PERIOD)

        if rsi is None:
            logger.info(
                "Collecting prices… (%d/%d)",
                len(self.prices),
                RSI_PERIOD + 1,
            )
            return

        signal = None
        if rsi < RSI_OVERSOLD:
            signal = "BUY"
        elif rsi > RSI_OVERBOUGHT:
            signal = "SELL"

        logger.info(
            "[%s] Price: $%.2f | RSI: %.1f | Signal: %s",
            time.strftime("%H:%M:%S"),
            price,
            rsi,
            signal or "NONE",
        )

        if signal and self.active_trade is None:
            self._place_trade(ws, signal)

    def _place_trade(self, ws, signal: str):
        contract_type = "CALL" if signal == "BUY" else "PUT"
        logger.info("📊 TRADE SIGNAL: %s (%s)", signal, contract_type)

        proposal = {
            "buy": 1,
            "price": STAKE,
            "parameters": {
                "amount": STAKE,
                "basis": "stake",
                "contract_type": contract_type,
                "currency": "USD",
                "duration": 60,
                "duration_unit": "s",
                "symbol": TRADING_PAIR,
            },
        }
        ws.send(json.dumps(proposal))

    def _handle_buy(self, buy: dict):
        self.active_trade = buy
        self.trade_count += 1
        logger.info(
            "→ Trade #%d placed | Contract ID: %s",
            self.trade_count,
            buy.get("contract_id"),
        )
        if self.ws:
            self.ws.send(
                json.dumps(
                    {
                        "proposal_open_contract": 1,
                        "contract_id": buy["contract_id"],
                        "subscribe": 1,
                    }
                )
            )

    def _handle_contract_update(self, contract: dict):
        if contract.get("is_sold"):
            profit = float(contract.get("profit", 0))
            self.profit_loss += profit
            result = "✓ WIN" if profit > 0 else "✗ LOSS"
            logger.info(
                "%s | Profit/Loss: $%.2f | Total P/L: $%.2f",
                result,
                profit,
                self.profit_loss,
            )
            self.active_trade = None

    # ------------------------------------------------------------------
    # Entry point
    # ------------------------------------------------------------------

    def run(self):
        logger.info("DERIV TRADING BOT - LOW STAKE VERSION")
        logger.info(
            "Settings: account=%s pair=%s stake=$%.2f risk/reward=1:%.0f RSI(%d) OB=%.0f OS=%.0f",
            ACCOUNT_TYPE,
            TRADING_PAIR,
            STAKE,
            RISK_REWARD_RATIO,
            RSI_PERIOD,
            RSI_OVERBOUGHT,
            RSI_OVERSOLD,
        )
        if ACCOUNT_TYPE != "demo":
            logger.warning("⚠ Running on a REAL account – trades will use real funds!")

        self.ws = websocket.WebSocketApp(
            DERIV_SERVER,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )
        self.ws.run_forever(ping_interval=30, ping_payload="")


if __name__ == "__main__":
    bot = DerivTradingBot()
    bot.run()
