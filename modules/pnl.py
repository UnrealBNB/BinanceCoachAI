"""
pnl.py — P&L calculator using Binance trade history (FIFO method)
Calculates realised + unrealised P&L, exports CSV for tax tools.
"""
import csv
import logging
from collections import deque
from datetime import datetime, timedelta
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

logger = logging.getLogger(__name__)
console = Console()

EXPORT_PATH = Path(__file__).parent.parent / "data" / "pnl_export.csv"


class PnLCalculator:
    """FIFO-based P&L calculator using Binance trade history."""

    def __init__(self, client, market, portfolio):
        self.client = client
        self.market = market
        self.portfolio = portfolio

    def _get_trades(self, symbol: str, days: int = 90) -> list:
        try:
            start_ms = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)
            trades = self.client.my_trades(symbol=symbol, limit=500, startTime=start_ms)
            return trades or []
        except Exception as e:
            logger.warning(f"Could not fetch trades for {symbol}: {e}")
            return []

    def calculate_coin_pnl(self, symbol: str) -> dict | None:
        """FIFO P&L for a single coin."""
        symbol = symbol.upper()
        if not symbol.endswith("USDT"):
            symbol += "USDT"

        trades = self._get_trades(symbol)
        if not trades:
            return None

        asset = symbol.replace("USDT", "").replace("USDC", "")
        buy_queue = deque()      # (price, qty)
        realised_pnl = 0.0
        total_bought_usd = 0.0
        total_sold_usd = 0.0
        total_commission_usd = 0.0

        for t in sorted(trades, key=lambda x: x["time"]):
            price = float(t["price"])
            qty = float(t["qty"])
            commission = float(t["commission"])
            # Estimate commission in USD (rough — commission asset varies)
            total_commission_usd += commission * price if t.get("commissionAsset") == asset else commission

            if t["isBuyer"]:
                buy_queue.append([price, qty])
                total_bought_usd += price * qty
            else:
                # Sell — FIFO cost basis
                remaining = qty
                total_sold_usd += price * qty
                while remaining > 0 and buy_queue:
                    oldest_price, oldest_qty = buy_queue[0]
                    matched = min(remaining, oldest_qty)
                    realised_pnl += matched * (price - oldest_price)
                    remaining -= matched
                    if matched >= oldest_qty:
                        buy_queue.popleft()
                    else:
                        buy_queue[0][1] -= matched

        # Unrealised from remaining holdings
        held_qty = sum(q for _, q in buy_queue)
        cost_basis = sum(p * q for p, q in buy_queue)
        avg_entry = cost_basis / held_qty if held_qty > 0 else 0

        try:
            current_price = self.market.get_price(symbol)
        except Exception:
            current_price = None

        current_value = held_qty * current_price if current_price and held_qty > 0 else None
        unrealised_pnl = (current_value - cost_basis) if current_value is not None else None
        unrealised_pct = (unrealised_pnl / cost_basis * 100) if (unrealised_pnl is not None and cost_basis > 0) else None

        return {
            "symbol": symbol,
            "asset": asset,
            "total_trades": len(trades),
            "total_bought_usd": total_bought_usd,
            "total_sold_usd": total_sold_usd,
            "realised_pnl": realised_pnl,
            "held_qty": held_qty,
            "avg_entry": avg_entry,
            "cost_basis": cost_basis,
            "current_price": current_price,
            "current_value": current_value,
            "unrealised_pnl": unrealised_pnl,
            "unrealised_pct": unrealised_pct,
            "total_commission_usd": total_commission_usd,
        }

    def calculate_portfolio_pnl(self) -> list:
        """P&L for all held non-stable coins."""
        try:
            balances = self.portfolio.get_balances()
            coins = [
                b["asset"] for b in balances
                if not b["is_stable"] and b["usd_value"] > 1
            ]
        except Exception:
            coins = ["BTC", "ETH", "BNB"]

        results = []
        for coin in coins[:12]:
            result = self.calculate_coin_pnl(coin + "USDT")
            if result:
                results.append(result)
        return sorted(results, key=lambda x: abs(x["realised_pnl"] + (x["unrealised_pnl"] or 0)), reverse=True)

    def print_pnl(self, symbol: str = None):
        if symbol:
            console.print(f"[dim]Fetching {symbol.upper()} trade history...[/dim]")
            result = self.calculate_coin_pnl(symbol)
            if not result:
                console.print(f"[red]No trade history for {symbol.upper()} in the last 90 days.[/red]")
                return
            results = [result]
        else:
            console.print("[dim]Fetching trade history from Binance (90 days)...[/dim]")
            results = self.calculate_portfolio_pnl()

        if not results:
            console.print("[yellow]No trade history found.[/yellow]")
            return

        table = Table(title="💰 P&L Summary — 90 days, FIFO", border_style="green")
        table.add_column("Coin",           width=7)
        table.add_column("Trades",         justify="right", width=7)
        table.add_column("Avg Entry",      justify="right", width=12)
        table.add_column("Current",        justify="right", width=12)
        table.add_column("Cost Basis",     justify="right", width=12)
        table.add_column("Realised P&L",   justify="right", width=14)
        table.add_column("Unrealised P&L", justify="right", width=15)
        table.add_column("Total P&L",      justify="right", width=12)

        total_realised = 0.0
        total_unrealised = 0.0

        for r in results:
            realised = r["realised_pnl"]
            unrealised = r["unrealised_pnl"] or 0
            total = realised + unrealised
            total_realised += realised
            total_unrealised += unrealised

            rc = "green" if realised >= 0 else "red"
            uc = "green" if unrealised >= 0 else "red"
            tc = "green" if total >= 0 else "red"

            table.add_row(
                r["asset"],
                str(r["total_trades"]),
                f"${r['avg_entry']:,.4f}" if r["avg_entry"] else "—",
                f"${r['current_price']:,.4f}" if r["current_price"] else "?",
                f"${r['cost_basis']:,.2f}",
                f"[{rc}]${realised:+,.2f}[/{rc}]",
                f"[{uc}]${unrealised:+,.2f}[/{uc}]" if r["unrealised_pnl"] is not None else "?",
                f"[{tc}]${total:+,.2f}[/{tc}]",
            )

        console.print(table)
        grand = total_realised + total_unrealised
        gc = "green" if grand >= 0 else "red"
        console.print(
            f"\n[bold]Realised:[/bold] [{'green' if total_realised>=0 else 'red'}]${total_realised:+,.2f}[/{'green' if total_realised>=0 else 'red'}]  "
            f"[bold]Unrealised:[/bold] [{'green' if total_unrealised>=0 else 'red'}]${total_unrealised:+,.2f}[/{'green' if total_unrealised>=0 else 'red'}]  "
            f"[bold]Grand Total:[/bold] [{gc}]${grand:+,.2f}[/{gc}]"
        )
        console.print(
            "[dim]⚠️  FIFO method, 90-day window, excludes fees. "
            "Run 'pnl-export' for a CSV you can import into Koinly / CoinTracking.[/dim]"
        )

    def export_csv(self):
        """Export P&L data to CSV for tax tools."""
        console.print("[dim]Fetching trade history...[/dim]")
        results = self.calculate_portfolio_pnl()
        if not results:
            console.print("[yellow]No data to export.[/yellow]")
            return

        EXPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(EXPORT_PATH, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "coin", "trades_90d", "avg_entry_usd", "current_price_usd",
                "held_qty", "cost_basis_usd", "current_value_usd",
                "realised_pnl_usd", "unrealised_pnl_usd", "unrealised_pct",
                "total_bought_usd", "total_sold_usd",
            ])
            for r in results:
                writer.writerow([
                    r["asset"],
                    r["total_trades"],
                    round(r["avg_entry"], 8),
                    r["current_price"] or "",
                    round(r["held_qty"], 8),
                    round(r["cost_basis"], 2),
                    round(r["current_value"], 2) if r["current_value"] else "",
                    round(r["realised_pnl"], 2),
                    round(r["unrealised_pnl"], 2) if r["unrealised_pnl"] is not None else "",
                    round(r["unrealised_pct"], 2) if r["unrealised_pct"] is not None else "",
                    round(r["total_bought_usd"], 2),
                    round(r["total_sold_usd"], 2),
                ])

        console.print(f"[green]✅ Exported to {EXPORT_PATH}[/green]")
        console.print("[dim]Import into Koinly or CoinTracking for a full tax report.[/dim]")

    def format_pnl_html(self, symbol: str = None) -> str:
        if symbol:
            results = [r for r in [self.calculate_coin_pnl(symbol)] if r]
        else:
            results = self.calculate_portfolio_pnl()

        if not results:
            return "💰 <b>P&amp;L Summary</b>\nNo trade history found (last 90 days)."

        lines = ["💰 <b>P&amp;L Summary — 90 days, FIFO</b>"]
        total_pnl = 0.0
        for r in results:
            total = r["realised_pnl"] + (r["unrealised_pnl"] or 0)
            total_pnl += total
            emoji = "🟢" if total >= 0 else "🔴"
            pct = f" ({r['unrealised_pct']:+.1f}%)" if r["unrealised_pct"] is not None else ""
            lines.append(f"{emoji} <b>{r['asset']}</b> avg ${r['avg_entry']:,.4f} → total <b>${total:+,.2f}</b>{pct}")

        grand_emoji = "🟢" if total_pnl >= 0 else "🔴"
        lines.append(f"\n{grand_emoji} <b>Grand Total: ${total_pnl:+,.2f}</b>")
        lines.append("<i>FIFO, 90-day window. Not tax advice — use /pnlexport for CSV.</i>")
        return "\n".join(lines)
