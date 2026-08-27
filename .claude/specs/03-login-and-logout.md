# Spec: Login and Logout

## Overview
Complete the authentication story started in Step 2 by wiring up the existing `GET /login` stub and the existing `GET /logout` stub into a real session-based sign-in / sign-out flow. After this step, registered users can authenticate, the navbar can reflect logged-in state, and protected routes (e.g. `/profile`, `/expenses/*`) have a session helper they can reuse in later steps. The login form is already present in `templates/login.html` — the work here is the route logic, a small `verify_user` DB helper, and a `current_user` lookup helper.

## Depends on
- Step 1 — Database Setup (`users` table with `password_hash` populated by `werkzeug.security.generate_password_hash`)
- Step 2 — Registration (sets `session["user_id"]`; we reuse that same session key here)

## Routes
- `GET /login` — render the sign-in form — public
- `POST /login` — verify credentials, set `session["user_id"]`, redirect to `/profile` — public
- `GET /logout` — clear the session and redirect to `/` — public

If a logged-in user visits `/login`, redirect them to `/profile` (the stub is fine for now).
If an unauthenticated user visits `/logout`, just clear whatever's there and redirect to `/` — no error.

## Database changes
No new schema.

Two small helpers added to `database/db.py`:
- `verify_user(email, password) -> int | None` — looks up the user by normalised email, calls `werkzeug.security.check_password_hash`. Returns the user id on success, `None` on failure (unknown email OR wrong password — the two cases must be indistinguishable to the caller to avoid email enumeration).
- `get_user_by_id(user_id) -> sqlite3.Row | None` — returns the user row (or `None`) so routes can render the user's name in templates without re-implementing the SELECT.

## Templates
- **Modify:** `templates/login.html`
  - Pre-fill the `email` input with the submitted value on validation failure (same pattern as `register.html`)
  - Keep all existing CSS classes (`auth-error`, `form-input`, `btn-submit`, `auth-switch`)
- **Modify:** `templates/base.html`
  - Update the navbar to show different links depending on `current_user.is_authenticated`:
    - Logged out: "Sign in" + "Get started" (existing behaviour)
    - Logged in: greeting (e.g. `Hi, {{ current_user.name }}`) + "Profile" link + "Sign out" link
  - This requires a `current_user` context — implement via a small `@app.context_processor` in `app.py` that returns `current_user` (the row from `get_user_by_id(session.get("user_id"))`, or `None`).

No new templates.

## Files to change
- `app.py` — convert `/login` from a single GET stub to GET + POST; convert `/logout` from a string stub to a real handler that clears `session`; add `@app.context_processor` registering `current_user`
- `database/db.py` — add `verify_user(email, password)` and `get_user_by_id(user_id)` helpers
- `templates/login.html` — preserve submitted email on error
- `templates/base.html` — render logged-in vs logged-out navbar variants

## Files to create
None.

## New dependencies
No new dependencies. Use existing `werkzeug.security.check_password_hash` (already installed in Step 1).

## Rules for implementation
- No SQLAlchemy or ORMs — raw sqlite3 via `get_db()` only
- All SQL must use `?` parameterised placeholders — never f-strings in SQL
- Password verification must use `werkzeug.security.check_password_hash` — never compare hashes or plaintext yourself
- `verify_user` MUST return the same `None` for both "unknown email" and "wrong password" — do not leak which one failed
- Normalise email the same way `create_user` does: `email.strip().lower()` before the SELECT
- The login rate-limit story is out of scope for this step — don't add brute-force protection, captchas, or account lockouts
- Use Flask's `session` (already configured in Step 2 with `app.secret_key`) — never roll your own cookie auth
- Use `url_for()` for every internal link, including the navbar — never hardcode paths
- All templates extend `base.html` (already true)
- Use existing CSS variables (`--accent`, `--ink`, `--danger`) — never hardcode hex values
- Route functions: one responsibility (fetch/validate/process, render, redirect) — keep DB logic in `database/db.py`
- Logout should call `session.clear()` and then `redirect(url_for("landing"))`

## Definition of done
- [ ] `GET /login` renders the sign-in form (200)
- [ ] `POST /login` with valid email + password sets `session["user_id"]` and redirects to `/profile` (302)
- [ ] `POST /login` with an unknown email shows the same generic error as a wrong password (no enumeration)
- [ ] `POST /login` with a wrong password shows a generic "Invalid email or password" message
- [ ] `POST /login` with empty email or empty password is rejected with a validation error
- [ ] On validation error, the submitted email is preserved in the form (password is NOT preserved)
- [ ] After a successful login, the navbar shows the user's name + "Profile" + "Sign out" (instead of "Sign in" + "Get started")
- [ ] `GET /logout` clears the session cookie and redirects to `/` (302)
- [ ] After logout, the navbar reverts to the logged-out variant
- [ ] Visiting `/login` while already logged in redirects to `/profile`
- [ ] `app.context_processor` exposes `current_user` (a row-like object or `None`) to every template
- [ ] `current_user.is_authenticated` works in templates (True when a row is loaded, False when None — easiest is a `SimpleNamespace` wrapper or a Jinja `default(None, False)` pattern in the template)
- [ ] No new pip packages — `requirements.txt` is unchanged
- [ ] All SQL queries use `?` placeholders
- [ ] Passwords are verified with `check_password_hash` — never compared as strings or bytes directly
