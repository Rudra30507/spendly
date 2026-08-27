# Spec: Registration

## Overview
Implement the user registration flow so new visitors can create a Spendly account. This step transforms the existing `/register` stub route into a working endpoint that accepts name, email, and password, validates input, persists a new user with a hashed password, signs the user in via Flask session, and redirects them to a post-login landing area. This is the entry point for all authenticated features in the Spendly roadmap (profile, expense tracking, etc.).

## Depends on
- Step 1 — Database Setup (`users` table with `id`, `name`, `email` (UNIQUE), `password_hash`, `created_at`)

## Routes
- `GET /register` — render registration form — public
- `POST /register` — process registration, create user, log them in, redirect — public

If a logged-in user visits `/register`, redirect them away (e.g. to `/profile`) — but only if `/profile` is implemented. For this step, keep it simple: `/register` is always reachable.

## Database changes
No new schema. The `users` table created in Step 1 already supports this feature.

A small helper may be added to `database/db.py`:
- `create_user(name, email, password) -> int` — hashes the password, inserts the row, returns the new user id. Raises a domain-specific error (e.g. `ValueError("Email already registered")`) on UNIQUE constraint violation.

## Templates
- **Modify:** `templates/register.html`
  - Wire the existing form (already posts to `/register`, already has `{% if error %}` block)
  - Ensure form fields are preserved on validation error (re-populate `name` and `email`)
  - Keep all CSS classes already in place — the auth section already has form styling in `static/css/style.css`
- **No new templates** for this step. The post-registration redirect target (`/profile`) is still a stub route — do not implement it here.

## Files to change
- `app.py` — convert `/register` from a single GET stub to GET + POST handlers; add `app.secret_key` config; add `session`-based login helper
- `database/db.py` — add `create_user(name, email, password)` helper
- `templates/register.html` — preserve form values on error

## Files to create
None.

## New dependencies
No new dependencies. Use existing `werkzeug.security.generate_password_hash` and `check_password_hash`.

## Rules for implementation
- No SQLAlchemy or ORMs — use raw sqlite3 via `get_db()` from `database/db.py`
- All SQL must use `?` parameterised placeholders — never f-strings in SQL
- Passwords must be hashed with `werkzeug.security.generate_password_hash` before storage — never store plaintext
- Use the existing `error` context variable in `register.html` via `render_template(..., error="...")` — do not introduce a flash message system yet
- Flask session requires `app.secret_key`. Set a development-safe value (e.g. read from an env var with a sensible default). Do not commit a production secret.
- Email must be stored lowercased and trimmed to prevent duplicate-account issues (`"User@x.com "` vs `"user@x.com"`)
- All templates must extend `base.html`
- Use the existing CSS variables (e.g. `--accent`, `--ink`, `--danger`) — never hardcode hex values in new templates or JS
- Route functions should follow CLAUDE.md guidance: one responsibility (fetch/validate/process data, render template, redirect) — keep DB logic in `database/db.py`

## Definition of done
- [ ] `GET /register` still renders the registration form
- [ ] `POST /register` with valid name + email + password (≥ 1 char password is acceptable for dev) creates a new row in `users` with a hashed password (verify by inspecting `password_hash` — it must NOT be plaintext)
- [ ] After successful registration, the user is logged in (Flask `session` contains `user_id`) and is redirected to `/profile` (the stub for now — a 200 from `/profile`'s "Profile page — coming in Step 4" string is acceptable)
- [ ] Submitting an email that already exists shows an error message on the form (no redirect, no user created)
- [ ] Submitting an empty name or empty email shows a validation error on the form
- [ ] Submitting with whitespace-only fields is rejected
- [ ] Email is normalised (lowercased + trimmed) before insert and before the duplicate check
- [ ] On validation error, the previously entered `name` and `email` are preserved in the form
- [ ] `app.secret_key` is configured and the app starts without `RuntimeError` about the session being insecure
- [ ] The new user row appears in `users` table with `created_at` populated automatically
- [ ] No new pip packages were added to `requirements.txt`
- [ ] All queries use parameterised SQL
