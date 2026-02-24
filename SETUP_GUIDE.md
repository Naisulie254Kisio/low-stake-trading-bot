# Complete Setup Guide for Deriv Trading Bot

## Step-by-Step Setup Instructions

### Step 1: Get Your Deriv API Token

1. **Create a Deriv Account** (if you don't have one):
   - Go to https://app.deriv.com
   - Sign up with email/social account
   - Verify your email

2. **Get API Token**:
   - Log in to https://app.deriv.com
   - Click on your profile icon (top right)
   - Select **Settings**
   - Go to **API Tokens** (left menu)
   - Click **Create New Token**
   - Give it a name: "Trading Bot"
   - Check these permissions:
     - ✅ `trade` (to place trades)
     - ✅ `read` (to read account info)
   - Click **Create**
   - **Copy and save the token** (you won't see it again!)

3. **Get Your App ID** (Optional - default 1089 works):
   - Same page where you got the token
   - Find your default App ID or create one
   - Default is usually: **1089**

### Step 2: Install Python & Dependencies

1. **Check Python Installation**:
   ```bash
   python --version
   ```
   Should be 3.8+. If not, download from https://www.python.org/

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

   This installs:
   - `websocket-client` - Connect to Deriv API
   - `requests` - HTTP requests
   - `python-dotenv` - Load environment variables
   - `numpy` - Math calculations
   - `pandas` - Data handling

### Step 3: Configure the Bot

1. **Copy the example config**:
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` file** with your credentials:
   ```
   DERIV_API_TOKEN=your_api_token_here
   DERIV_APP_ID=1089
   ACCOUNT_TYPE=demo
   TRADING_PAIR=R_100
   STAKE=1
   RISK_REWARD_RATIO=5
   RSI_PERIOD=14
   RSI_OVERBOUGHT=70
   RSI_OVERSOLD=30
   ```

   **Important**: 
   - Start with `ACCOUNT_TYPE=demo`
   - Don't share `.env` file (contains your token!)

### Step 4: Test the Connection

Create a test file `test_connection.py`:

```python
import json
import websocket
from config import *

def on_message(ws, message):
    data = json.loads(message)
    if 'authorize' in data:
        print("✓ Connection successful!")
        print(data)
        ws.close()
    elif 'error' in data:
        print("✗ Error:", data['error'])
        ws.close()

def on_error(ws, error):
    print("✗ Error:", error)

def test_connection():
    ws = websocket.WebSocketApp(
        DERIV_SERVER,
        on_message=on_message,
        on_error=on_error
    )
    
def on_open(ws):
        auth = {"authorize": DERIV_API_TOKEN}
        ws.send(json.dumps(auth))
    
    ws.on_open = on_open
    ws.run_forever(ping_interval=30, ping_payload="")

if __name__ == "__main__":
    print("Testing connection to Deriv API...")
    test_connection()
```

Run it:
```bash
python test_connection.py
```

You should see: `✓ Connection successful!`

### Step 5: Run the Bot

```bash
python deriv_bot.py
```

### Step 6: Monitor the Trading

The bot will:
1. Connect to Deriv API ✓
2. Subscribe to price updates
3. Calculate RSI
4. Wait for signals
5. Place trades automatically
6. Track profit/loss

**Example output**:
```
2026-02-24 10:15:30 - INFO - DERIV TRADING BOT - LOW STAKE VERSION
2026-02-24 10:15:32 - INFO - ✓ Connected to Deriv API
2026-02-24 10:15:33 - INFO - ✓ Authorization successful
2026-02-24 10:16:15 - INFO - [10:16:15] Price: $123.45 | RSI: 28.5 | Signal: BUY
2026-02-24 10:16:15 - INFO - 📊 TRADE SIGNAL: BUY (CALL)
2026-02-24 10:17:15 - INFO - ✓ WIN | Profit/Loss: $5.00
```

## Understanding the Output

| Symbol | Meaning |
|--------|---------|
| ✓ | Success |
| ✗ | Error |
| → | Action being performed |
| ⚠ | Warning |
| 📊 | Trading signal |

## Trading Explanation

### What is RSI?

**RSI (Relative Strength Index)** measures momentum:
- **RSI < 30**: Asset is oversold → likely to go UP (BUY signal)
- **RSI > 70**: Asset is overbought → likely to go DOWN (SELL signal)
- **30-70**: Normal range, no signal

### Risk/Reward 1:5

- **You risk**: $1 per trade
- **You can win**: $5 per trade
- **You can lose**: $1 per trade

**Break-even point**: Win rate > 16.7% (1 out of 6)
**Profitable**: Win rate > 20%

### Trade Duration

Each trade lasts **60 seconds**. After 60 seconds:
- Deriv calculates if you won or lost
- Profit/loss is added to your account
- Next trade can be placed

## Important Tips

### ✅ Do's
- ✅ Start with DEMO account
- ✅ Run for at least 24 hours before real money
- ✅ Monitor the bot regularly
- ✅ Keep API token secret
- ✅ Track your results
- ✅ Adjust RSI settings based on performance

### ❌ Don'ts
- ❌ Don't use real money immediately
- ❌ Don't share your API token
- ❌ Don't leave running unattended for weeks
- ❌ Don't modify code without understanding it
- ❌ Don't ignore losses

## Troubleshooting

### Problem: "Authorization failed"

**Solution**:
1. Check API token is correct (copy from Deriv again)
2. Ensure you selected correct permissions: `trade` and `read`
3. Token might be expired - create a new one

### Problem: "WebSocket connection closed"

**Solution**:
1. Check your internet connection
2. Bot will auto-retry after 30 seconds
3. If persistent, check Deriv API status

### Problem: "No trading signals"

**Solution**:
1. RSI needs 14+ price updates (takes ~1-2 minutes)
2. Market might not be in oversold/overbought
3. Wait longer for signals to appear
4. Try adjusting RSI settings:
   - Decrease RSI_OVERBOUGHT (e.g., 65 instead of 70)
   - Increase RSI_OVERSOLD (e.g., 35 instead of 30)

### Problem: "Trades not profitable"

**Solution**:
1. Win rate is too low - adjust RSI:
   - More aggressive: RSI_OVERSOLD=35, RSI_OVERBOUGHT=65
   - More conservative: RSI_OVERSOLD=25, RSI_OVERBOUGHT=75
2. Market might be in trend - RSI works best in ranging markets
3. Run longer to get statistical significance
4. Try different TRADING_PAIR (e.g., R_50, R_75)

## Next Steps

1. **Test in demo** for 24+ hours
2. **Analyze results** - Calculate your win rate
3. **If profitable** - Transfer real funds (small amount)
4. **Scale up** - Increase stake gradually
5. **Monitor regularly** - Don't let it run completely unattended

## Support Resources

- **Deriv API Docs**: https://api.deriv.com/docs
- **Deriv Community**: https://community.deriv.com
- **Trading Basics**: https://www.investopedia.com/terms/r/rsi.asp

---

**Good luck with your trading! Remember: Start small, test thoroughly, scale gradually.** 📈