#!/usr/bin/env bash
# bc.sh — BinanceCoach CLI wrapper for OpenClaw skill
#
# Usage:
#   bc.sh <command> [args...]
#   bc.sh --path           (print project path and exit)
#   bc.sh --lang nl <cmd>  (run command in Dutch)
#
# Finds the BinanceCoach project in common locations:
#   1. $BINANCE_COACH_PATH env var
#   2. ~/.binance-coach/
#   3. ~/workspace/binance-coach/
#   4. Same directory as this script's parent parent (skill-adjacent install)

set -euo pipefail

# ── Find project root ────────────────────────────────────────────────────────
find_project() {
    # Priority 1: explicit env var
    if [[ -n "${BINANCE_COACH_PATH:-}" && -f "$BINANCE_COACH_PATH/main.py" ]]; then
        echo "$BINANCE_COACH_PATH"
        return
    fi

    # Priority 2: standard install location
    local candidates=(
        "$HOME/.binance-coach"
        "$HOME/workspace/binance-coach"
        "$HOME/binance-coach"
    )

    for dir in "${candidates[@]}"; do
        if [[ -f "$dir/main.py" && -f "$dir/.env" ]]; then
            echo "$dir"
            return
        fi
    done

    # Priority 3: relative to skill location (repo-bundled skill)
    local skill_dir
    skill_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
    if [[ -f "$skill_dir/main.py" ]]; then
        echo "$skill_dir"
        return
    fi

    echo ""
}

PROJECT="$(find_project)"

# ── --path flag ──────────────────────────────────────────────────────────────
if [[ "${1:-}" == "--path" ]]; then
    echo "$PROJECT"
    exit 0
fi

if [[ -z "$PROJECT" ]]; then
    echo "❌ BinanceCoach project not found."
    echo "   Set BINANCE_COACH_PATH or install to ~/workspace/binance-coach/"
    echo "   Run: scripts/setup.sh"
    exit 1
fi

# ── Parse optional --lang flag ───────────────────────────────────────────────
LANG_FLAG=""
if [[ "${1:-}" == "--lang" ]]; then
    shift
    LANG_FLAG="--lang ${1:-en}"
    shift
fi

COMMAND="${1:-help}"
shift || true
ARGS=("$@")

# ── Load .env if present ─────────────────────────────────────────────────────
if [[ -f "$PROJECT/.env" ]]; then
    set -o allexport
    source "$PROJECT/.env"
    set +o allexport
fi

# ── Find Python ──────────────────────────────────────────────────────────────
PYTHON="${PYTHON:-}"
if [[ -z "$PYTHON" ]]; then
    for py in python3 python; do
        if command -v "$py" &>/dev/null && "$py" -c "import anthropic" 2>/dev/null; then
            PYTHON="$py"
            break
        fi
    done
fi
if [[ -z "$PYTHON" ]]; then
    PYTHON="python3"  # fallback — let it fail with a clear error
fi

# ── Dispatch command ─────────────────────────────────────────────────────────
cd "$PROJECT"

case "$COMMAND" in
    portfolio)
        $PYTHON main.py $LANG_FLAG <<< "portfolio
quit" 2>&1 | grep -v "^coach>" | grep -v "^$" | tail -n +3
        ;;
    dca)
        SYMBOLS="${ARGS[*]:-BTCUSDT ETHUSDT BNBUSDT}"
        $PYTHON main.py $LANG_FLAG <<< "dca $SYMBOLS
quit" 2>&1 | grep -v "^coach>" | tail -n +3
        ;;
    market)
        SYM="${ARGS[0]:-BTCUSDT}"
        $PYTHON main.py $LANG_FLAG <<< "market $SYM
quit" 2>&1 | grep -v "^coach>" | tail -n +3
        ;;
    fg)
        $PYTHON main.py $LANG_FLAG <<< "fg
quit" 2>&1 | grep -v "^coach>" | tail -n +3
        ;;
    behavior)
        $PYTHON main.py $LANG_FLAG <<< "behavior
quit" 2>&1 | grep -v "^coach>" | tail -n +3
        ;;
    alert)
        $PYTHON main.py $LANG_FLAG <<< "alert ${ARGS[*]}
quit" 2>&1 | grep -v "^coach>" | tail -n +3
        ;;
    alerts)
        $PYTHON main.py $LANG_FLAG <<< "alerts
quit" 2>&1 | grep -v "^coach>" | tail -n +3
        ;;
    check-alerts)
        $PYTHON main.py $LANG_FLAG <<< "check-alerts
quit" 2>&1 | grep -v "^coach>" | tail -n +3
        ;;
    learn)
        TOPIC="${ARGS[0]:-}"
        $PYTHON main.py $LANG_FLAG <<< "learn $TOPIC
quit" 2>&1 | grep -v "^coach>" | tail -n +3
        ;;
    project)
        SYM="${ARGS[0]:-BTCUSDT}"
        $PYTHON main.py $LANG_FLAG <<< "project $SYM
quit" 2>&1 | grep -v "^coach>" | tail -n +3
        ;;
    coach)
        $PYTHON main.py $LANG_FLAG <<< "coach
quit" 2>&1 | grep -v "^coach>" | tail -n +3
        ;;
    weekly)
        $PYTHON main.py $LANG_FLAG <<< "weekly
quit" 2>&1 | grep -v "^coach>" | tail -n +3
        ;;
    ask)
        QUESTION="${ARGS[*]}"
        $PYTHON main.py $LANG_FLAG <<< "ask $QUESTION
quit" 2>&1 | grep -v "^coach>" | tail -n +3
        ;;
    models)
        $PYTHON main.py $LANG_FLAG <<< "models
quit" 2>&1 | grep -v "^coach>" | tail -n +3
        ;;
    model)
        $PYTHON main.py $LANG_FLAG <<< "model ${ARGS[0]:-}
quit" 2>&1 | grep -v "^coach>" | tail -n +3
        ;;
    telegram)
        echo "🤖 Starting BinanceCoach Telegram bot..."
        exec $PYTHON main.py --telegram
        ;;
    demo)
        exec $PYTHON main.py --demo
        ;;
    help|--help|-h)
        exec $PYTHON main.py --help 2>&1 || true
        echo ""
        echo "BinanceCoach OpenClaw Skill — Commands:"
        echo "  portfolio, dca [SYMBOLS], market [SYM], fg, behavior"
        echo "  alert SYM COND VALUE, alerts, check-alerts"
        echo "  learn [TOPIC], project [SYM]"
        echo "  coach, weekly, ask <question>"
        echo "  models, model <id>"
        echo "  telegram, demo"
        ;;
    *)
        echo "❌ Unknown command: $COMMAND"
        echo "   Run: scripts/bc.sh help"
        exit 1
        ;;
esac
