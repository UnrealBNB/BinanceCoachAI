---
name: binance-coach
description: AI-powered crypto trading behavior coach for Binance users. Analyzes live portfolio health, detects emotional trading patterns (FOMO, panic selling, overtrading), provides smart DCA recommendations based on RSI + Fear & Greed index, and delivers personalized AI coaching via Claude. Use when a user asks to: analyze their crypto portfolio, get DCA advice, check market conditions (RSI, Fear & Greed, SMA200), review trading behavior/FOMO/panic sells, get AI coaching on their holdings, set price/RSI alerts, learn about crypto concepts (RSI, DCA, SMA200), start a Telegram trading coach bot, or ask anything about their Binance portfolio.
homepage: https://github.com/UnrealBNB/BinanceCoachAI
env_vars:
  - name: BINANCE_API_KEY
    description: "Binance read-only API key (binance.com → Account → API Management). Enable Read Only permissions only — never enable trading or withdrawal."
    required: true
    sensitive: true
  - name: BINANCE_API_SECRET
    description: "Binance read-only API secret. Required alongside API key for HMAC SHA256 request signing on authenticated endpoints."
    required: true
    sensitive: true
  - name: ANTHROPIC_API_KEY
    description: "Anthropic Claude API key — only needed for the standalone Telegram bot or CLI without OpenClaw. Not required when using via OpenClaw (OpenClaw already provides Claude)."
    required: false
    sensitive: true
  - name: TELEGRAM_BOT_TOKEN
    description: "Telegram bot token from @BotFather — only needed for the optional standalone Telegram bot. Not required in OpenClaw plugin mode."
    required: false
    sensitive: true
  - name: TELEGRAM_USER_ID
    description: "Your numeric Telegram user ID (from @userinfobot) — restricts bot access to one authorized user."
    required: false
    sensitive: false
  - name: LANGUAGE
    description: "Display language: en (English) or nl (Nederlands). Default: en."
    required: false
    sensitive: false
  - name: RISK_PROFILE
    description: "DCA risk profile: conservative, moderate, or aggressive. Affects DCA multipliers. Default: moderate."
    required: false
    sensitive: false
  - name: DCA_BUDGET_MONTHLY
    description: "Monthly DCA budget in USD. Used to calculate weekly buy amounts. Default: 500."
    required: false
    sensitive: false
metadata:
  {
    "openclaw":
      {
        "emoji": "📊",
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
          "data_stored": "local .env file and local SQLite DB (~/workspace/binance-coach/data/)",
          "network_calls": ["api.binance.com (read-only)", "api.alternative.me (Fear & Greed index)", "api.anthropic.com (optional, standalone mode only)"],
          "no_trading": true,
          "no_withdrawal": true
        }
      }
  }
---

# BinanceCoach

AI-powered crypto trading behavior coach. Connects to the user's Binance account (read-only) and provides portfolio analysis, behavioral coaching, and smart DCA recommendations via Claude.

## Security & Privacy

**Read the [SECURITY.md](SECURITY.md) before installing.** Key points:

- Binance API access is **read-only** — no trading, no withdrawals possible
- Secrets are stored **only** in a local `.env` file, never transmitted to third parties
- Runtime code is fetched from a **public, auditable** GitHub repo: [UnrealBNB/BinanceCoachAI](https://github.com/UnrealBNB/BinanceCoachAI)
- Portfolio data is shared with OpenClaw/Claude for analysis — only if you trust your OpenClaw setup

## How AI coaching works in OpenClaw mode

When used as an OpenClaw skill, **only Binance API credentials are required**:

| | OpenClaw skill | Standalone bot |
|---|---|---|
| Binance API key + secret | ✅ Required | ✅ Required |
| Anthropic API key | ❌ Not needed | ✅ Required |
| Telegram bot token | ❌ Not needed | ✅ Required |

Note: both key **and** secret are needed even for read-only access — Binance uses HMAC SHA256 signing for all authenticated endpoints (portfolio, trade history). Public endpoints (price, Fear & Greed) work without credentials.

OpenClaw is already Claude and already handles Telegram. BinanceCoach provides the Binance data layer — OpenClaw does the AI analysis and messaging natively.

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

```bash
# Update a single setting
sed -i '' 's/^LANGUAGE=.*/LANGUAGE=nl/' ~/workspace/binance-coach/.env
sed -i '' 's/^DCA_BUDGET_MONTHLY=.*/DCA_BUDGET_MONTHLY=750/' ~/workspace/binance-coach/.env
```

### Full .env reference

```env
BINANCE_API_KEY=...          # required
BINANCE_API_SECRET=...       # required
LANGUAGE=en                  # en or nl (default: en)
RISK_PROFILE=moderate        # conservative / moderate / aggressive
DCA_BUDGET_MONTHLY=500       # monthly budget in USD
AI_MODEL=claude-haiku-4-5-20251001   # Claude model (standalone mode only)
TELEGRAM_BOT_TOKEN=...       # optional — standalone bot only
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
- For AI coaching: in OpenClaw mode, fetch data and analyze natively — do not call bc.sh coach/weekly/ask (those require a standalone Anthropic key)

## Language

Set via `.env`: `LANGUAGE=en` or `LANGUAGE=nl`
Or per-command: `scripts/bc.sh --lang nl portfolio`

## Full Command Reference

See `references/commands.md` for all commands, flags, and output formats.
See `references/setup.md` for first-time configuration and API key setup.
See `SECURITY.md` for security model, data handling, and audit instructions.
