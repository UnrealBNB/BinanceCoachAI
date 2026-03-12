"""
journal.py — Persistent decision journal with P&L tracking
Log DCA decisions, track performance over time, sync to OpenClaw memory.
"""
import sqlite3
import os
import logging
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

logger = logging.getLogger(__name__)
console = Console()

DB_PATH = Path(__file__).parent.parent / "data" / "journal.db"


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""CREATE TABLE IF NOT EXISTS entries (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        coin        TEXT    NOT NULL,
        action      TEXT    NOT NULL,
        price_usd   REAL    NOT NULL,
        amount_usd  REAL,
        qty         REAL,
        notes       TEXT,
        created_at  TEXT    DEFAULT CURRENT_TIMESTAMP
    )""")
    conn.commit()
    conn.close()


class DecisionJournal:
    """Log buy/sell decisions, track performance vs current prices."""

    def __init__(self, market=None):
        self.market = market
        init_db()

    def add_entry(self, coin: str, action: str, price_usd: float,
                  amount_usd: float = None, notes: str = ""):
        coin = coin.upper().replace("USDT", "").replace("USDC", "")
        action = action.upper()
        qty = (amount_usd / price_usd) if amount_usd and price_usd > 0 else None
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            "INSERT INTO entries (coin, action, price_usd, amount_usd, qty, notes) VALUES (?,?,?,?,?,?)",
            (coin, action, price_usd, amount_usd, qty, notes)
        )
        conn.commit()
        conn.close()
        console.print(f"[green]✅ Logged: {action} {coin} @ ${price_usd:,.4f}"
                      f"{f' (${amount_usd:,.2f})' if amount_usd else ''}[/green]")
        self._sync_to_memory(coin, action, price_usd, amount_usd, notes)

    def get_entries(self, coin: str = None, limit: int = 20) -> list:
        conn = sqlite3.connect(DB_PATH)
        if coin:
            rows = conn.execute(
                "SELECT * FROM entries WHERE coin=? ORDER BY created_at DESC LIMIT ?",
                (coin.upper().replace("USDT","").replace("USDC",""), limit)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM entries ORDER BY created_at DESC LIMIT ?", (limit,)
            ).fetchall()
        conn.close()
        return rows

    def get_performance(self, coin: str = None) -> list:
        """Calculate unrealised P&L for journal entries vs current prices."""
        entries = self.get_entries(coin=coin, limit=200)
        if not entries:
            return []

        # Group buys by coin
        coins = {}
        for row in entries:
            id_, c, action, price, amount, qty, notes, created_at = row
            if action != "BUY":
                continue
            if c not in coins:
                coins[c] = []
            coins[c].append({"price": price, "amount": amount or 0, "qty": qty or 0})

        results = []
        for c, trades in coins.items():
            total_invested = sum(t["amount"] for t in trades)
            total_qty = sum(t["qty"] for t in trades)
            avg_entry = total_invested / total_qty if total_qty > 0 else 0

            current_price = None
            if self.market:
                try:
                    current_price = self.market.get_price(c + "USDT")
                except Exception:
                    pass

            current_value = (total_qty * current_price) if current_price and total_qty else None
            unrealised_pnl = (current_value - total_invested) if current_value is not None else None
            unrealised_pct = (unrealised_pnl / total_invested * 100) if (unrealised_pnl is not None and total_invested > 0) else None

            results.append({
                "coin": c,
                "entries": len(trades),
                "avg_entry": avg_entry,
                "current_price": current_price,
                "total_invested": total_invested,
                "total_qty": total_qty,
                "current_value": current_value,
                "unrealised_pnl": unrealised_pnl,
                "unrealised_pct": unrealised_pct,
            })
        return sorted(results, key=lambda x: abs(x["unrealised_pnl"] or 0), reverse=True)

    def print_journal(self, coin: str = None):
        entries = self.get_entries(coin=coin)
        if not entries:
            console.print("[yellow]No journal entries yet.[/yellow]")
            console.print("[dim]Log a decision: journal-add BTC buy 70000 100 \"oversold -49% SMA200\"[/dim]")
            return
        table = Table(title="📓 Decision Journal", border_style="blue")
        table.add_column("Date", style="dim", width=12)
        table.add_column("Coin", width=8)
        table.add_column("Action", width=8)
        table.add_column("Price", justify="right", width=12)
        table.add_column("Amount $", justify="right", width=10)
        table.add_column("Notes")
        for row in entries:
            id_, coin_, action, price, amount, qty, notes, created_at = row
            color = "green" if action == "BUY" else "red"
            table.add_row(
                created_at[:10],
                coin_,
                f"[{color}]{action}[/{color}]",
                f"${price:,.4f}",
                f"${amount:,.2f}" if amount else "—",
                notes or "—"
            )
        console.print(table)

    def print_performance(self):
        results = self.get_performance()
        if not results:
            console.print("[yellow]No journal entries to analyse.[/yellow]")
            return
        table = Table(title="📈 Journal Performance vs Current Price", border_style="green")
        table.add_column("Coin", width=8)
        table.add_column("Entries", justify="right", width=8)
        table.add_column("Avg Entry", justify="right", width=12)
        table.add_column("Current", justify="right", width=12)
        table.add_column("Invested", justify="right", width=12)
        table.add_column("Unrealised P&L", justify="right", width=16)
        table.add_column("P&L %", justify="right", width=9)

        total_invested = 0
        total_pnl = 0
        for r in results:
            pnl = r["unrealised_pnl"]
            pct = r["unrealised_pct"]
            color = "green" if (pnl or 0) >= 0 else "red"
            table.add_row(
                r["coin"],
                str(r["entries"]),
                f"${r['avg_entry']:,.4f}",
                f"${r['current_price']:,.4f}" if r["current_price"] else "?",
                f"${r['total_invested']:,.2f}",
                f"[{color}]${pnl:+,.2f}[/{color}]" if pnl is not None else "?",
                f"[{color}]{pct:+.1f}%[/{color}]" if pct is not None else "?",
            )
            total_invested += r["total_invested"]
            if pnl:
                total_pnl += pnl

        console.print(table)
        color = "green" if total_pnl >= 0 else "red"
        console.print(
            f"\n[bold]Total invested:[/bold] ${total_invested:,.2f}  "
            f"[bold]Unrealised P&L:[/bold] [{color}]${total_pnl:+,.2f}[/{color}]"
        )

    def format_journal_html(self, coin: str = None) -> str:
        entries = self.get_entries(coin=coin, limit=8)
        if not entries:
            return "📓 <b>Decision Journal</b>\nNo entries yet.\nLog via: <code>bc.sh journal-add BTC buy 70000 100 \"reason\"</code>"
        lines = ["📓 <b>Decision Journal</b>"]
        for row in entries:
            id_, coin_, action, price, amount, qty, notes, created_at = row
            emoji = "🟢" if action == "BUY" else "🔴"
            amt = f" ${amount:,.0f}" if amount else ""
            lines.append(f"{emoji} <b>{coin_}</b> {action} @ ${price:,.4f}{amt} — {created_at[:10]}")
            if notes:
                lines.append(f"   <i>{notes}</i>")
        return "\n".join(lines)

    def format_performance_html(self) -> str:
        results = self.get_performance()
        if not results:
            return "📈 <b>Journal Performance</b>\nNo buy entries to analyse."
        lines = ["📈 <b>Journal Performance vs Current Price</b>"]
        for r in results:
            if r["unrealised_pnl"] is not None:
                emoji = "🟢" if r["unrealised_pnl"] >= 0 else "🔴"
                pct = f"{r['unrealised_pct']:+.1f}%"
                lines.append(
                    f"{emoji} <b>{r['coin']}</b> avg ${r['avg_entry']:,.4f} → "
                    f"${r['current_price']:,.4f} (<b>{pct}</b>  ${r['unrealised_pnl']:+,.2f})"
                )
            else:
                lines.append(f"• <b>{r['coin']}</b> avg ${r['avg_entry']:,.4f} (price unavailable)")
        return "\n".join(lines)

    def _sync_to_memory(self, coin: str, action: str, price_usd: float,
                        amount_usd: float = None, notes: str = ""):
        """Append decision to OpenClaw daily memory file."""
        workspace = None
        for candidate in [
            os.path.expanduser("~/.openclaw/workspace"),
            os.path.expanduser("~/clawd/workspace"),
        ]:
            if os.path.isdir(candidate):
                workspace = candidate
                break
        if not workspace:
            return
        try:
            memory_dir = os.path.join(workspace, "memory")
            os.makedirs(memory_dir, exist_ok=True)
            today = datetime.now().strftime("%Y-%m-%d")
            memory_file = os.path.join(memory_dir, f"{today}.md")
            amt_str = f" (${amount_usd:,.2f})" if amount_usd else ""
            note_str = f" — {notes}" if notes else ""
            entry = f"\n- BinanceCoach: {action} {coin} @ ${price_usd:,.4f}{amt_str}{note_str}\n"
            with open(memory_file, "a") as f:
                f.write(entry)
        except Exception as e:
            logger.debug(f"Memory sync failed: {e}")
