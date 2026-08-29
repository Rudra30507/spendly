from datetime import datetime
from database.db import get_db

def get_user_by_id(user_id: int):
    """Return a dictionary for user_id (name, email, member_since), or None if not found."""
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT id, name, email, created_at FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
        if row is None:
            return None

        # Format created_at (YYYY-MM-DD HH:MM:SS) to "Month YYYY"
        created_at = row["created_at"]
        try:
            dt = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
            member_since = dt.strftime("%B %Y")
        except (ValueError, TypeError):
            member_since = "Unknown"

        return {
            "name": row["name"],
            "email": row["email"],
            "member_since": member_since
        }
    finally:
        conn.close()

def get_summary_stats(user_id: int):
    """Return a summary of spending for the user: total, count, and top category."""
    conn = get_db()
    try:
        # Get total spent and transaction count
        stats = conn.execute(
            "SELECT SUM(amount) as total, COUNT(*) as count FROM expenses WHERE user_id = ?",
            (user_id,),
        ).fetchone()

        total_spent = stats["total"] if stats["total"] is not None else 0
        transaction_count = stats["count"] if stats["count"] is not None else 0

        if transaction_count == 0:
            return {"total_spent": 0, "transaction_count": 0, "top_category": "—"}

        # Get top category by total spend
        top_category = conn.execute(
            """
            SELECT category FROM expenses
            WHERE user_id = ?
            GROUP BY category
            ORDER BY SUM(amount) DESC
            LIMIT 1
            """,
            (user_id,),
        ).fetchone()

        return {
            "total_spent": total_spent,
            "transaction_count": transaction_count,
            "top_category": top_category["category"] if top_category else "—"
        }
    finally:
        conn.close()

def get_category_breakdown(user_id: int):
    """Return category spending breakdown for user_id, ordered by amount DESC."""
    conn = get_db()
    try:
        total_row = conn.execute(
            "SELECT SUM(amount) as total FROM expenses WHERE user_id = ?",
            (user_id,),
        ).fetchone()
        total = total_row["total"] if total_row else None

        if total is None or total == 0:
            return []

        rows = conn.execute(
            "SELECT category, SUM(amount) as amount FROM expenses WHERE user_id = ? GROUP BY category ORDER BY amount DESC",
            (user_id,),
        ).fetchall()

        breakdown = []
        sum_pct = 0
        for row in rows:
            amount = row["amount"]
            pct = round((amount / total) * 100)
            breakdown.append({
                "name": row["category"],
                "amount": amount,
                "pct": pct
            })
            sum_pct += pct

        diff = 100 - sum_pct
        if diff != 0 and breakdown:
            breakdown[0]["pct"] += diff

        return breakdown
    finally:
        conn.close()


def get_recent_transactions(user_id: int, limit: int = 10):
    """Return a list of recent expenses for the user, newest first."""
    conn = get_db()
    try:
        rows = conn.execute(
            "SELECT date, description, category, amount FROM expenses WHERE user_id = ? ORDER BY date DESC LIMIT ?",
            (user_id, limit),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()

