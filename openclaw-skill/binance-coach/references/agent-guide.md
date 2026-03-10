# BinanceCoach — Agent Guide (OpenClaw Internal)

This file contains full dispatch instructions for OpenClaw. Read this when you need to know exactly which command to run for a given user request.

---

## ⚠️ Security Notes for Agents

- **API keys are written directly to `~/workspace/binance-coach/.env` on disk** — never log them in conversation history, never store them in memory files, never include them in tool call output
- **`.env` is gitignored** — it will never be committed to any repo
- **Only read-only Binance keys are needed** — no trading, no withdrawal permissions ever
- **In OpenClaw mode, no Anthropic key is needed** — OpenClaw IS Claude. Do not ask for or store an Anthropic API key
- When writing `.env`, use the `write` tool directly — do not echo secrets to terminal output

---

## Updating BinanceCoach

When a user says "update BinanceCoach", "upgrade the skill", or "get the latest version":

1. First show what's changing:
```bash
clawhub info binance-coach 2>/dev/null || echo "Check https://clawhub.ai/skills/binance-coach for latest changelog"
```

2. Then update (preserves .env and data/):
```bash
scripts/bc.sh update
```

This does three things:
1. `clawhub update binance-coach` — pulls latest skill files from ClaWHub
2. Copies new bundled `src/` to `~/workspace/binance-coach/` — preserves `.env` and `data/alerts.db`
3. Re-runs `pip install` in case dependencies changed

The user's API keys and alert history are **never touched**.

---

## Setup Check (always do this first)

```bash
ls ~/workspace/binance-coach/.env 2>/dev/null || echo "NOT CONFIGURED"
```

If not configured → follow the setup flow below.

---

## Setup Flow

**Step 1 — Copy bundled source**
```bash
SKILL_DIR="/path/to/skills/binance-coach"
mkdir -p ~/workspace/binance-coach/data
cp -r "$SKILL_DIR/src/." ~/workspace/binance-coach/
pip3 install --break-system-packages -q -r ~/workspace/binance-coach/requirements.txt
```

**Step 2 — Ask for Binance API keys (required)**
> "Go to binance.com → Account → API Management → Create API with **Read Only** permissions only. Paste your API Key and Secret here."

Write to `.env` using the `write` tool (not echo/terminal):
```
BINANCE_API_KEY=<key>
BINANCE_API_SECRET=<secret>
LANGUAGE=en
RISK_PROFILE=moderate
DCA_BUDGET_MONTHLY=500
AI_MODEL=claude-haiku-4-5-20251001
```

**Step 3 — Preferences (optional)**
> "What's your monthly DCA budget in USD? (default: $500) And risk profile: conservative / moderate / aggressive? (default: moderate)"

**Step 4 — Telegram bot (only if explicitly requested)**
> "Create a bot via @BotFather on Telegram: /newbot → copy the token. Get your Telegram user ID from @userinfobot."

Add to `.env`:
```
TELEGRAM_BOT_TOKEN=<token>
TELEGRAM_USER_ID=<your_id>
```
Then start: `scripts/bc.sh telegram`

---

## .env Template

```env
BINANCE_API_KEY=...
BINANCE_API_SECRET=...
LANGUAGE=en
RISK_PROFILE=moderate
DCA_BUDGET_MONTHLY=500
AI_MODEL=claude-haiku-4-5-20251001
# Optional — standalone Telegram bot only:
TELEGRAM_BOT_TOKEN=...
TELEGRAM_USER_ID=...
```

---

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
| Update skill | `bc.sh update` |

Available learn topics: `rsi_oversold`, `rsi_overbought`, `fear_greed`, `dca`, `sma_200`, `concentration_risk`, `panic_selling`

---

## AI Coaching in OpenClaw Mode

**In OpenClaw mode, you ARE Claude — do NOT call `bc.sh coach`, `bc.sh weekly`, or `bc.sh ask`.**

Those commands require a standalone `ANTHROPIC_API_KEY` and are only for the Telegram bot (standalone mode). In OpenClaw mode, Claude is already built in.

Instead — fetch data and analyze it yourself:
1. `bc.sh portfolio` → portfolio holdings, health score
2. `bc.sh behavior` → FOMO score, overtrading, panic sells
3. `bc.sh fg` → Fear & Greed index
4. `bc.sh dca` → DCA multipliers and weekly amounts
5. `bc.sh market <SYMBOL>` → price, RSI, SMA200 for specific coins

Then synthesize the output and respond as the coach directly.

---

## Output Handling

- `portfolio` → summarize score, grade, top holdings, concentration warnings, suggestions
- `dca` → share multiplier (×1.0 / ×1.3 / ×2.0 etc.) and weekly amount per coin, plus reasoning
- `behavior` → highlight FOMO score, overtrading label, panic sells detected
- `fg` → share score, label, and buy/hold/accumulate advice
- `market` → share price, RSI zone, trend, vs SMA200 %

---

## Updating Config

```bash
sed -i '' 's/^LANGUAGE=.*/LANGUAGE=nl/' ~/workspace/binance-coach/.env
sed -i '' 's/^DCA_BUDGET_MONTHLY=.*/DCA_BUDGET_MONTHLY=750/' ~/workspace/binance-coach/.env
sed -i '' 's/^RISK_PROFILE=.*/RISK_PROFILE=aggressive/' ~/workspace/binance-coach/.env
```

## Language

Set via `.env` or per-command:
```bash
bc.sh --lang nl portfolio
```
