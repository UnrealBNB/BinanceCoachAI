"""
behavior.py — Behavioral bias detector & coaching engine
Analyzes trade history for emotional trading patterns
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from binance.spot import Spot
from rich.console import Console
from rich.panel import Panel
from modules.i18n import t

console = Console()

DB_PATH = str(Path(__file__).parent.parent / "data" / "behavior.db")


def init_db():
    """Initialize the behavior tracking database."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            side TEXT,
            price REAL,
            qty REAL,
            time INTEGER,
            order_id TEXT UNIQUE
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS streaks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            streak_type TEXT,
            start_date TEXT,
            count INTEGER,
            last_updated TEXT
        )
    """)
    conn.commit()
    conn.close()


class BehaviorCoach:
    """Detects emotional trading patterns and coaches users."""

    def __init__(self, client: Spot, market):
        self.client = client
        self.market = market
        init_db()

    def sync_trades(self, symbols: list[str], days: int = 30):
        """Pull recent trade history from Binance into local DB."""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        cutoff = int((datetime.utcnow() - timedelta(days=days)).timestamp() * 1000)

        for symbol in symbols:
            try:
                trades = self.client.my_trades(symbol=symbol, limit=500)
                for trade in trades:
                    if trade["time"] < cutoff:
                        continue
                    c.execute("""
                        INSERT OR IGNORE INTO trades (symbol, side, price, qty, time, order_id)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        trade["symbol"],
                        "BUY" if trade["isBuyer"] else "SELL",
                        float(trade["price"]),
                        float(trade["qty"]),
                        trade["time"],
                        trade["id"]
                    ))
            except Exception as e:
                pass  # Skip symbols with no history

        conn.commit()
        conn.close()

    def calculate_fomo_score(self) -> dict:
        """
        FOMO Score: Did you buy during Fear & Greed extremes (>75 greed)?
        Higher score = more FOMO buying detected.
        """
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        # Get buy trades from last 30 days
        cutoff = int((datetime.utcnow() - timedelta(days=30)).timestamp() * 1000)
        c.execute("SELECT time, price FROM trades WHERE side='BUY' AND time > ?", (cutoff,))
        buys = c.fetchall()
        conn.close()

        if not buys:
            return {"score": 0, "label": "N/A", "detail": "No trades in last 30 days."}

        # Current F&G
        fg = self.market.get_fear_greed()
        fg_val = fg["value"]

        # Simple heuristic: if you traded a lot when F&G was high, that's FOMO
        # We can't get historical F&G per trade easily without paid API
        # So we approximate by clustering: rapid buys near local highs
        fomo_score = 0
        if fg_val > 75:
            fomo_score += 30  # Currently buying in extreme greed
        elif fg_val > 60:
            fomo_score += 15

        # Overbuying: many buys in short windows (buying the hype)
        buy_times = sorted([row[0] for row in buys])
        rapid_buys = 0
        for i in range(1, len(buy_times)):
            if buy_times[i] - buy_times[i-1] < 3600_000:  # within 1 hour
                rapid_buys += 1
        fomo_score += min(30, rapid_buys * 5)

        label = t("behavior.fomo.label.low") if fomo_score < 20 else t("behavior.fomo.label.med") if fomo_score < 50 else t("behavior.fomo.label.high")
        return {
            "score": fomo_score,
            "label": label,
            "current_fg": fg_val,
            "current_fg_label": fg["classification"],
            "rapid_buy_clusters": rapid_buys,
        }

    def detect_panic_sells(self) -> list[dict]:
        """
        Detect sells that happened near local price lows
        (sold low, then price recovered significantly).
        """
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        cutoff = int((datetime.utcnow() - timedelta(days=30)).timestamp() * 1000)
        c.execute("SELECT symbol, price, time FROM trades WHERE side='SELL' AND time > ?", (cutoff,))
        sells = c.fetchall()
        conn.close()

        panic_sells = []
        for symbol, sell_price, sell_time in sells:
            try:
                current = self.market.get_price(symbol)
                recovery = ((current - sell_price) / sell_price) * 100
                if recovery > 15:  # Price is 15%+ higher than where you sold
                    panic_sells.append({
                        "symbol": symbol,
                        "sell_price": sell_price,
                        "current_price": current,
                        "recovery_pct": round(recovery, 1),
                        "sold_at": datetime.fromtimestamp(sell_time / 1000).strftime("%Y-%m-%d"),
                    })
            except Exception:
                pass
        return panic_sells

    def calculate_overtrading_index(self) -> dict:
        """Count trades per week — high frequency often leads to worse outcomes."""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        cutoff = int((datetime.utcnow() - timedelta(days=30)).timestamp() * 1000)
        c.execute("SELECT COUNT(*) FROM trades WHERE time > ?", (cutoff,))
        count = c.fetchone()[0]
        conn.close()

        per_week = count / 4.3
        label = t("behavior.overtrade.label.healthy") if per_week < 5 else t("behavior.overtrade.label.mod") if per_week < 15 else t("behavior.overtrade.label.high") if per_week < 30 else t("behavior.overtrade.label.over")
        tip = ""
        if per_week > 15:
            tip = t("behavior.overtrade.tip")

        return {
            "total_30d": count,
            "per_week_avg": round(per_week, 1),
            "label": label,
            "tip": tip,
        }

    def get_streaks(self) -> dict:
        """Get gamified streak data — days without panic selling, etc."""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT streak_type, count, last_updated FROM streaks")
        rows = c.fetchall()
        conn.close()

        streaks = {}
        for streak_type, count, last_updated in rows:
            streaks[streak_type] = {"count": count, "last_updated": last_updated}

        # Default streaks
        if "no_panic_sell" not in streaks:
            streaks["no_panic_sell"] = {"count": 0, "last_updated": None}
        if "dca_consistency" not in streaks:
            streaks["dca_consistency"] = {"count": 0, "last_updated": None}

        return streaks

    def print_behavior_report(self):
        """Print a rich behavior analysis panel."""
        fomo = self.calculate_fomo_score()
        overtrade = self.calculate_overtrading_index()
        panic = self.detect_panic_sells()
        streaks = self.get_streaks()

        report = f"""
[bold]🧠 {t('behavior.title')}[/bold]

[yellow]{t('behavior.fomo')}:[/yellow] {fomo['score']}/100 — {fomo['label']}
  {t('behavior.fomo.fg')}: {fomo.get('current_fg', '?')} ({fomo.get('current_fg_label', '?')})
  {t('behavior.fomo.rapid')}: {fomo.get('rapid_buy_clusters', 0)}

[yellow]{t('behavior.overtrade')}:[/yellow] {overtrade['label']}
  {t('behavior.overtrade.total')}: {overtrade['total_30d']}
  {t('behavior.overtrade.week')}: {overtrade['per_week_avg']}
  {overtrade.get('tip', '')}

[yellow]{t('behavior.panic')}:[/yellow]
"""
        if panic:
            for p in panic[:3]:
                sell_fmt = f"{p['sell_price']:.4f}"
                now_fmt = f"{p['current_price']:.4f}"
                report += f"  {t('behavior.panic.found', symbol=p['symbol'], sell=sell_fmt, date=p['sold_at'], now=now_fmt, pct=p['recovery_pct'])}\n"
        else:
            report += f"  {t('behavior.panic.none')}\n"

        report += f"""
[yellow]{t('behavior.streaks')}:[/yellow]
  {t('behavior.streak.no_panic')}: {t('behavior.streak.days', n=streaks['no_panic_sell']['count'])}
  {t('behavior.streak.dca')}: {t('behavior.streak.weeks', n=streaks['dca_consistency']['count'])}
"""
        console.print(Panel(report, title=f"[bold magenta]BinanceCoach — {t('behavior.title')}[/bold magenta]", border_style="magenta"))
