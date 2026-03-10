---
name: binance-coach
description: AI-powered crypto trading behavior coach for Binance users. Analyzes live portfolio health, detects emotional trading patterns (FOMO, panic selling, overtrading), provides smart DCA recommendations based on RSI + Fear & Greed index, and delivers personalized AI coaching via Claude. Use when a user asks to: analyze their crypto portfolio, get DCA advice, check market conditions (RSI, Fear & Greed, SMA200), review trading behavior/FOMO/panic sells, get AI coaching on their holdings, set price/RSI alerts, learn about crypto concepts (RSI, DCA, SMA200), start a Telegram trading coach bot, or ask anything about their Binance portfolio.
license: MIT
metadata:
  {
    "openclaw": {
      "emoji": "📊",
      "homepage": "https://github.com/UnrealBNB/BinanceCoachAI",
      "requires": { "bins": ["python3", "pip3"] },
      "setup": "scripts/setup.sh",
      "source": {
        "type": "github",
        "repo": "https://github.com/UnrealBNB/BinanceCoachAI",
        "branch": "main",
        "install_path": "~/workspace/binance-coach"
      },
      "security": {
        "api_access": "read-only",
        "no_trading": true,
        "no_withdrawal": true,
        "data_stored": "local .env + local SQLite DB only",
        "network_calls": [
          "api.binance.com (read-only portfolio/market data)",
          "api.alternative.me (Fear & Greed index)",
          "api.anthropic.com (optional, standalone mode only)",
          "api.telegram.org (optional, standalone bot only)"
        ]
      },
      "env_vars": [
        { "name": "BINANCE_API_KEY", "description": "Binance read-only API key.", "required": true, "sensitive": true },
        { "name": "BINANCE_API_SECRET", "description": "Binance read-only API secret for HMAC signing.", "required": true, "sensitive": true },
        { "name": "ANTHROPIC_API_KEY", "description": "Claude API key — standalone mode only, not needed with OpenClaw.", "required": false, "sensitive": true },
        { "name": "TELEGRAM_BOT_TOKEN", "description": "Telegram bot token from @BotFather — standalone bot only.", "required": false, "sensitive": true },
        { "name": "TELEGRAM_USER_ID", "description": "Your Telegram user ID — restricts bot to one authorized user.", "required": false, "sensitive": false },
        { "name": "LANGUAGE", "description": "en or nl. Default: en.", "required": false, "sensitive": false },
        { "name": "RISK_PROFILE", "description": "conservative, moderate, or aggressive. Default: moderate.", "required": false, "sensitive": false },
        { "name": "DCA_BUDGET_MONTHLY", "description": "Monthly DCA budget in USD. Default: 500.", "required": false, "sensitive": false }
      ]
    }
  }
---

# 📊 BinanceCoach

> Your AI-powered crypto trading behavior coach — connected to your Binance account.

BinanceCoach analyzes your live Binance portfolio, spots emotional trading patterns like FOMO and panic selling, and gives you smart DCA buy signals based on RSI and the Fear & Greed index — all via your OpenClaw assistant.

---

## ✨ What it does

| Feature | Description |
|---|---|
| 💼 Portfolio Health | Score 0–100 with grade, concentration warnings, stablecoin check |
| 📐 Smart DCA | Weekly buy amounts per coin, adjusted by RSI × Fear & Greed (25 combinations) |
| 🧠 Behavior Analysis | FOMO score, overtrading index, panic sell detector, streak tracker |
| 📈 Market Context | Live price, RSI, SMA50/200, trend direction per coin |
| 😱 Fear & Greed | Real-time index with buy/hold advice |
| 🔔 Price Alerts | Set price or RSI alerts, check when triggered |
| 📚 Education | 7 lessons: RSI, DCA, SMA200, Fear & Greed, concentration risk, panic selling |
| 📅 Projections | 12-month DCA accumulation projection per coin |

---

## 🚀 Quick Start

**Only one credential required when using with OpenClaw:**

```
Binance API key + secret (read-only)
```

> OpenClaw already has Claude built in and handles messaging — no Anthropic key or Telegram bot needed.

Just say: **"analyze my portfolio"** or **"set up BinanceCoach"** — your assistant handles the rest.

---

## 🗣️ Example questions

- *"Analyze my portfolio"*
- *"What's the Fear & Greed index?"*
- *"Give me DCA advice for DOGE and ADA"*
- *"Check my trading behavior"*
- *"Set an alert if BTC drops below $60,000"*
- *"Show me the market context for ETH"*
- *"What's a 12-month DCA projection for BTC?"*
- *"Explain dollar cost averaging"*

---

## 🔐 Security

- **Read-only Binance API** — no trading, no withdrawals possible
- Secrets stored **locally only** in `~/workspace/binance-coach/.env`
- `.env` is gitignored and never committed
- Source code is fully auditable: [github.com/UnrealBNB/BinanceCoachAI](https://github.com/UnrealBNB/BinanceCoachAI)

See [SECURITY.md](SECURITY.md) for full audit guide.

---

## ⚙️ Optional: Standalone Telegram Bot

Want a dedicated Telegram bot (separate from OpenClaw)?

1. Create a bot via [@BotFather](https://t.me/BotFather) — send `/newbot`
2. Get your Telegram user ID from [@userinfobot](https://t.me/userinfobot)
3. Tell your OpenClaw: *"Set up Telegram for BinanceCoach"*

Your assistant will ask for the token and user ID, then start the bot.

---

## 🌍 Languages

Supports **English** and **Dutch (Nederlands)**. Switch anytime:

> *"Switch BinanceCoach to Dutch"*

---

*Built for the Binance OpenClaw AI Assistant Campaign 2026 · [View on GitHub](https://github.com/UnrealBNB/BinanceCoachAI)*

---

<!-- AGENT INSTRUCTIONS — read references/agent-guide.md for full dispatch table -->
