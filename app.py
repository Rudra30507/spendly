import os
from types import SimpleNamespace
from flask import Flask, render_template, request, redirect, session, url_for
from database.db import get_db, init_db, seed_db, create_user, verify_user, get_user_by_id

app = Flask(__name__)
app.secret_key = os.environ.get("SPENDLY_SECRET_KEY", "dev-secret-change-me")


def _current_user():
    """Return a user object with .is_authenticated, .id, .name, .email — or None."""
    uid = session.get("user_id")
    if uid is None:
        return None
    row = get_user_by_id(uid)
    if row is None:
        return None
    return SimpleNamespace(
        is_authenticated=True,
        id=row["id"],
        name=row["name"],
        email=row["email"],
    )


app.context_processor(lambda: {"current_user": _current_user()})


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    # Already signed in? Bounce to /profile.
    if session.get("user_id"):
        return redirect(url_for("profile"))

    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        email = (request.form.get("email") or "").strip()
        password = request.form.get("password") or ""

        # Validation
        if not name:
            return render_template("register.html",
                                   error="Name is required.",
                                   name=name, email=email), 400
        if not email:
            return render_template("register.html",
                                   error="Email is required.",
                                   name=name, email=email), 400
        if not password:
            return render_template("register.html",
                                   error="Password is required.",
                                   name=name, email=email), 400

        # Create user
        try:
            user_id = create_user(name, email, password)
        except ValueError as e:
            return render_template("register.html",
                                   error=str(e),
                                   name=name, email=email), 400

        # Log in via session
        session["user_id"] = user_id
        return redirect(url_for("profile"))

    # GET — render empty form
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    # Already signed in? Bounce to /profile.
    if session.get("user_id"):
        return redirect(url_for("profile"))

    if request.method == "POST":
        email = (request.form.get("email") or "").strip()
        password = request.form.get("password") or ""

        if not email:
            return render_template("login.html",
                                   error="Email is required.",
                                   email=email), 400
        if not password:
            return render_template("login.html",
                                   error="Password is required.",
                                   email=email), 400

        user_id = verify_user(email, password)
        if user_id is None:
            return render_template("login.html",
                                   error="Invalid email or password.",
                                   email=email), 400

        session["user_id"] = user_id
        return redirect(url_for("profile"))

    return render_template("login.html")


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))


@app.route("/profile")
def profile():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))

    # Hardcoded user data (matching seed user)
    user = {
        "name": "Demo User",
        "email": "demo@spendly.com",
        "member_since": "January 2026"
    }

    # Hardcoded summary stats
    stats = {
        "total_spent": 11990.00,
        "transaction_count": 8,
        "top_category": "Shopping"
    }

    # Hardcoded recent transactions (newest first)
    transactions = [
        {"date": "2026-01-25", "description": "Weekend dinner", "category": "Food", "amount": 890.00},
        {"date": "2026-01-22", "description": "Gift for friend", "category": "Other", "amount": 650.00},
        {"date": "2026-01-18", "description": "New headphones", "category": "Shopping", "amount": 3200.00},
        {"date": "2026-01-15", "description": "Movie tickets", "category": "Entertainment", "amount": 1800.00},
        {"date": "2026-01-12", "description": "Pharmacy - vitamins", "category": "Health", "amount": 950.00},
        {"date": "2026-01-08", "description": "Electricity bill", "category": "Bills", "amount": 2800.00},
        {"date": "2026-01-05", "description": "Metro pass recharge", "category": "Transport", "amount": 450.00},
        {"date": "2026-01-02", "description": "Lunch with colleagues", "category": "Food", "amount": 1250.00},
    ]

    # Hardcoded category breakdown (pct sums to 100)
    categories = [
        {"name": "Shopping", "amount": 3200.00, "pct": 27},
        {"name": "Bills", "amount": 2800.00, "pct": 23},
        {"name": "Food", "amount": 2140.00, "pct": 18},
        {"name": "Entertainment", "amount": 1800.00, "pct": 15},
        {"name": "Health", "amount": 950.00, "pct": 8},
        {"name": "Transport", "amount": 450.00, "pct": 4},
        {"name": "Other", "amount": 650.00, "pct": 5},
    ]

    return render_template(
        "profile.html",
        user=user,
        stats=stats,
        transactions=transactions,
        categories=categories
    )


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    with app.app_context():
        init_db()
        seed_db()
    app.run(debug=True, port=5001)
