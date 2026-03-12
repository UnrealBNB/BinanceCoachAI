"""
rebalance.py — Portfolio rebalancing engine
Compares current allocation vs user-defined target percentages.
Suggests buy/sell amounts when drift exceeds threshold.
"""
import json
import logging
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

logger = logging.getLogger(__name__)
console = Console()

TARGETS_PATH = Path(__file__).parent.parent / "data" / "targets.json"
DRIFT_THRESHOLD = 5.0  # % drift before flagging action needed


class RebalanceAdvisor:
    def __init__(self, portfolio, market):
        self.portfolio = portfolio
        self.market = market

    # ── Target management ────────────────────────────────────────────────────

    def _load_targets(self) -> dict:
        if not TARGETS_PATH.exists():
            return {}
        try:
            return json.loads(TARGETS_PATH.read_text())
        except Exception:
            return {}

    def _save_targets(self, targets: dict):
        TARGETS_PATH.parent.mkdir(parents=True, exist_ok=True)
        TARGETS_PATH.write_text(json.dumps(targets, indent=2))

    def set_targets(self, allocations: dict) -> bool:
        """Set target allocations. allocations = {"BTC": 40, "ETH": 30, ...}"""
        total = sum(allocations.values())
        if abs(total - 100) > 1:
            console.print(f"[red]❌ Targets must sum to 100% (got {total:.1f}%)[/red]")
            return False
        normalized = {k.upper(): round(v, 1) for k, v in allocations.items()}
        self._save_targets(normalized)
        console.print("[green]✅ Target allocation saved:[/green]")
        for coin, pct in sorted(normalized.items(), key=lambda x: -x[1]):
            bar = "█" * int(pct / 5)
            console.print(f"   {coin:6s} {pct:.1f}%  {bar}")
        return True

    # ── Analysis ─────────────────────────────────────────────────────────────

    def analyze(self) -> dict:
        targets = self._load_targets()
        try:
            balances = self.portfolio.get_balances()
            health = self.portfolio.calculate_health_score(balances)
            total_usd = health.get("total_usd", 0)
        except Exception as e:
            return {"error": str(e)}

        if total_usd == 0:
            return {"error": "Portfolio empty or API unavailable."}

        # Current allocation
        current = {}
        for b in balances:
            asset = b["asset"].upper()
            pct = b["usd_value"] / total_usd * 100
            current[asset] = {
                "usd_value": b["usd_value"],
                "pct": pct,
            }

        suggestions = []
        if targets:
            for coin, target_pct in targets.items():
                cur_pct = current.get(coin, {}).get("pct", 0)
                cur_usd = current.get(coin, {}).get("usd_value", 0)
                target_usd = total_usd * target_pct / 100
                drift = cur_pct - target_pct
                delta_usd = target_usd - cur_usd

                if drift > DRIFT_THRESHOLD:
                    action = "SELL"
                elif drift < -DRIFT_THRESHOLD:
                    action = "BUY"
                else:
                    action = "OK"

                suggestions.append({
                    "coin": coin,
                    "target_pct": target_pct,
                    "current_pct": round(cur_pct, 1),
                    "current_usd": cur_usd,
                    "target_usd": target_usd,
                    "drift": round(drift, 1),
                    "delta_usd": delta_usd,
                    "action": action,
                })

        return {
            "total_usd": total_usd,
            "current": current,
            "targets": targets,
            "suggestions": sorted(suggestions, key=lambda x: abs(x["drift"]), reverse=True),
            "has_targets": bool(targets),
        }

    # ── CLI output ────────────────────────────────────────────────────────────

    def print_rebalance(self):
        result = self.analyze()
        if "error" in result:
            console.print(f"[red]{result['error']}[/red]")
            return

        if not result["has_targets"]:
            console.print("[yellow]No target allocation set.[/yellow]")
            console.print("[dim]Set targets: targets-set BTC 40 ETH 30 BNB 20 ADA 10[/dim]\n")
            # Still show current allocation
            table = Table(title="📊 Current Allocation", border_style="blue")
            table.add_column("Coin")
            table.add_column("Value USD", justify="right")
            table.add_column("% of Portfolio", justify="right")
            for coin, data in sorted(result["current"].items(), key=lambda x: -x[1]["pct"])[:12]:
                table.add_row(coin, f"${data['usd_value']:,.2f}", f"{data['pct']:.1f}%")
            console.print(table)
            return

        table = Table(title="⚖️ Portfolio Rebalancing", border_style="yellow")
        table.add_column("Coin",       width=8)
        table.add_column("Target",     justify="right", width=9)
        table.add_column("Current",    justify="right", width=9)
        table.add_column("Drift",      justify="right", width=8)
        table.add_column("Action",     width=10)
        table.add_column("Amount USD", justify="right", width=12)

        needs_action = 0
        for s in result["suggestions"]:
            if s["action"] == "SELL":
                color, emoji = "red", "📉"
                needs_action += 1
            elif s["action"] == "BUY":
                color, emoji = "green", "📈"
                needs_action += 1
            else:
                color, emoji = "dim", "✓"

            drift_color = "red" if s["drift"] > 0 else "green" if s["drift"] < 0 else "dim"
            table.add_row(
                s["coin"],
                f"{s['target_pct']:.1f}%",
                f"{s['current_pct']:.1f}%",
                f"[{drift_color}]{s['drift']:+.1f}%[/{drift_color}]",
                f"[{color}]{emoji} {s['action']}[/{color}]",
                f"[{color}]${abs(s['delta_usd']):,.0f}[/{color}]" if s["action"] != "OK" else "[dim]—[/dim]",
            )

        console.print(table)
        if needs_action:
            console.print(f"\n[bold yellow]⚠️  {needs_action} coin(s) have drifted >{DRIFT_THRESHOLD}% from target[/bold yellow]")
        else:
            console.print("\n[green]✅ Portfolio is within target thresholds.[/green]")

    def print_targets(self):
        targets = self._load_targets()
        if not targets:
            console.print("[yellow]No targets set.[/yellow]")
            console.print("[dim]Example: targets-set BTC 40 ETH 30 BNB 20 ADA 10[/dim]")
            return
        table = Table(title="🎯 Target Allocation", border_style="blue")
        table.add_column("Coin")
        table.add_column("Target %", justify="right")
        table.add_column("Visual")
        for coin, pct in sorted(targets.items(), key=lambda x: -x[1]):
            bar = "█" * int(pct / 2)
            table.add_row(coin, f"{pct:.1f}%", f"[blue]{bar}[/blue]")
        console.print(table)
        console.print(f"[dim]Total: {sum(targets.values()):.1f}% | Drift threshold: {DRIFT_THRESHOLD}%[/dim]")

    # ── Telegram HTML output ─────────────────────────────────────────────────

    def format_rebalance_html(self) -> str:
        result = self.analyze()
        if "error" in result:
            return f"⚖️ <b>Rebalancing</b>\n{result['error']}"
        if not result["has_targets"]:
            return (
                "⚖️ <b>Rebalancing</b>\nNo targets set.\n"
                "Use /targetsset to define your target allocation.\n"
                "Example: <code>/targetsset BTC 40 ETH 30 BNB 20 ADA 10</code>"
            )
        lines = ["⚖️ <b>Portfolio Rebalancing</b>"]
        needs = [s for s in result["suggestions"] if s["action"] != "OK"]
        ok = [s for s in result["suggestions"] if s["action"] == "OK"]

        if needs:
            lines.append(f"⚠️ <b>{len(needs)} coin(s) need rebalancing:</b>")
            for s in needs:
                emoji = "📉" if s["action"] == "SELL" else "📈"
                lines.append(
                    f"{emoji} <b>{s['coin']}</b> {s['current_pct']}% → target {s['target_pct']}% "
                    f"(drift {s['drift']:+.1f}%) → {s['action']} <b>${abs(s['delta_usd']):,.0f}</b>"
                )
        if ok:
            lines.append(f"✅ {len(ok)} coin(s) within target range")
        return "\n".join(lines)

    def format_targets_html(self) -> str:
        targets = self._load_targets()
        if not targets:
            return (
                "🎯 <b>Target Allocation</b>\nNone set.\n"
                "Use /targetsset to define targets.\n"
                "Example: <code>/targetsset BTC 40 ETH 30 BNB 20 ADA 10</code>"
            )
        lines = ["🎯 <b>Target Allocation</b>"]
        for coin, pct in sorted(targets.items(), key=lambda x: -x[1]):
            lines.append(f"• <b>{coin}</b> — {pct:.1f}%")
        lines.append(f"<i>Rebalance triggered at >{DRIFT_THRESHOLD}% drift</i>")
        return "\n".join(lines)
