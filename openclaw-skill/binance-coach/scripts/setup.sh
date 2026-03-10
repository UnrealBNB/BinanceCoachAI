#!/usr/bin/env bash
# setup.sh — First-time BinanceCoach setup
# Installs Python dependencies and creates .env from template

set -euo pipefail

INSTALL_DIR="${BINANCE_COACH_PATH:-$HOME/workspace/binance-coach}"

echo "🚀 BinanceCoach Setup"
echo "   Install dir: $INSTALL_DIR"
echo ""

# ── Clone repo if not present ────────────────────────────────────────────────
if [[ ! -f "$INSTALL_DIR/main.py" ]]; then
    echo "📥 Cloning BinanceCoach..."
    mkdir -p "$(dirname "$INSTALL_DIR")"
    git clone https://github.com/UnrealBNB/BinanceCoachAI.git "$INSTALL_DIR"
else
    echo "✅ Project found at $INSTALL_DIR"
fi

cd "$INSTALL_DIR"

# ── Python dependencies ──────────────────────────────────────────────────────
echo ""
echo "📦 Installing Python dependencies..."
python3 -m pip install -r requirements.txt --quiet 2>&1 || \
    pip3 install -r requirements.txt --break-system-packages --quiet 2>&1
echo "✅ Dependencies installed"

# ── Create .env from template ─────────────────────────────────────────────────
if [[ ! -f "$INSTALL_DIR/.env" ]]; then
    cp "$INSTALL_DIR/config.example.env" "$INSTALL_DIR/.env"
    echo ""
    echo "📝 Created .env from template"
    echo "   Edit $INSTALL_DIR/.env with your API keys:"
    echo ""
    echo "   Required:"
    echo "   • BINANCE_API_KEY     — Binance read-only key"
    echo "   • BINANCE_API_SECRET  — Binance read-only secret"
    echo "   • ANTHROPIC_API_KEY   — Claude API key (console.anthropic.com)"
    echo ""
    echo "   Optional:"
    echo "   • TELEGRAM_BOT_TOKEN  — BotFather token"
    echo "   • TELEGRAM_USER_ID    — Your Telegram user ID"
    echo "   • LANGUAGE            — en or nl (default: en)"
    echo ""
else
    echo "✅ .env already exists — skipping"
fi

# ── Create data dir ───────────────────────────────────────────────────────────
mkdir -p "$INSTALL_DIR/data"

echo ""
echo "✅ BinanceCoach setup complete!"
echo ""
echo "Next steps:"
echo "  1. Edit $INSTALL_DIR/.env with your API keys"
echo "  2. Test: scripts/bc.sh demo"
echo "  3. Full analysis: scripts/bc.sh portfolio"
echo "  4. Telegram bot: scripts/bc.sh telegram"
