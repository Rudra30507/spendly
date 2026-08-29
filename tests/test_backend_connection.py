import pytest
import uuid
from database.queries import (
    get_user_by_id,
    get_summary_stats,
    get_recent_transactions,
    get_category_breakdown
)
from database.db import init_db, seed_db, create_user

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    # Use a separate test db or ensure init_db is called
    init_db()
    seed_db()

def test_get_user_by_id():
    # Seed user should exist
    user = get_user_by_id(1)
    assert user is not None
    assert user["name"] == "Demo User"

def test_get_summary_stats():
    # Seed user (id=1) has 8 expenses totaling 11990.0, top category Shopping
    stats = get_summary_stats(1)
    assert stats["total_spent"] == 11990.0
    assert stats["transaction_count"] == 8
    assert stats["top_category"] == "Shopping"

    # User with no expenses
    unique_email = f"empty_{uuid.uuid4()}@spendly.com"
    empty_user_id = create_user("Empty User", unique_email, "password123")
    stats = get_summary_stats(empty_user_id)
    assert stats["total_spent"] == 0
    assert stats["transaction_count"] == 0
    assert stats["top_category"] == "—"

def test_get_recent_transactions():
    # User 1 has 8 expenses (from seed_db)
    transactions = get_recent_transactions(1)
    assert len(transactions) == 8
    # Check if the most recent one is first (dates are sorted in seed_db)
    assert transactions[0]["date"] > transactions[-1]["date"]
    assert "amount" in transactions[0]
    assert "category" in transactions[0]
    assert "description" in transactions[0]

    # Test user with no expenses
    unique_email = f"empty_{uuid.uuid4()}@spendly.com"
    empty_user_id = create_user("Empty User", unique_email, "password123")
    empty_transactions = get_recent_transactions(empty_user_id)
    assert empty_transactions == []

    # Test limit parameter
    limited_transactions = get_recent_transactions(1, limit=3)
    assert len(limited_transactions) == 3

def test_get_category_breakdown():
    # Seed user (id=1) has expenses.
    breakdown = get_category_breakdown(1)
    assert len(breakdown) > 0
    assert breakdown[0]["name"] == "Shopping" # 3200 is the max in seed_db

    # Check pct sum
    total_pct = sum(item["pct"] for item in breakdown)
    assert total_pct == 100

    # Check order
    amounts = [item["amount"] for item in breakdown]
    assert amounts == sorted(amounts, reverse=True)

def test_get_category_breakdown_no_expenses():
    # Create a user with no expenses
    unique_email = f"noexpense_{uuid.uuid4()}@spendly.com"
    user_id = create_user("No Expense User", unique_email, "password123")
    breakdown = get_category_breakdown(user_id)
    assert breakdown == []
