# Security & Privacy

This document explains what BinanceCoach accesses, what it stores, and how to audit it before use.

## TL;DR

- ✅ Binance API is **read-only** — no trades, no withdrawals possible
- ✅ Secrets stored **only locally** in `.env` — never sent to third parties
- ✅ Source code is **public and auditable** on GitHub
- ✅ All network calls go to known, legitimate APIs only
- ⚠️ Portfolio data is shared with your AI (OpenClaw/Claude) for coaching analysis

---

## What credentials are required?

| Credential | Required | Purpose |
|---|---|---|
| `BINANCE_API_KEY` | ✅ Yes | Authenticate read-only Binance API requests |
| `BINANCE_API_SECRET` | ✅ Yes | Sign requests with HMAC SHA256 (required even for read-only) |
| `ANTHROPIC_API_KEY` | ❌ Optional | Standalone mode only — not needed with OpenClaw |
| `TELEGRAM_BOT_TOKEN` | ❌ Optional | Standalone Telegram bot only — not needed with OpenClaw |
| `TELEGRAM_USER_ID` | ❌ Optional | Restrict standalone bot to one authorized user |

### How to create safe Binance API keys

1. Go to [binance.com](https://binance.com) → Account → API Management
2. Create a new API key
3. Enable **only** "Enable Reading"
4. **Never enable**: Spot Trading, Margin Trading, Futures, Withdrawals
5. Optionally restrict to your IP address for extra security

A read-only key **cannot trade or withdraw funds** — even if the key is compromised.

---

## What data is accessed?

| Data | Source | Stored locally? |
|---|---|---|
| Account balances | Binance API (read-only) | No — fetched live each request |
| Trade history (last 30 days) | Binance API (read-only) | Yes — SQLite DB at `data/behavior.db` |
| Live prices, RSI, SMA | Binance API (klines) | No — cached 30s in memory |
| Fear & Greed Index | [api.alternative.me](https://api.alternative.me/fng/) | No — cached 30s in memory |

### What is stored in `data/behavior.db`?

A local SQLite database containing:
- Trade timestamps, symbols, side (BUY/SELL), quantity, price
- Alert definitions you've set

This file never leaves your machine. You can delete it at any time.

---

## What network calls does BinanceCoach make?

| Host | Purpose | When |
|---|---|---|
| `api.binance.com` | Portfolio, trade history, prices | On every command |
| `api.alternative.me` | Fear & Greed index | On every command |
| `api.anthropic.com` | AI coaching (standalone mode only) | Only if `ANTHROPIC_API_KEY` is set and you run `coach`/`weekly`/`ask` |
| `api.telegram.org` | Standalone Telegram bot | Only if `TELEGRAM_BOT_TOKEN` is set and you run `bc.sh telegram` |

**In OpenClaw plugin mode**: only `api.binance.com` and `api.alternative.me` are called. AI analysis is done by OpenClaw locally — no Anthropic API calls.

---

## GitHub repo and install mechanism

Setup clones code from: **https://github.com/UnrealBNB/BinanceCoachAI**

This is a **public repo** — you can audit every line before running setup:

```bash
# Review before installing
open https://github.com/UnrealBNB/BinanceCoachAI/blob/main/main.py
open https://github.com/UnrealBNB/BinanceCoachAI/blob/main/requirements.txt
```

### Python dependencies (`requirements.txt`)

All packages are well-known, maintained libraries:

| Package | Purpose |
|---|---|
| `python-binance` | Binance REST API client |
| `python-telegram-bot` | Telegram bot framework |
| `anthropic` | Claude AI client |
| `python-dotenv` | Load `.env` files |
| `rich` | Terminal formatting |
| `requests` | HTTP requests (Fear & Greed) |

No obfuscated code, no unusual packages, no data exfiltration.

---

## Where are secrets stored?

All secrets are written to `~/workspace/binance-coach/.env`. This file:

- Is listed in `.gitignore` — **never committed to git**
- Is only readable by your user account
- Can be inspected at any time: `cat ~/workspace/binance-coach/.env`
- Can be deleted at any time to revoke all access

---

## How to audit the installation

```bash
# Check what's in .env (no secrets will be committed to git)
cat ~/workspace/binance-coach/.env

# Check what network connections the app makes
cat ~/workspace/binance-coach/modules/market.py | grep -i "http\|request\|api"

# Check trade history stored locally
sqlite3 ~/workspace/binance-coach/data/behavior.db "SELECT * FROM trades LIMIT 10;"

# Verify .gitignore includes .env
cat ~/workspace/binance-coach/.gitignore
```

---

## Reporting security issues

Found a security issue? Open a GitHub issue at:
https://github.com/UnrealBNB/BinanceCoachAI/issues

Or contact the maintainer: [@UnrealBNB](https://github.com/UnrealBNB)
