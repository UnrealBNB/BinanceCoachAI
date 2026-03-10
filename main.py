#!/usr/bin/env python3
"""
BinanceCoach — AI-Powered Trading Behavior Coach
Entry point: CLI mode and Telegram bot mode

Usage:
    python main.py                    # Interactive CLI
    python main.py --telegram         # Telegram bot mode
    python main.py --demo             # Demo mode (no API keys needed)
"""

import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from modules.i18n import t, set_lang, get_lang, AVAILABLE_LANGS

# Load env
load_dotenv()
os.makedirs("data", exist_ok=True)

# Set language from env (can be overridden at runtime with 'lang nl' command or --lang flag)
_default_lang = os.getenv("LANGUAGE", "en").lower()
try:
    set_lang(_default_lang)
except ValueError:
    set_lang("en")

console = Console()

BANNER = """
██████╗ ██╗███╗   ██╗ █████╗ ███╗   ██╗ ██████╗███████╗
██╔══██╗██║████╗  ██║██╔══██╗████╗  ██║██╔════╝██╔════╝
██████╔╝██║██╔██╗ ██║███████║██╔██╗ ██║██║     █████╗  
██╔══██╗██║██║╚██╗██║██╔══██║██║╚██╗██║██║     ██╔══╝  
██████╔╝██║██║ ╚████║██║  ██║██║ ╚████║╚██████╗███████╗
╚═════╝ ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝╚══════╝
       ██████╗ ██████╗  █████╗  ██████╗██╗  ██╗
      ██╔════╝██╔═══██╗██╔══██╗██╔════╝██║  ██║
      ██║     ██║   ██║███████║██║     ███████║
      ██║     ██║   ██║██╔══██║██║     ██╔══██║
      ╚██████╗╚██████╔╝██║  ██║╚██████╗██║  ██║
       ╚═════╝ ╚═════╝ ╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝
"""


def init_clients():
    """Initialize Binance client."""
    from binance.spot import Spot
    api_key = os.getenv("BINANCE_API_KEY", "")
    api_secret = os.getenv("BINANCE_API_SECRET", "")
    if not api_key or api_key == "your_read_only_api_key_here":
        console.print("[yellow]⚠️  No Binance API keys found. Market data only (no portfolio).[/yellow]")
        return Spot()  # Public endpoints only
    return Spot(api_key=api_key, api_secret=api_secret)


def run_demo():
    """Demo mode — shows what BinanceCoach can do without API keys."""
    from modules.market import MarketData
    from modules.dca import DCAAdvisor
    from modules.education import EducationModule

    client = init_clients()
    market = MarketData(client)
    dca = DCAAdvisor(market, monthly_budget=500, risk_profile="moderate")
    edu = EducationModule()

    console.print(Panel(
        "[bold cyan]Demo Mode[/bold cyan] — Showing BinanceCoach capabilities without API keys",
        border_style="cyan"
    ))

    # Market overview
    console.print("\n[bold]📊 Market Overview[/bold]")
    for symbol in ["BTCUSDT", "ETHUSDT", "BNBUSDT"]:
        ctx = market.get_market_context(symbol)
        fg = ctx["fear_greed"]
        console.print(
            f"  {symbol}: ${ctx['price']:,.2f} | RSI: {ctx['rsi']} ({ctx['rsi_zone']}) | "
            f"Trend: {ctx['trend']} | vs SMA200: {ctx['vs_sma200_pct']:+.1f}%"
        )

    console.print(f"\n[bold]😱 Fear & Greed: {fg['value']} — {fg['classification']}[/bold]")

    # DCA recommendations
    console.print("\n")
    dca.print_recommendations(["BTCUSDT", "ETHUSDT", "BNBUSDT"])

    # Education tip
    console.print("\n[bold]📚 Today's Lesson:[/bold]")
    edu.explain("dca")

    # Projection
    console.print("\n[bold]📈 DCA Projection (12 months, BTCUSDT):[/bold]")
    proj = dca.project_accumulation("BTCUSDT", months=12)
    console.print(
        f"  Invest ${proj['total_invested']:,.2f} → Projected: ${proj['projected_value']:,.2f} "
        f"(+{proj['roi_pct']}% if avg 5%/mo growth)"
    )
    console.print(f"  ⚠️  {proj['note']}", style="dim")


def run_cli():
    """Interactive CLI mode."""
    from modules.market import MarketData
    from modules.portfolio import Portfolio
    from modules.dca import DCAAdvisor
    from modules.alerts import AlertManager
    from modules.behavior import BehaviorCoach
    from modules.education import EducationModule
    from modules.ai_coach import AICoach

    client = init_clients()
    market = MarketData(client)
    portfolio = Portfolio(client, market)
    dca = DCAAdvisor(
        market,
        monthly_budget=float(os.getenv("DCA_BUDGET_MONTHLY", 500)),
        risk_profile=os.getenv("RISK_PROFILE", "moderate")
    )
    alert_mgr = AlertManager(market)
    behavior = BehaviorCoach(client, market)
    edu = EducationModule()

    # AI coach — optional, graceful fallback if no API key
    ai = None
    try:
        ai = AICoach()
        ai_status = f"[green]AI: {ai.model}[/green]"
    except ValueError:
        ai_status = "[yellow]AI: no key[/yellow]"

    console.print(BANNER, style="cyan")
    console.print("[bold cyan]BinanceCoach — AI Trading Behavior Coach[/bold cyan]")
    console.print(f"[dim]Lang: {get_lang().upper()} | {ai_status} | Type 'help' for commands[/dim]\n")

    while True:
        try:
            cmd = input("coach> ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[yellow]Goodbye! Trade smart. 👋[/yellow]")
            break

        if not cmd:
            continue

        parts = cmd.split()

        if parts[0] == "lang":
            if len(parts) > 1 and parts[1].lower() in AVAILABLE_LANGS:
                set_lang(parts[1].lower())
                console.print(f"[green]{t('cli.lang_switched')}[/green]")
            else:
                # Show available languages
                lang_list = "\n".join(
                    f"  {'→' if code == get_lang() else ' '} [cyan]{code}[/cyan]  {label}"
                    for code, label in AVAILABLE_LANGS.items()
                )
                console.print(t("cli.lang_list", langs=lang_list))
            continue

        if parts[0] == "help":
            console.print(t("cli.help"))

        elif parts[0] == "portfolio":
            try:
                balances = portfolio.get_balances()
                health = portfolio.calculate_health_score(balances)
                portfolio.print_portfolio_table(balances, health)
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")

        elif parts[0] == "dca":
            symbols = [s.upper() for s in parts[1:]] if len(parts) > 1 else ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
            dca.print_recommendations(symbols)

        elif parts[0] == "behavior":
            behavior.print_behavior_report()

        elif parts[0] == "alert" and len(parts) >= 4:
            symbol, condition, threshold = parts[1].upper(), parts[2], float(parts[3])
            notes = " ".join(parts[4:]) if len(parts) > 4 else ""
            alert_mgr.add_alert(symbol, condition, threshold, notes)

        elif parts[0] == "alerts":
            alert_mgr.list_alerts()

        elif parts[0] == "check-alerts":
            fired = alert_mgr.check_alerts()
            if fired:
                for f in fired:
                    console.print(Panel(f["context"], title=f"🔔 Alert: {f['symbol']}", border_style="yellow"))
            else:
                console.print("[green]No alerts triggered.[/green]")

        elif parts[0] == "learn":
            topic = parts[1] if len(parts) > 1 else None
            if topic:
                edu.explain(topic)
            else:
                edu.list_lessons()

        elif parts[0] == "market":
            symbol = parts[1].upper() if len(parts) > 1 else "BTCUSDT"
            ctx = market.get_market_context(symbol)
            fg = ctx["fear_greed"]
            console.print(f"""
[bold]{t('market.title', symbol=symbol)}[/bold]
{t('market.price')}:        ${ctx['price']:,.4f}
{t('market.rsi')}:          {ctx['rsi']} ({ctx['rsi_zone_label']})
{t('market.trend')}:        {ctx['trend']}
{t('market.sma50')}:       ${ctx['sma_50']:,.4f}
{t('market.sma200')}:      ${ctx['sma_200']:,.4f}
{t('market.ema21')}:       ${ctx['ema_21']:,.4f}
{t('market.vs_sma200')}:    {ctx['vs_sma200_pct']:+.1f}%
{t('market.fear_greed')}: {fg['value']} ({fg['classification']})
""")

        elif parts[0] == "fg":
            fg = market.get_fear_greed()
            val = fg["value"]
            emoji = "😱" if val < 25 else "😰" if val < 40 else "😐" if val < 55 else "😄" if val < 75 else "🤑"
            console.print(f"{emoji} Fear & Greed: [bold]{val}/100[/bold] — {fg['classification']}")

        elif parts[0] == "project":
            symbol = parts[1].upper() if len(parts) > 1 else "BTCUSDT"
            proj = dca.project_accumulation(symbol)
            console.print(f"""
[bold]{symbol} — 12-Month DCA Projection[/bold]
Total invested:     ${proj['total_invested']:,.2f}
Projected value:    ${proj['projected_value']:,.2f}
Projected ROI:      +{proj['roi_pct']}%
Note: {proj['note']}
""")

        # ── AI commands ───────────────────────────────────────────────────
        elif parts[0] == "models":
            if not ai:
                console.print("[yellow]⚠️  No Anthropic API key configured.[/yellow]")
            else:
                console.print("[dim]Fetching models from Anthropic API...[/dim]")
                models = ai.list_models()
                ai.print_models_table(models)

        elif parts[0] == "model":
            if not ai:
                console.print("[yellow]⚠️  No Anthropic API key configured.[/yellow]")
            elif len(parts) < 2:
                console.print(f"[yellow]Usage: model <id>  —  e.g. model claude-sonnet-4-5[/yellow]")
            else:
                ai.set_model(parts[1])
                console.print(f"[green]✅ Model switched to: {ai.model}[/green]")

        elif parts[0] == "coach":
            if not ai:
                console.print("[yellow]⚠️  No Anthropic API key configured.[/yellow]")
            else:
                console.print("[dim]🤖 Analysing portfolio + calling Claude...[/dim]")
                try:
                    balances = portfolio.get_balances()
                    health = portfolio.calculate_health_score(balances)
                    ctx = market.get_market_context("BTCUSDT")
                    bc = behavior
                    fomo = bc.calculate_fomo_score()
                    overtrade = bc.calculate_overtrading_index()
                    panic = bc.detect_panic_sells()
                    beh_data = {
                        "fomo_score": fomo["score"],
                        "fomo_label": fomo["label"],
                        "total_trades": overtrade["total_30d"],
                        "per_week": overtrade["per_week_avg"],
                        "overtrade_label": overtrade["label"],
                        "panic_count": len(panic),
                    }
                    result = ai.coaching_summary(health, ctx, beh_data)
                    ai.print_response("Coaching Summary", result, "magenta")
                except Exception as e:
                    console.print(f"[red]AI error: {e}[/red]")

        elif parts[0] == "weekly":
            if not ai:
                console.print("[yellow]⚠️  No Anthropic API key configured.[/yellow]")
            else:
                console.print("[dim]🤖 Generating weekly brief...[/dim]")
                try:
                    balances = portfolio.get_balances()
                    health = portfolio.calculate_health_score(balances)
                    ctx = market.get_market_context("BTCUSDT")
                    bc = behavior
                    fomo = bc.calculate_fomo_score()
                    overtrade = bc.calculate_overtrading_index()
                    panic = bc.detect_panic_sells()
                    beh_data = {
                        "fomo_score": fomo["score"],
                        "fomo_label": fomo["label"],
                        "total_trades": overtrade["total_30d"],
                        "per_week": overtrade["per_week_avg"],
                        "overtrade_label": overtrade["label"],
                        "panic_count": len(panic),
                    }
                    market_summary = {
                        "trend": ctx["trend"],
                        "fg_value": ctx["fear_greed"]["value"],
                        "fg_label": ctx["fear_greed"]["classification"],
                    }
                    symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
                    dca_recs = [dca.get_recommendation(s) for s in symbols]
                    result = ai.weekly_brief(health, beh_data, market_summary, dca_recs)
                    ai.print_response("Weekly Coaching Brief", result, "cyan")
                except Exception as e:
                    console.print(f"[red]AI error: {e}[/red]")

        elif parts[0] == "ask":
            if not ai:
                console.print("[yellow]⚠️  No Anthropic API key configured.[/yellow]")
            elif len(parts) < 2:
                console.print("[yellow]Usage: ask <your question>[/yellow]")
            else:
                import re as _re
                question = " ".join(parts[1:])
                console.print("[dim]🤖 Gathering portfolio context & asking Claude...[/dim]")
                try:
                    # Full context: portfolio + behavior + coin data
                    if client:
                        _balances = portfolio.get_balances()
                        _health   = portfolio.calculate_health_score(_balances)
                        _beh      = behavior.calculate_fomo_score()
                        _over     = behavior.calculate_overtrading_index()
                        _total    = _health["total_usd"] or 1
                        for _b in _balances:
                            _b["pct"] = _b["usd_value"] / _total * 100
                    else:
                        _health, _balances, _beh, _over = {}, [], {}, {}

                    fg  = market.get_fear_greed()
                    _KNOWN = {"BTC","ETH","BNB","ADA","DOGE","SHIB","FLOKI","ANKR",
                              "SOL","XRP","DOT","MATIC","AVAX","LINK","UNI","SCR"}
                    mentioned = {w.upper() for w in _re.findall(r"\b[A-Za-z]{2,10}\b", question)
                                 if w.upper() in _KNOWN} | {"BTC"}
                    coin_data = {}
                    for sym in mentioned:
                        try:
                            coin_data[sym] = market.get_market_context(sym + "USDT")
                        except Exception:
                            pass

                    context = {
                        "total_usd":       _health.get("total_usd", 0),
                        "score":           _health.get("score"),
                        "grade":           _health.get("grade"),
                        "stable_pct":      _health.get("stable_pct", 0),
                        "suggestions":     _health.get("suggestions", []),
                        "holdings":        _balances[:10],
                        "fg_value":        fg["value"],
                        "fg_label":        fg["classification"],
                        "fomo_score":      _beh.get("score", 0),
                        "overtrade_label": _over.get("label", "?"),
                        "panic_count":     0,
                        "coin_data":       coin_data,
                    }
                    result = ai.chat(question, context)
                    ai.print_response("Claude Answer", result, "green")
                except Exception as ex:
                    console.print(f"[red]AI error: {ex}[/red]")

        elif parts[0] in ("quit", "exit", "q"):
            console.print(f"[yellow]{t('general.goodbye')}[/yellow]")
            break

        else:
            console.print(f"[red]{t('general.unknown_cmd', cmd=cmd)}[/red]")


def run_telegram():
    """Start the Telegram bot."""
    from modules.market import MarketData
    from bot.telegram_bot import build_app

    client = init_clients()
    market = MarketData(client)
    app = build_app(client, market)

    console.print("[green]🤖 Starting Telegram bot...[/green]")
    app.run_polling()


def main():
    parser = argparse.ArgumentParser(description="BinanceCoach — AI Trading Behavior Coach")
    parser.add_argument("--telegram", action="store_true", help="Run as Telegram bot")
    parser.add_argument("--demo", action="store_true", help="Demo mode (no API keys)")
    parser.add_argument("--lang", choices=["en", "nl"], default=None, help="Language (en/nl)")
    args = parser.parse_args()

    if args.lang:
        set_lang(args.lang)

    if args.demo:
        run_demo()
    elif args.telegram:
        run_telegram()
    else:
        run_cli()


if __name__ == "__main__":
    main()
