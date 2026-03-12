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
    # 1. Explicit env override
    if [[ -n "${BINANCE_COACH_PATH:-}" && -f "$BINANCE_COACH_PATH/main.py" ]]; then
        echo "$BINANCE_COACH_PATH"; return
    fi
    # 2. Standard workspace locations
    local candidates=("$HOME/workspace/binance-coach" "$HOME/.binance-coach" "$HOME/binance-coach")
    for dir in "${candidates[@]}"; do
        if [[ -f "$dir/main.py" && -f "$dir/.env" ]]; then echo "$dir"; return; fi
    done
    # 3. Bundled src/ inside skill (no setup needed for read-only commands)
    local skill_dir src_dir
    skill_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
    src_dir="$skill_dir/src"
    if [[ -f "$src_dir/main.py" ]]; then echo "$src_dir"; return; fi
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
    update)
        echo "🔄 BinanceCoach update — review before applying"
        echo "   Changelog: https://clawhub.ai/skills/binance-coach"
        echo "   Source:    https://github.com/UnrealBNB/BinanceCoachAI"
        echo ""
        printf "   Proceed with update? [y/N] "
        read -r confirm
        [[ "$confirm" =~ ^[Yy]$ ]] || { echo "Update cancelled."; exit 0; }
        echo ""
        echo "🔄 Updating BinanceCoach skill..."
        # Step 1: Update skill files via ClaWHub
        if command -v clawhub &>/dev/null; then
            clawhub update binance-coach && echo "✅ Skill updated from ClaWHub"
        else
            echo "⚠️  clawhub CLI not found — skipping registry update"
        fi
        # Step 2: Copy new bundled src to workspace (preserve .env and data/)
        SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
        SRC_DIR="$SKILL_DIR/src"
        if [[ -d "$SRC_DIR" && -f "$SRC_DIR/main.py" && -d "$PROJECT" ]]; then
            # Back up .env and data/
            TMP_ENV=$(mktemp)
            cp "$PROJECT/.env" "$TMP_ENV" 2>/dev/null || true
            # Copy new source (excludes .env and data/)
            rsync -a --exclude='.env' --exclude='data/' "$SRC_DIR/" "$PROJECT/" 2>/dev/null || \
            cp -r "$SRC_DIR/." "$PROJECT/"
            # Restore .env
            [[ -f "$TMP_ENV" ]] && cp "$TMP_ENV" "$PROJECT/.env"
            rm -f "$TMP_ENV"
            echo "✅ Source updated at $PROJECT"
        else
            echo "⚠️  Bundled src not found — re-run setup to reinstall"
        fi
        # Step 3: Re-install deps in case requirements changed
        pip3 install --break-system-packages -q -r "$PROJECT/requirements.txt" 2>/dev/null || true
        echo "✅ BinanceCoach updated successfully"
        echo "   Your .env and alert data are preserved."
        ;;
    news)         run_cmd "news ${ARGS[0]:-}" ;;
    listings)     run_cmd "listings ${ARGS[0]:-}" ;;
    launchpool)   run_cmd "launchpool" ;;
    news-check)   run_cmd "news-check" ;;
    watch)
        INTERVAL="${ARGS[0]:-60}"
        echo "👁  Starting BinanceCoach watcher (interval: ${INTERVAL}s)..."
        echo "    Ctrl+C to stop, or run: bc.sh watch-stop"
        run_cmd "watch ${INTERVAL}"
        ;;
    watch-bg)
        INTERVAL="${ARGS[0]:-60}"
        LOG_FILE="$PROJECT/data/watcher.log"
        nohup bash "${BASH_SOURCE[0]}" watch "$INTERVAL" >> "$LOG_FILE" 2>&1 &
        BG_PID=$!
        echo "👁  Watcher started in background (PID: $BG_PID)"
        echo "    Logs: $LOG_FILE"
        echo "    Stop: bc.sh watch-stop"
        ;;
    watch-stop)   run_cmd "watch-stop" ;;
    watch-status) run_cmd "watch-status" ;;
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
        echo "  news [N]             Latest Binance news & announcements (default: 5)"
        echo "  listings [N]         New coin listings (default: 5)"
        echo "  launchpool           Active launchpools & HODLer airdrops"
        echo "  news-check           Check for new unseen announcements (heartbeat use)"
        echo "  watch [SECS]         Watch for new announcements, notify Telegram (default: 60s)"
        echo "  watch-bg [SECS]      Same but runs in background (nohup)"
        echo "  watch-stop           Stop the running watcher"
        echo "  watch-status         Check if watcher is running"
        echo "  coach                AI coaching summary (needs Anthropic key)"
        echo "  weekly               AI weekly brief (needs Anthropic key)"
        echo "  ask <question>       Ask Claude (needs Anthropic key)"
        echo "  models / model <id>  Claude model management"
        echo "  telegram             Start standalone Telegram bot"
        echo "  demo                 Demo mode (no API keys needed)"
        echo "  setup                First-time setup wizard"
        echo "  update               Update to latest version from ClaWHub"
        ;;
    *)
        echo "❌ Unknown command: $COMMAND"
        echo "   Run: bc.sh help"
        exit 1
        ;;
esac
