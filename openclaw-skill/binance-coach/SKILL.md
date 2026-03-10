---
name: binance-coach
description: AI-powered crypto trading behavior coach for Binance users. Analyzes live portfolio health, detects emotional trading patterns (FOMO, panic selling, overtrading), provides smart DCA recommendations based on RSI + Fear & Greed index, and delivers personalized AI coaching via Claude. Use when a user asks to: analyze their crypto portfolio, get DCA advice, check market conditions (RSI, Fear & Greed, SMA200), review trading behavior/FOMO/panic sells, get AI coaching on their holdings, set price/RSI alerts, learn about crypto concepts (RSI, DCA, SMA200), start a Telegram trading coach bot, or ask anything about their Binance portfolio.
---

# BinanceCoach

AI-powered crypto trading behavior coach. Connects to the user's Binance account (read-only) and provides portfolio analysis, behavioral coaching, and smart DCA recommendations via Claude.

## How AI coaching works in OpenClaw mode

When used as an OpenClaw skill, **only Binance API credentials are required**:

| | OpenClaw skill | Standalone bot |
|---|---|---|
| Binance API key + secret | ✅ Required | ✅ Required |
| Anthropic API key | ❌ Not needed | ✅ Required |
| Telegram bot token | ❌ Not needed | ✅ Required |

Note: both key **and** secret are needed even for read-only access — Binance uses HMAC SHA256 signing for all authenticated endpoints (portfolio, trade history). Public endpoints (price, Fear & Greed) work without credentials.

OpenClaw is already Claude and already handles Telegram. BinanceCoach provides the Binance data layer — OpenClaw does the AI analysis and messaging natively.

The `bc.sh coach`, `bc.sh weekly`, `bc.sh ask`, and `bc.sh telegram` commands exist for standalone use only. In OpenClaw mode, just ask naturally — the data commands are all you need.

## Conversational Setup (IMPORTANT — read this)

**Never assume keys are configured. Always check first:**

```bash
ls ~/workspace/binance-coach/.env 2>/dev/null || echo "NOT CONFIGURED"
```

### First-time setup flow

When the user asks to set up BinanceCoach, or when `.env` is missing, follow this conversational flow — ask each question in chat, then write to `.env`:

**Step 1 — Binance API keys (required)**
Ask: "Go to binance.com → Account → API Management → Create API (Read Only). Paste your API Key and Secret here."
Then write `BINANCE_API_KEY` and `BINANCE_API_SECRET` to `.env`.

**Step 2 — Preferences (optional, have sensible defaults)**
Ask: "What's your monthly DCA budget (default: $500) and risk profile: conservative / moderate / aggressive (default: moderate)?"

**Step 3 — Language (optional)**
Ask: "Preferred language: English (en) or Dutch (nl)? (default: en)"

**Step 4 — Telegram bot (optional, separate feature)**
Only ask if user explicitly wants a standalone Telegram bot.
If yes: "Create a bot via @BotFather on Telegram: send /newbot, pick a name and username, copy the token. Also send a message to @userinfobot to get your Telegram user ID."
Then write `TELEGRAM_BOT_TOKEN` and `TELEGRAM_USER_ID` to `.env`.
Start with: `scripts/bc.sh telegram`

**Never hardcode bot names or tokens.** Each user creates their own bot via @BotFather. The bot name is entirely up to them.

### Updating existing config

If the user says "change my DCA budget" / "switch to Dutch" / "add telegram" etc — just update the relevant line in `.env` directly. No need to re-run full setup.

```bash
# Example: update a single setting
sed -i '' 's/^LANGUAGE=.*/LANGUAGE=nl/' ~/workspace/binance-coach/.env
sed -i '' 's/^DCA_BUDGET_MONTHLY=.*/DCA_BUDGET_MONTHLY=750/' ~/workspace/binance-coach/.env
```

### Full .env reference

```env
BINANCE_API_KEY=...          # required
BINANCE_API_SECRET=...       # required
LANGUAGE=en                  # en or nl
RISK_PROFILE=moderate        # conservative / moderate / aggressive
DCA_BUDGET_MONTHLY=500       # monthly budget in USD
AI_MODEL=claude-haiku-4-5-20251001   # Claude model for standalone mode
TELEGRAM_BOT_TOKEN=...       # optional — only for standalone bot
TELEGRAM_USER_ID=...         # optional — your Telegram numeric user ID
```

## Running Commands

All commands run via:

```bash
scripts/bc.sh <command> [args]
```

## Key Commands

| User asks about | Run |
|---|---|
| Portfolio health/score | `scripts/bc.sh portfolio` |
| DCA for BTC/ETH/BNB | `scripts/bc.sh dca` |
| DCA for specific coin | `scripts/bc.sh dca DOGEUSDT` |
| Fear & Greed index | `scripts/bc.sh fg` |
| Market data for a coin | `scripts/bc.sh market BTCUSDT` |
| Behavioral analysis | `scripts/bc.sh behavior` |
| Set price alert | `scripts/bc.sh alert BTCUSDT above 70000` |
| List alerts | `scripts/bc.sh alerts` |
| Check triggered alerts | `scripts/bc.sh check-alerts` |
| Educational lesson | `scripts/bc.sh learn dca` |
| 12-month DCA projection | `scripts/bc.sh project BTCUSDT` |
| Start standalone Telegram bot | `scripts/bc.sh telegram` |

## Output Handling

- Commands print rich terminal output — relay key findings to the user
- For portfolio: summarise score, grade, top holdings, and suggestions
- For dca: share multiplier and weekly amount per coin, plus rationale
- For behavior: highlight FOMO score, overtrading label, and any panic sells
- For AI coaching (coach/weekly/ask): in OpenClaw mode, fetch data yourself and analyze natively — do not call bc.sh coach/weekly/ask (those need Anthropic key)

## Language

Set via `.env`: `LANGUAGE=en` or `LANGUAGE=nl`
Or per-command: `scripts/bc.sh --lang nl portfolio`

## Full Command Reference

See `references/commands.md` for all commands, flags, and output formats.
See `references/setup.md` for first-time configuration and API key setup.
