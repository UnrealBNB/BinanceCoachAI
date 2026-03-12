"""
yield_optimizer.py — Stablecoin yield optimizer
Shows potential earnings from Binance Simple Earn for idle stablecoins.
"""
import logging
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

logger = logging.getLogger(__name__)
console = Console()

STABLECOINS = {"USDT", "USDC", "BUSD", "TUSD", "FDUSD", "DAI", "USD1", "USDP", "USDE"}


class YieldOptimizer:
    def __init__(self, client, portfolio):
        self.client = client
        self.portfolio = portfolio

    def _get_earn_rate(self, asset: str) -> float | None:
        """Fetch best available APR for an asset from Simple Earn."""
        # Try new Simple Earn Flexible endpoint
        try:
            resp = self.client.get_flexible_product_list(asset=asset, status="SUBSCRIBABLE")
            if resp:
                rates = [float(r.get("latestAnnualPercentageRate", 0)) for r in resp]
                if rates:
                    return max(rates) * 100
        except Exception:
            pass

        # Try the Simple Earn v2 endpoint
        try:
            resp = self.client.simple_earn_flexible_product_list(asset=asset, current=1, size=5)
            rows = resp.get("data", {}).get("rows", [])
            if rows:
                rates = [float(r.get("latestAnnualPercentageRate", 0)) for r in rows]
                return max(rates) * 100
        except Exception:
            pass

        return None

    def analyze(self) -> dict:
        try:
            balances = self.portfolio.get_balances()
        except Exception as e:
            return {"error": str(e)}

        stable_holdings = [
            b for b in balances
            if b["asset"].upper() in STABLECOINS and b["usd_value"] > 0.5
        ]

        if not stable_holdings:
            return {
                "stable_holdings": [],
                "total_idle": 0,
                "total_monthly": 0,
                "total_annual": 0,
            }

        results = []
        total_idle = sum(b["usd_value"] for b in stable_holdings)
        total_monthly = 0.0
        total_annual = 0.0

        for b in stable_holdings:
            asset = b["asset"].upper()
            usd = b["usd_value"]
            apr = self._get_earn_rate(asset)
            monthly = usd * apr / 100 / 12 if apr else None
            annual = usd * apr / 100 if apr else None
            if monthly:
                total_monthly += monthly
                total_annual += annual
            results.append({
                "asset": asset,
                "usd_value": usd,
                "apr": apr,
                "monthly_yield": monthly,
                "annual_yield": annual,
                "is_earning": apr is not None and apr > 0,
            })

        return {
            "stable_holdings": sorted(results, key=lambda x: -x["usd_value"]),
            "total_idle": total_idle,
            "total_monthly": total_monthly,
            "total_annual": total_annual,
        }

    def print_yield(self):
        result = self.analyze()
        if "error" in result:
            console.print(f"[red]Error: {result['error']}[/red]")
            return
        if not result["stable_holdings"]:
            console.print("[yellow]No stablecoin holdings found.[/yellow]")
            return

        table = Table(title="💵 Stablecoin Yield Optimizer", border_style="green")
        table.add_column("Asset",         width=8)
        table.add_column("Balance",       justify="right", width=12)
        table.add_column("APR",           justify="right", width=8)
        table.add_column("Monthly Yield", justify="right", width=15)
        table.add_column("Annual Yield",  justify="right", width=13)
        table.add_column("Status")

        idle_usd = 0.0
        for r in result["stable_holdings"]:
            if r["apr"] and r["apr"] > 0:
                status = "[green]✅ Earning[/green]"
                monthly = f"[green]+${r['monthly_yield']:,.2f}[/green]"
                annual  = f"[green]+${r['annual_yield']:,.2f}[/green]"
                apr_str = f"{r['apr']:.2f}%"
            else:
                status = "[red]💤 Idle[/red]"
                monthly = "[red]$0.00[/red]"
                annual  = "[red]$0.00[/red]"
                apr_str = "—"
                idle_usd += r["usd_value"]

            table.add_row(
                r["asset"],
                f"${r['usd_value']:,.2f}",
                apr_str,
                monthly,
                annual,
                status,
            )

        console.print(table)

        if result["total_monthly"] > 0:
            console.print(Panel(
                f"[bold green]+${result['total_monthly']:,.2f} / month[/bold green]  "
                f"([dim]+${result['total_annual']:,.2f} / year[/dim])\n"
                f"[dim]Total stablecoins: ${result['total_idle']:,.2f}[/dim]",
                title="💰 Earning Potential",
                border_style="green"
            ))
        if idle_usd > 1:
            console.print(Panel(
                f"[yellow]${idle_usd:,.2f} sitting idle — not earning anything.[/yellow]\n"
                f"[dim]Enable Binance Simple Earn (Flexible) for free passive yield.[/dim]",
                title="💤 Idle Capital",
                border_style="yellow"
            ))

    def format_yield_html(self) -> str:
        result = self.analyze()
        if "error" in result:
            return f"💵 <b>Yield Optimizer</b>\nError: {result['error']}"
        if not result["stable_holdings"]:
            return "💵 <b>Yield Optimizer</b>\nNo stablecoin holdings found."

        lines = ["💵 <b>Stablecoin Yield Optimizer</b>"]
        idle_usd = 0.0
        for r in result["stable_holdings"]:
            if r["monthly_yield"]:
                lines.append(
                    f"✅ <b>{r['asset']}</b> ${r['usd_value']:,.2f} "
                    f"@ {r['apr']:.2f}% APR → <b>+${r['monthly_yield']:,.2f}/mo</b>"
                )
            else:
                idle_usd += r["usd_value"]
                lines.append(f"💤 <b>{r['asset']}</b> ${r['usd_value']:,.2f} — idle, not earning")

        if result["total_monthly"] > 0:
            lines.append(
                f"\n💰 <b>Total: +${result['total_monthly']:,.2f}/month "
                f"(+${result['total_annual']:,.2f}/year)</b>"
            )
        if idle_usd > 1:
            lines.append(
                f"\n⚠️ ${idle_usd:,.2f} idle — consider enabling Binance Simple Earn."
            )
        return "\n".join(lines)
