#!/usr/bin/env bash
# bc.sh — BinanceCoach CLI wrapper for OpenClaw skill
#
# Uses python main.py --command "..." for clean non-interactive output.
# No banner, no prompt, no piping hacks.
#
# Usage:
#   bc.sh <command> [args...]
#   bc.sh --path           (print project path and exit)
#   bc.sh --lang nl <cmd>  (run command in Dutch)

set -euo pipefail

# ── Find project root ────────────────────────────────────────────────────────
find_project() {
    if [[ -n "${BINANCE_COACH_PATH:-}" && -f "$BINANCE_COACH_PATH/main.py" ]]; then
        echo "$BINANCE_COACH_PATH"; return
    fi
    local candidates=("$HOME/.binance-coach" "$HOME/workspace/binance-coach" "$HOME/binance-coach")
    for dir in "${candidates[@]}"; do
        if [[ -f "$dir/main.py" && -f "$dir/.env" ]]; then echo "$dir"; return; fi
    done
    # Relative to skill location (repo-bundled)
    local skill_dir
    skill_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
    if [[ -f "$skill_dir/main.py" ]]; then echo "$skill_dir"; return; fi
    echo ""
}

PROJECT="$(find_project)"

if [[ "${1:-}" == "--path" ]]; then echo "$PROJECT"; exit 0; fi

if [[ -z "$PROJECT" ]]; then
    echo "❌ BinanceCoach project not found."
    echo "   Run: bc.sh setup  OR  set BINANCE_COACH_PATH"
    exit 1
fi

# ── Parse optional --lang flag ───────────────────────────────────────────────
LANG_ARGS=""
if [[ "${1:-}" == "--lang" ]]; then
    shift; LANG_ARGS="--lang ${1:-en}"; shift
fi

COMMAND="${1:-help}"
shift || true
ARGS=("$@")

# ── Load .env ────────────────────────────────────────────────────────────────
if [[ -f "$PROJECT/.env" ]]; then
    set -o allexport; source "$PROJECT/.env"; set +o allexport
fi

# ── Find Python ──────────────────────────────────────────────────────────────
PYTHON="${PYTHON:-}"
if [[ -z "$PYTHON" ]]; then
    for py in python3 python; do
        if command -v "$py" &>/dev/null; then PYTHON="$py"; break; fi
    done
fi

# ── Run via --command flag (clean non-interactive output) ────────────────────
run_cmd() {
    cd "$PROJECT"
    # shellcheck disable=SC2086
    $PYTHON main.py $LANG_ARGS --command "$1"
}

# ── Dispatch ─────────────────────────────────────────────────────────────────
cd "$PROJECT"

case "$COMMAND" in
    portfolio)    run_cmd "portfolio" ;;
    dca)          run_cmd "dca ${ARGS[*]:-}" ;;
    market)       run_cmd "market ${ARGS[0]:-BTCUSDT}" ;;
    fg)           run_cmd "fg" ;;
    behavior)     run_cmd "behavior" ;;
    alert)        run_cmd "alert ${ARGS[*]}" ;;
    alerts)       run_cmd "alerts" ;;
    check-alerts) run_cmd "check-alerts" ;;
    learn)        run_cmd "learn ${ARGS[0]:-}" ;;
    project)      run_cmd "project ${ARGS[0]:-BTCUSDT}" ;;
    coach)        run_cmd "coach" ;;
    weekly)       run_cmd "weekly" ;;
    ask)          run_cmd "ask ${ARGS[*]}" ;;
    models)       run_cmd "models" ;;
    model)        run_cmd "model ${ARGS[0]:-}" ;;
    telegram)
        echo "🤖 Starting BinanceCoach Telegram bot..."
        exec $PYTHON main.py --telegram
        ;;
    demo)         exec $PYTHON main.py --demo ;;
    setup)
        SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
        exec bash "$SCRIPT_DIR/setup.sh"
        ;;
    help|--help|-h)
        echo "BinanceCoach — commands:"
        echo "  portfolio            Portfolio health score & analysis"
        echo "  dca [SYMBOLS]        Smart DCA recommendations"
        echo "  market [SYMBOL]      Market context (price/RSI/SMA/F&G)"
        echo "  fg                   Fear & Greed index"
        echo "  behavior             Behavioral bias analysis"
        echo "  alert SYM COND VAL   Set price/RSI alert"
        echo "  alerts               List active alerts"
        echo "  check-alerts         Check if any alert triggered"
        echo "  learn [TOPIC]        Educational lessons"
        echo "  project [SYMBOL]     12-month DCA projection"
        echo "  coach                AI coaching summary (needs Anthropic key)"
        echo "  weekly               AI weekly brief (needs Anthropic key)"
        echo "  ask <question>       Ask Claude (needs Anthropic key)"
        echo "  models / model <id>  Claude model management"
        echo "  telegram             Start standalone Telegram bot"
        echo "  demo                 Demo mode (no API keys needed)"
        echo "  setup                First-time setup wizard"
        ;;
    *)
        echo "❌ Unknown command: $COMMAND"
        echo "   Run: bc.sh help"
        exit 1
        ;;
esac
