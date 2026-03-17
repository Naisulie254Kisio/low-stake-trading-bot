import os
from dotenv import load_dotenv

load_dotenv()

DERIV_API_TOKEN = os.getenv("DERIV_API_TOKEN", "")
DERIV_APP_ID = os.getenv("DERIV_APP_ID", "1089")
DERIV_SERVER = f"wss://ws.binaryws.com/websockets/v3?app_id={DERIV_APP_ID}"

ACCOUNT_TYPE = os.getenv("ACCOUNT_TYPE", "demo")
TRADING_PAIR = os.getenv("TRADING_PAIR", "R_100")
STAKE = float(os.getenv("STAKE", "1"))
RISK_REWARD_RATIO = float(os.getenv("RISK_REWARD_RATIO", "5"))

RSI_PERIOD = int(os.getenv("RSI_PERIOD", "14"))
RSI_OVERBOUGHT = float(os.getenv("RSI_OVERBOUGHT", "70"))
RSI_OVERSOLD = float(os.getenv("RSI_OVERSOLD", "30"))
