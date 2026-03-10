# 🧠 BinanceCoach — AI-Powered Trading Behavior Coach

> *Stop trading on emotion. Start trading with intelligence.*

BinanceCoach is an AI assistant that connects to your Binance account (read-only), analyzes your trading behavior, and coaches you toward better financial decisions. It combines behavioral finance, real-time market data, and smart DCA strategies — powered by Claude (Anthropic).

**Built for the [OpenClaw AI Assistant Build Campaign 2026](https://binance.com/en/survey/c707e12435d44eaba19cdbc6bbe6f21d).**

---

## 🚀 Two Ways to Use BinanceCoach

### Option 1 — OpenClaw Skill (Recommended)

BinanceCoach is published on [ClaWHub](https://clawhub.com/skills/binance-coach) as a native OpenClaw skill. Once installed, your OpenClaw assistant handles everything — no commands, just natural conversation.

#### Install

```bash
clawhub install binance-coach
```

#### First-time setup

After installation, tell your OpenClaw assistant to set it up:

> *"Set up BinanceCoach"*

OpenClaw will run the setup script automatically, which:
1. **Copies bundled source** to `~/workspace/binance-coach/` — no internet required, all code ships inside the skill
2. **Installs** Python dependencies via pip
3. **Asks you interactively** for your API keys:
   - Binance API key + secret (read-only) ← **required**
   - Anthropic API key ← **not needed in OpenClaw mode** (see below)
   - Telegram bot token + your user ID (optional, for standalone bot)
   - Language preference (English or Dutch)
   - Risk profile (conservative / moderate / aggressive)
   - Monthly DCA budget
4. **Writes everything to `.env`** — no manual file editing
5. **Verifies** Binance connectivity

> 💡 **When using OpenClaw, you only need Binance API credentials.**
>
> | | OpenClaw skill | Standalone bot |
> |---|---|---|
> | Binance API key + secret | ✅ Required | ✅ Required |
> | Anthropic API key | ❌ Not needed | ✅ Required |
> | Telegram bot token | ❌ Not needed | ✅ Required |
>
> You need both the **API key and secret** — even for read-only access. The secret signs your requests (HMAC SHA256) so Binance knows they're from you. Without it, portfolio/trade data is inaccessible. Public data (prices, Fear & Greed) works without any key.
>
> OpenClaw already has Claude built in and handles Telegram — no extra accounts or API costs beyond Binance.

#### Use it

Just talk naturally to your OpenClaw assistant:

> *"Analyze my crypto portfolio"*  
> *"What should I DCA into this week?"*  
> *"Is my trading behavior healthy?"*  
> *"Should I sell all my DOGE?"* ← Claude already has your live portfolio loaded  
> *"Explain what RSI oversold means"*  
> *"Set an alert for BTC below $60,000"*

No slash commands. No separate app. OpenClaw loads the skill and runs it.

---

### Option 2 — Standalone (CLI + Telegram Bot)

Run BinanceCoach directly as a CLI tool or Telegram bot.

#### Quick install

```bash
git clone https://github.com/UnrealBNB/BinanceCoachAI.git
cd BinanceCoachAI
pip install -r requirements.txt
cp config.example.env .env
# Edit .env with your API keys
python main.py
```

#### Or use the setup script (handles everything interactively)

```bash
bash openclaw-skill/binance-coach/scripts/setup.sh
```

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
| **FOMO Score** (0-100) | Buying during extreme greed? Clustering rapid buys near highs? |
| **Overtrading Index** | Trades per week — high frequency typically leads to worse returns |
| **Panic Sell Detector** | Did you sell at a loss, and the price recovered 15%+ since? |
| **Streak Tracker** | Days without panic sell, weeks of consistent DCA |

### 📐 Smart DCA Advisor
Suggests weekly buy amounts based on a **25-combination matrix** of RSI × Fear & Greed:

| RSI Zone | Extreme Fear | Fear | Neutral | Greed | Extreme Greed |
|----------|-------------|------|---------|-------|---------------|
| Oversold | **2.0×** | 1.8× | 1.4× | 1.2× | 1.0× |
| Neutral-Low | 1.7× | 1.5× | 1.0× | 0.8× | 0.5× |
| Neutral | 1.3× | 1.1× | 1.0× | 0.8× | 0.3× |
| Neutral-High | 1.0× | 0.8× | 0.8× | 0.6× | 0.25× |
| Overbought | 0.6× | 0.5× | 0.4× | 0.4× | **0.2×** |

RSI oversold + Extreme Fear → **2.0× your base DCA** (best buying opportunity).  
Overbought + Extreme Greed → **0.2× base** (don't chase tops).

### 💼 Portfolio Health Score (0–100)
Grades your portfolio across 5 dimensions:

| Category | Max Points | What's measured |
|----------|-----------|-----------------|
| Diversification | 30 | Number of meaningful non-stablecoin holdings |
| Stablecoin reserve | 20 | % in stablecoins (optimal: 10–30%) |
| Concentration risk | 25 | Top holding as % of total portfolio |
| Chain diversification | 15 | BNB chain exposure vs. multi-chain |
| Dust cleanup | 10 | Number of sub-$5 positions |

### 🤖 AI Coaching via Claude (Anthropic)

All AI commands automatically load your **live portfolio data** — Claude never asks "what's your portfolio?" because it already knows:

- **Current holdings** with USD values and percentages
- **Market data** for every coin mentioned in your question (RSI, trend, vs SMA200)
- **Behavioral analysis** — your FOMO score, overtrading index, panic sell history
- **Fear & Greed index**

| Command | What Claude does |
|---------|-----------------|
| `coach` | Full personalized coaching summary of your portfolio |
| `weekly` | Weekly behavior brief + action plan |
| `ask "question"` | Free-form Q&A with full portfolio context pre-loaded |

### 🔔 Context-Rich Price Alerts
Alerts that explain *why it matters*, not just that a price was hit:

```
🔔 BTCUSDT Alert Triggered

Price hit $45,000 (your target: $45,000)

📊 Market Context:
• RSI: 28.4 (oversold)
• Trend: recovering
• Fear & Greed: 18 (Extreme Fear)
• vs 200-day SMA: -22.3%

🧠 What this means:
• RSI oversold — potential buying opportunity 💎
• Extreme fear — historically good accumulation zone
• ⚠️ Below 200-day SMA — size positions carefully
```

Alert types: `above`, `below`, `rsi_above`, `rsi_below`

### 📚 Educational Lessons (EN + NL)
7 built-in lessons: RSI oversold/overbought, Fear & Greed index, DCA, SMA200, concentration risk, panic selling.

### 🌐 Bilingual: English & Dutch
All output, AI prompts, lessons, and Telegram messages available in English and Dutch.  
Switch: `LANGUAGE=nl` in `.env`, or `/lang` in Telegram, or `lang nl` in CLI.

---

## 🏗️ Project Structure

```
BinanceCoachAI/
├── main.py                        # Entry point (CLI + Telegram bot + demo)
├── requirements.txt
├── config.example.env             # .env template
├── .gitignore                     # Excludes .env and data/
│
├── modules/
│   ├── market.py                  # Binance market data (price, RSI, SMA, Fear & Greed)
│   ├── portfolio.py               # Portfolio analysis & health scoring
│   ├── dca.py                     # Smart DCA advisor (25-combo RSI × F&G matrix)
│   ├── behavior.py                # Behavioral bias detector
│   ├── alerts.py                  # Context-rich price alert system
│   ├── education.py               # Educational content module
│   ├── ai_coach.py                # Claude AI coaching engine
│   ├── i18n.py                    # Translation loader
│   ├── tg_utils.py                # Telegram HTML formatting helpers
│   └── locales/
│       ├── en.py                  # English strings + lessons (179 keys, 7 lessons)
│       └── nl.py                  # Dutch strings + lessons
│
├── bot/
│   └── telegram_bot.py            # Telegram bot (17 commands, HTML formatting)
│
├── openclaw-skill/
│   └── binance-coach/             # OpenClaw skill (published on ClaWHub)
│       ├── SKILL.md               # Skill definition — triggers & instructions
│       ├── scripts/
│       │   ├── bc.sh              # CLI wrapper (auto-finds project, dispatches commands)
│       │   └── setup.sh           # Interactive first-time setup
│       └── references/
│           ├── commands.md        # Full command reference
│           └── setup.md           # API key setup guide
│
└── data/                          # SQLite databases (auto-created, gitignored)
```

---

## ⚙️ Configuration

Copy `config.example.env` to `.env` and fill in your keys:

```env
# ── Binance API (read-only) ────────────────────────────────
BINANCE_API_KEY=your_read_only_api_key_here
BINANCE_API_SECRET=your_read_only_api_secret_here

# ── Anthropic (Claude AI) ──────────────────────────────────
ANTHROPIC_API_KEY=your_anthropic_key_here
AI_MODEL=claude-haiku-4-5-20251001   # fast/cheap — or claude-sonnet-4-6 for best quality

# ── Telegram Bot (optional) ────────────────────────────────
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_USER_ID=your_telegram_user_id_here

# ── Preferences ────────────────────────────────────────────
LANGUAGE=en                    # en or nl
RISK_PROFILE=moderate          # conservative / moderate / aggressive
DCA_BUDGET_MONTHLY=500         # Monthly budget in USD
```

### Creating a Binance read-only API key

1. Binance → **Account → API Management → Create API**
2. Enable only: ✅ **Enable Reading** — nothing else
3. Copy key + secret into `.env`

> ⚠️ Never commit `.env`. It's excluded by `.gitignore`. If you accidentally share your key, delete it immediately in Binance API Management.

---

## 🖥️ CLI Usage

```bash
python main.py          # Interactive CLI
python main.py --demo   # Demo (no API key needed — public market data only)
```

| Command | Description |
|---------|-------------|
| `portfolio` | Health score, holdings, suggestions |
| `dca [SYMBOLS]` | Smart DCA recommendations |
| `market BTCUSDT` | Price, RSI, trend, SMA50/200, Fear & Greed |
| `fg` | Fear & Greed index |
| `behavior` | FOMO score, overtrading, panic sells, streaks |
| `alert BTCUSDT below 45000` | Set price alert |
| `alert BTCUSDT rsi_below 30` | Set RSI alert |
| `alerts` | List active alerts |
| `check-alerts` | Manually check if any alerts triggered |
| `learn` | List all 7 lessons |
| `learn dca` | Read a specific lesson |
| `project BTCUSDT` | 12-month DCA projection |
| `coach` | AI coaching summary (Claude) |
| `weekly` | AI weekly brief (Claude) |
| `ask "question"` | Ask Claude anything — full portfolio context pre-loaded |
| `models` | List available Claude models |
| `model claude-sonnet-4-6` | Switch Claude model |
| `lang nl` | Switch language |
| `quit` | Exit |

---

## 🤖 Telegram Bot

```bash
python main.py --telegram
```

All 17 commands registered with Telegram (shows in autocomplete):

| Command | Description |
|---------|-------------|
| `/start` | Help menu |
| `/portfolio` | Portfolio health analysis |
| `/dca [SYMBOLS]` | Smart DCA recommendations |
| `/market [SYMBOL]` | Market context |
| `/fg` | Fear & Greed index |
| `/alert SYMBOL COND VALUE` | Set price/RSI alert |
| `/alerts` | List active alerts |
| `/checkalerts` | Check triggered alerts |
| `/behavior` | Behavioral analysis |
| `/project [SYMBOL]` | 12-month DCA projection |
| `/learn [TOPIC]` | Educational lessons |
| `/coach` | 🤖 AI coaching summary |
| `/weekly` | 🤖 AI weekly brief |
| `/ask <question>` | 🤖 Ask Claude anything |
| `/models` | 🤖 List Claude models |
| `/model <id>` | 🤖 Switch Claude model |
| `/lang` | 🌐 Choose language (inline buttons) |

All messages use Telegram HTML formatting — no Markdown rendering issues.

---

## 🔐 Security

| What | How |
|------|-----|
| API keys | Stored locally in `.env`, never transmitted |
| Binance permissions | Read-only — no trading, no withdrawals |
| Trade history | Stored locally in SQLite (`data/`) — never leaves your machine |
| Telegram bot | Single-user restriction via `TELEGRAM_USER_ID` — others get ⛔ |
| `.env` | Excluded from git via `.gitignore` |

### ⚠️ About the ClaWHub Security Scanner

When installing via ClaWHub, you may see a **"Suspicious"** warning. This is expected and explained below — it does **not** mean the skill is malicious.

The scanner flags two patterns that are accurate but inherent to what this tool does:

**1. "Registry metadata claims no required env vars"**
ClaWHub's registry API doesn't store declared env vars for any skill — it's a platform limitation. The scanner compares the registry (which always says "none") against the SKILL.md (which correctly declares `BINANCE_API_KEY` as required) and flags the mismatch. This cannot be fixed without ClaWHub updating their infrastructure.

**2. "Portfolio data sent to Anthropic"**
If you configure `ANTHROPIC_API_KEY` (optional, standalone mode only), the `/coach`, `/weekly`, and `/ask` commands will send your portfolio data to Anthropic's API for AI analysis. This is documented, intentional, and only happens if you explicitly provide that key.

**In OpenClaw mode, no data is sent to Anthropic** — OpenClaw already has Claude built in and analyzes locally.

**What to verify before installing:**
- Create a Binance API key with **Read Only** permissions only
- Skip `ANTHROPIC_API_KEY` unless you're running the standalone bot
- Audit the bundled source: everything is in `openclaw-skill/binance-coach/src/`

---

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| `binance-connector` | Official Binance REST API SDK |
| `pandas` | RSI + moving average calculations |
| `anthropic` | Claude AI coaching |
| `python-telegram-bot` | Telegram bot interface |
| `python-dotenv` | Load `.env` config |
| `rich` | Terminal output formatting |
| `requests` | Fear & Greed index API |
| `aiohttp` | Async HTTP for bot mode |

---

## ⚠️ Known Limitations

- **Spot only** — Futures and Margin positions are not included
- **Alert polling** — Alerts are checked manually (`check-alerts`) or via `/checkalerts`. Background auto-polling is not yet implemented
- **Historical Fear & Greed** — The FOMO score uses the current F&G index as a proxy. Per-trade historical F&G requires a paid data provider

---

## 🏆 Competition Entry

Built for the **[OpenClaw AI Assistant Build Campaign 2026](https://binance.com/en/survey/c707e12435d44eaba19cdbc6bbe6f21d)** by [@UnrealBNB](https://twitter.com/UnrealBNB).

**Category:** Trading & Strategy Tools · Asset Management · Education

**Unique angle:** Most crypto tools tell you *what* the price is. BinanceCoach tells you *what you're doing wrong behaviorally* and how to fix it — backed by real analysis of your actual trade history, not generic advice.

---

## 📄 License

MIT — free to use, modify, and distribute.
