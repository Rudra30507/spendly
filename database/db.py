import sqlite3
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash


DB_PATH = "expense_tracker.db"

CATEGORIES = [
    "Food",
    "Transport",
    "Bills",
    "Health",
    "Entertainment",
    "Shopping",
    "Other",
]


def get_db():
    """Open a connection to the SQLite database with row_factory and foreign keys enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create users and expenses tables if they don't exist."""
    conn = get_db()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id),
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL,
                description TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        conn.commit()
    finally:
        conn.close()


def seed_db():
    """Insert demo user and 8 sample expenses if database is empty."""
    conn = get_db()
    try:
        # Check if users table already has data
        cursor = conn.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] > 0:
            return  # Already seeded, avoid duplicates

        # Insert demo user
        password_hash = generate_password_hash("demo123")
        cursor = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            ("Demo User", "demo@spendly.com", password_hash)
        )
        user_id = cursor.lastrowid

        # Generate dates spread across current month
        today = datetime.now()
        start_of_month = today.replace(day=1)
        # Use a few dates across the month
        dates = [
            start_of_month + timedelta(days=2),
            start_of_month + timedelta(days=5),
            start_of_month + timedelta(days=8),
            start_of_month + timedelta(days=12),
            start_of_month + timedelta(days=15),
            start_of_month + timedelta(days=18),
            start_of_month + timedelta(days=22),
            start_of_month + timedelta(days=25),
        ]

        # Sample expenses: one per category + one extra (Food again)
        sample_expenses = [
            (1250.00, "Food", dates[0], "Lunch with colleagues"),
            (450.00, "Transport", dates[1], "Metro pass recharge"),
            (2800.00, "Bills", dates[2], "Electricity bill"),
            (950.00, "Health", dates[3], "Pharmacy - vitamins"),
            (1800.00, "Entertainment", dates[4], "Movie tickets"),
            (3200.00, "Shopping", dates[5], "New headphones"),
            (650.00, "Other", dates[6], "Gift for friend"),
            (890.00, "Food", dates[7], "Weekend dinner"),
        ]

        for amount, category, date, description in sample_expenses:
            conn.execute(
                """
                INSERT INTO expenses (user_id, amount, category, date, description)
                VALUES (?, ?, ?, ?, ?)
                """,
                (user_id, amount, category, date.strftime("%Y-%m-%d"), description)
            )

        conn.commit()
    finally:
        conn.close()


def create_user(name: str, email: str, password: str) -> int:
    """Insert a new user; return new user id. Raise ValueError on duplicate email."""
    email = email.strip().lower()
    name = name.strip()
    password_hash = generate_password_hash(password)
    conn = get_db()
    try:
        cursor = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (name, email, password_hash),
        )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        raise ValueError("Email already registered")
    finally:
        conn.close()