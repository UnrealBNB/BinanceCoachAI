# 🧠 BinanceCoach — AI-Powered Trading Behavior Coach

> *Stop trading on emotion. Start trading with intelligence.*

BinanceCoach is an AI assistant that connects to your Binance account (read-only), analyzes your trading behavior, and coaches you toward better financial decisions. It combines behavioral finance, real-time market data, and systematic DCA strategies to help you trade smarter — not harder.

---

## 🎯 Why This Exists

Over 80% of retail crypto traders lose money — not because they lack information, but because they act on **emotion**:

- 📈 FOMO buying at market tops
- 📉 Panic selling at market bottoms
- 🔁 Overtrading during volatile periods
- 💎 Selling too early and watching it recover

BinanceCoach is your AI accountability partner that identifies these patterns in your own trading history and tells you what to do differently.

---

## ✨ Features

### 🔍 Behavioral Bias Detector
Analyzes your last 30 days of trades and detects:

| Metric | What it detects |
|--------|----------------|
| **FOMO Score** (0-100) | Are you buying during extreme greed? Clustering rapid buys near highs? |
| **Overtrading Index** | Trades per week — high frequency typically leads to worse returns |
| **Panic Sell Detector** | Did you sell at a loss, and the price recovered 15%+ since? |
| **Streak Tracker** | Gamified: days without panic sell, weeks of consistent DCA |

### 📐 Smart DCA Advisor
Suggests weekly buy amounts based on a **25-combination matrix** of:
- RSI zone (oversold / neutral-low / neutral / neutral-high / overbought)
- Fear & Greed zone (extreme fear / fear / neutral / greed / extreme greed)

Example: If RSI is oversold AND Fear & Greed shows Extreme Fear → **2.0× your base DCA** (best buying opportunity). If overbought AND Extreme Greed → **0.2× base** (don't chase tops).

Adjusts further based on your **risk profile**: conservative (0.7×), moderate (1.0×), aggressive (1.3×).

### 💼 Portfolio Health Score (0–100)
Grades your portfolio across 5 dimensions:

| Category | Max Points | What's measured |
|----------|-----------|-----------------|
| Diversification | 30 | Number of meaningful non-stablecoin holdings |
| Stablecoin reserve | 20 | % in stablecoins (optimal: 10–30%) |
| Concentration risk | 25 | Top holding as % of total portfolio |
| Chain diversification | 15 | BNB chain exposure vs. multi-chain |
| Dust cleanup | 10 | Number of sub-$5 positions |

### 🔔 Context-Rich Price Alerts
Set alerts that don't just say "price hit X" — they explain **why it matters**:

```
📉 BTCUSDT Alert Triggered!

Price hit $45,000 (your target: $45,000)

📊 Market Context:
• RSI: 28.4 (oversold)
• Trend: recovering
• Fear & Greed: 18 (Extreme Fear)
• vs 200-day SMA: -22.3%

🧠 What this means:
• Dropped to your target and RSI is oversold — this could be a buying opportunity 💎
• Extreme fear in the market — historically these are good accumulation zones
• ⚠️ Below 200-day SMA — long-term trend is bearish, size positions carefully
```

Supported alert types:
- `above` — price crosses above a level
- `below` — price drops below a level
- `rsi_above` — RSI crosses above a value (e.g. overbought trigger)
- `rsi_below` — RSI drops below a value (e.g. oversold entry signal)

### 📚 Contextual Education
Explains concepts in plain language, triggered by what's happening in your portfolio:

- RSI oversold/overbought explained
- Fear & Greed index — how to use it
- Dollar Cost Averaging — why and how
- The 200-day moving average — what institutions watch
- Concentration risk — why diversification matters
- Panic selling — the psychology and how to stop

---

## 🏗️ Project Structure

```
binance-coach/
├── main.py                    # Entry point (CLI + Telegram bot)
├── requirements.txt           # Python dependencies
├── .env                       # Your API keys (never commit this!)
├── .gitignore                 # Excludes .env and data/ from git
├── config.example.env         # Template for .env
│
├── modules/
│   ├── __init__.py
│   ├── market.py              # Binance market data (price, RSI, SMA, Fear & Greed)
│   ├── portfolio.py           # Portfolio analysis & health scoring
│   ├── dca.py                 # Smart DCA advisor (25-combo matrix)
│   ├── behavior.py            # Behavioral bias detector & coaching
│   ├── alerts.py              # Context-rich price alert system
│   └── education.py          # Educational content module
│
├── bot/
│   ├── __init__.py
│   └── telegram_bot.py        # Telegram bot interface
│
└── data/                      # SQLite databases (auto-created, gitignored)
    ├── alerts.db
    └── behavior.db
```

---

## ⚙️ Setup

### Requirements
- Python 3.11 or higher
- A Binance account with a read-only API key
- (Optional) A Telegram bot token for bot mode

### Step 1 — Clone / download the project

```bash
cd ~/workspace
# Already here? You're good.
cd binance-coach
```

### Step 2 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 3 — Configure your API keys

Copy the example config and fill it in:

```bash
cp config.example.env .env
```

Edit `.env`:

```env
# Required: Binance read-only API key
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_api_secret_here

# Optional: Claude AI for enhanced natural language insights
ANTHROPIC_API_KEY=your_anthropic_key_here

# Optional: Telegram bot
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_USER_ID=your_telegram_user_id_here

# Your preferences
RISK_PROFILE=moderate          # conservative / moderate / aggressive
FIAT_CURRENCY=EUR
DCA_BUDGET_MONTHLY=500         # Your monthly DCA budget in FIAT_CURRENCY
```

### Step 4 — Create a Binance read-only API key

1. Log in to [Binance](https://www.binance.com)
2. Go to **Account → API Management**
3. Click **Create API** → choose **System Generated**
4. Give it a name like `BinanceCoach`
5. Under **API restrictions**, enable only:
   - ✅ Enable Reading
   - ❌ Enable Spot & Margin Trading ← **leave OFF**
   - ❌ Enable Withdrawals ← **leave OFF**
6. Copy both the **API Key** and **Secret Key** into your `.env`

> ⚠️ **Security note:** Never share your API key publicly or commit your `.env` file. The `.gitignore` already excludes it. If you accidentally share it, go to Binance API Management and delete/regenerate it immediately.

---

## 🚀 Running BinanceCoach

### Demo Mode (no API key needed)
Shows what the tool can do using only public Binance data:

```bash
python main.py --demo
```

Output includes:
- Live BTC/ETH/BNB market overview (RSI, trend, SMA200)
- Current Fear & Greed index
- Smart DCA recommendations for 3 coins
- 12-month DCA projection

### Interactive CLI Mode

```bash
python main.py
```

You'll get a `coach>` prompt. Available commands:

| Command | Description |
|---------|-------------|
| `portfolio` | Portfolio health score + breakdown |
| `dca` | DCA recommendations for BTC/ETH/BNB |
| `dca SOLUSDT DOTUSDT` | DCA for specific coins |
| `market BTCUSDT` | Full market context for a coin |
| `behavior` | Behavioral bias analysis |
| `alert BTCUSDT below 45000` | Set a price alert |
| `alert BTCUSDT rsi_below 30` | Alert when RSI is oversold |
| `alerts` | List all active alerts |
| `check-alerts` | Manually check if any alerts triggered |
| `learn` | List all educational topics |
| `learn dca` | Read a specific lesson |
| `learn rsi_oversold` | Learn about RSI oversold signals |
| `fg` | Current Fear & Greed index |
| `project BTCUSDT` | 12-month DCA projection |
| `quit` | Exit |

### Telegram Bot Mode

#### Setup
1. Open Telegram and message [@BotFather](https://t.me/BotFather)
2. Send `/newbot` and follow the prompts
3. Copy the token into `.env` as `TELEGRAM_BOT_TOKEN`
4. Get your Telegram user ID: message [@userinfobot](https://t.me/userinfobot)
5. Put your ID in `.env` as `TELEGRAM_USER_ID`

#### Run the bot

```bash
python main.py --telegram
```

#### Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Show help menu |
| `/portfolio` | Portfolio health score |
| `/dca` | DCA recommendations (BTC/ETH/BNB) |
| `/dca SOLUSDT DOTUSDT` | DCA for specific coins |
| `/alert BTCUSDT above 70000` | Set price alert |
| `/alert BTCUSDT rsi_below 30` | Set RSI alert |
| `/alerts` | List active alerts |
| `/behavior` | Behavioral analysis |
| `/learn` | List lessons |
| `/learn dca` | Read a lesson |
| `/fg` | Fear & Greed index |

---

## 📊 How the Smart DCA Matrix Works

BinanceCoach calculates your suggested weekly buy amount using:

```
suggested_weekly = base_weekly × rsi_fg_multiplier × risk_modifier
```

Where:
- `base_weekly = monthly_budget / 4`
- `rsi_fg_multiplier` is looked up from the 25-combination matrix below
- `risk_modifier` = 0.7 (conservative) / 1.0 (moderate) / 1.3 (aggressive)

**Multiplier matrix:**

| RSI Zone | Extreme Fear | Fear | Neutral | Greed | Extreme Greed |
|----------|-------------|------|---------|-------|---------------|
| Oversold | **2.0×** | 1.8× | 1.4× | 1.2× | 1.0× |
| Neutral-Low | 1.7× | 1.5× | 1.0× | 0.8× | 0.5× |
| Neutral | 1.3× | 1.1× | 1.0× | 0.8× | 0.3× |
| Neutral-High | 1.0× | 0.8× | 0.8× | 0.6× | 0.25× |
| Overbought | 0.6× | 0.5× | 0.4× | 0.4× | **0.2×** |

**Example** (€500/month budget, moderate profile, BTCUSDT):
- Base weekly: €500 / 4 = **€125**
- RSI = 28 (oversold) + Fear & Greed = 19 (extreme fear) → **2.0× multiplier**
- Risk modifier: 1.0 (moderate)
- **Suggested this week: €250** → accumulate aggressively at the bottom

---

## 🔐 Security

| What | How it's handled |
|------|-----------------|
| API keys | Stored locally in `.env`, never transmitted |
| API permissions | Read-only by default — no trade or withdraw access |
| Trade history | Stored locally in SQLite (`data/`) — never leaves your machine |
| `.env` in git | Excluded via `.gitignore` |

**If you accidentally commit your `.env` or share your API key:**
1. Go to Binance → Account → API Management
2. Delete the compromised key immediately
3. Create a new one
4. Update your `.env`

---

## 📦 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `binance-connector` | ≥3.7.0 | Official Binance REST API SDK |
| `pandas` | ≥2.0.0 | Data analysis (klines, RSI calculation) |
| `numpy` | ≥1.24.0 | Numerical calculations |
| `anthropic` | ≥0.20.0 | Claude AI for natural language insights |
| `python-telegram-bot` | ≥20.0 | Telegram bot interface |
| `python-dotenv` | ≥1.0.0 | Load `.env` config |
| `rich` | ≥13.0.0 | Beautiful terminal output |
| `requests` | ≥2.31.0 | Fear & Greed index API |
| `aiohttp` | ≥3.9.0 | Async HTTP for bot mode |

---

## 🧪 Testing

### Run demo (no API key):
```bash
python main.py --demo
```

### Quick market check:
```bash
python -c "
from dotenv import load_dotenv; load_dotenv()
import os
from binance.spot import Spot
from modules.market import MarketData
client = Spot(os.getenv('BINANCE_API_KEY'), os.getenv('BINANCE_API_SECRET'))
market = MarketData(client)
ctx = market.get_market_context('BTCUSDT')
print(f'BTC: \${ctx[\"price\"]:,.2f} | RSI: {ctx[\"rsi\"]} | F&G: {ctx[\"fear_greed\"][\"value\"]}')
"
```

### Verify API key works:
```bash
python -c "
from dotenv import load_dotenv; load_dotenv()
import os
from binance.spot import Spot
client = Spot(os.getenv('BINANCE_API_KEY'), os.getenv('BINANCE_API_SECRET'))
info = client.account()
print('API key working. Total assets:', len([b for b in info['balances'] if float(b['free']) > 0]))
"
```

---

## ⚠️ Known Limitations

- **No secret key provided yet** — portfolio and trade history commands require both API key + secret. Market data and demo mode work with key only.
- **Alert polling** — alerts are checked when you run `check-alerts` manually or via the Telegram `/alert` command. Background auto-polling is not yet implemented (planned).
- **Historical Fear & Greed** — the behavioral FOMO score uses the *current* F&G index as a proxy. Per-trade historical F&G requires a paid data API.
- **Futures/Margin** — only Spot wallet is analyzed. Futures positions are not included.

---

## 🗺️ Roadmap

- [ ] Background alert scheduler (poll every 5 minutes)
- [ ] Push notifications via Telegram when alert triggers automatically
- [ ] Historical trade P&L chart
- [ ] AI-generated weekly coaching summary (Claude)
- [ ] Web dashboard (FastAPI + simple HTML)
- [ ] Futures/Margin portfolio support
- [ ] Multi-account support

---

## 🏆 Competition Entry

Built for the **OpenClaw AI Assistant Build Campaign 2026** — deadline March 18, 2026.

**Category:** Portfolio / DCA / Behavioral coaching tool  
**Unique angle:** Behavioral finance meets crypto. Most tools tell you *what* the price is. BinanceCoach tells you *what you're doing wrong* and how to fix it.  
**Social impact:** The #1 reason retail traders lose money isn't lack of information — it's emotional decision-making. This directly solves that.

---

## 📄 License

MIT — free to use, modify, and distribute.
