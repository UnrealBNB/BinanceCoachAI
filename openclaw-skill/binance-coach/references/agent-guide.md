# BinanceCoach — Agent Guide (OpenClaw Internal)

This file contains full dispatch instructions for OpenClaw. Read this when you need to know exactly which command to run for a given user request.

## Setup Check (always do this first)

```bash
ls ~/workspace/binance-coach/.env 2>/dev/null || echo "NOT CONFIGURED"
```

If not configured → follow the conversational setup flow below.

## Conversational Setup Flow

Ask each question in chat, then write answers to `.env`.

**Step 1 — Binance API keys (required)**
> "Go to binance.com → Account → API Management → Create API (Read Only). Paste your API Key and Secret here."

Write to `.env`:
```
BINANCE_API_KEY=...
BINANCE_API_SECRET=...
```

**Step 2 — Preferences (optional, defaults are fine)**
> "What's your monthly DCA budget? (default: $500) And risk profile: conservative / moderate / aggressive? (default: moderate)"

**Step 3 — Language**
> "Preferred language: English (en) or Dutch (nl)? (default: en)"

**Step 4 — Telegram bot (only if user explicitly asks)**
> "Create a bot via @BotFather on Telegram: send /newbot, pick any name and username, copy the token. Also send a message to @userinfobot to get your Telegram user ID."

Write to `.env`:
```
TELEGRAM_BOT_TOKEN=...
TELEGRAM_USER_ID=...
```
Then start: `scripts/bc.sh telegram`

## Updating Config

```bash
# Change a single setting
sed -i '' 's/^LANGUAGE=.*/LANGUAGE=nl/' ~/workspace/binance-coach/.env
sed -i '' 's/^DCA_BUDGET_MONTHLY=.*/DCA_BUDGET_MONTHLY=750/' ~/workspace/binance-coach/.env
sed -i '' 's/^RISK_PROFILE=.*/RISK_PROFILE=aggressive/' ~/workspace/binance-coach/.env
```

## .env Template

```env
BINANCE_API_KEY=...
BINANCE_API_SECRET=...
LANGUAGE=en
RISK_PROFILE=moderate
DCA_BUDGET_MONTHLY=500
AI_MODEL=claude-haiku-4-5-20251001
TELEGRAM_BOT_TOKEN=...        # optional
TELEGRAM_USER_ID=...          # optional
```

## Command Dispatch Table

Run all commands via:
```bash
bash /path/to/skills/binance-coach/scripts/bc.sh <command>
```

| User asks | Command |
|---|---|
| Portfolio / holdings / health | `bc.sh portfolio` |
| DCA advice (default coins) | `bc.sh dca` |
| DCA for specific coin | `bc.sh dca DOGEUSDT ADAUSDT` |
| Fear & Greed | `bc.sh fg` |
| Market data for coin | `bc.sh market BTCUSDT` |
| Behavior / FOMO / panic sells | `bc.sh behavior` |
| Set price alert | `bc.sh alert BTCUSDT above 70000` |
| Set RSI alert | `bc.sh alert BTCUSDT rsi_below 30` |
| List alerts | `bc.sh alerts` |
| Check alerts | `bc.sh check-alerts` |
| Learn / education | `bc.sh learn dca` |
| 12-month projection | `bc.sh project BTCUSDT` |
| Start Telegram bot | `bc.sh telegram` |
| Demo mode | `bc.sh demo` |

Available learn topics: `rsi_oversold`, `rsi_overbought`, `fear_greed`, `dca`, `sma_200`, `concentration_risk`, `panic_selling`

## AI Coaching in OpenClaw Mode

In OpenClaw mode **you are Claude** — do NOT call `bc.sh coach`, `bc.sh weekly`, or `bc.sh ask` (those require a standalone Anthropic key).

Instead:
1. Fetch data: `portfolio`, `behavior`, `fg`, `dca`, `market <coins>`
2. Analyze the output yourself and respond as the coach

## Output Handling

- `portfolio` → summarize score, grade, top holdings, concentration warnings, suggestions
- `dca` → share multiplier (×1.0 / ×1.3 / ×2.0 etc.) and weekly amount per coin, plus the reasoning
- `behavior` → highlight FOMO score, overtrading label, panic sells detected
- `fg` → share score, label, and buy/hold/accumulate advice
- `market` → share price, RSI zone, trend, vs SMA200 %

## Language

Set via `.env` or per-command:
```bash
bc.sh --lang nl portfolio
```
