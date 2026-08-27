This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
# CLAUDE.md

Project overview
Spendly is a lightweight personal expense tracker built with Flask and SQLite.

Architecture
spendly/
├── app.py              # All routes — single file, no blueprints
├── database/
│   └── db.py           # SQLite helpers: get_db(), init_db(), seed_db()
├── templates/
│   ├── base.html       # Shared layout — all templates must extend this
│   └── *.html          # One template per page
├── static/
│   ├── css/
│   │   ├── style.css       # Global styles
│   │   └── landing.css     # Landing-page-only styles
│   └── js/
│       └── main.js         # Vanilla JS only
└── requirements.txt
Where things belong:

New routes → app.py only, no blueprints
DB logic → database/db.py only, never inline in routes
New pages → new .html file extending base.html
Page-specific styles → new .css file, not inline <style> tags
Code style
Python: PEP 8, snake_case for all variables and functions
Templates: Jinja2 with url_for() for every internal link — never hardcode URLs
Route functions: one responsibility only — fetch data, render template, done
DB queries: always use parameterized queries (? placeholders) — never f-strings in SQL
Error handling: use abort() for HTTP errors, not bare return "error string"
Tech constraints
Flask only — no FastAPI, no Django, no other web frameworks
SQLite only — no PostgreSQL, no SQLAlchemy ORM, no external DB
Vanilla JS only — no React, no jQuery, no npm packages
No new pip packages — work within requirements.txt as-is unless explicitly told otherwise
Python 3.10+ assumed — f-strings and match statements are fine
Subagent Policy
Always use a builtin explore subagent for codebase exploration before implementing any new feature
Always use a subagent to verify test results after any implementation
When asked to plan, delegate codebase research to a subagent before presenting the plan
always use a builtin plan subagent in plan mode
Commands
# Setup
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run dev server (port 5001)
python app.py

# Run all tests
pytest

# Run a specific test file
pytest tests/test_foo.py

# Run a specific test by name
pytest -k "test_name"

# Run tests with output visible
pytest -s
Implemented vs stub routes
Route	Status
GET /	Implemented — renders landing.html
GET /register	Implemented — renders register.html
GET /login	Implemented — renders login.html
GET /logout	Stub — Step 3
GET /profile	Stub — Step 4
GET /expenses/add	Stub — Step 7
GET /expenses/<id>/edit	Stub — Step 8
GET /expenses/<id>/delete	Stub — Step 9
Do not implement a stub route unless the active task explicitly targets that step.

Warnings and things to avoid
Never use raw string returns for stub routes once a step is implemented — always render a template
Never hardcode URLs in templates — always use url_for()
Never put DB logic in route functions — it belongs in database/db.py
Never install new packages mid-feature without flagging it — keep requirements.txt in sync
Never use JS frameworks — the frontend is intentionally vanilla
database/db.py is currently empty — do not assume helpers exist until the step that implements them
FK enforcement is manual — SQLite foreign keys are off by default; get_db() must run PRAGMA foreign_keys = ON on every connection
The app runs on port 5001, not the Flask default 5000 — don't change this



## Project

**Spendly** — a Flask personal expense tracking web app. Designed as a step-by-step learning project (database setup, auth, expenses, profile, etc.). Built with Flask + Jinja2 + vanilla CSS/JS. Currency is INR (₹).

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run dev server (debug mode, port 5001)
python app.py

# Run tests (pytest with pytest-flask)
pytest
```

There is no build step, linter, or formatter configured. The app runs directly via `app.run(debug=True, port=5001)`.

## Architecture

### Entry point — `app.py`
Flask app with routes grouped into two sections:
- **Implemented routes** (line ~10): `/`, `/register`, `/login`, `/terms`, `/privacy` — all currently return `render_template(...)` with no form processing yet.
- **Placeholder routes** (line ~39): `/logout`, `/profile`, `/expenses/add`, `/expenses/<id>/edit`, `/expenses/<id>/delete` — return string stubs (`"… — coming in Step N"`). These are the next steps in the curriculum and the natural extension points.

### Database — `database/db.py`
**Currently empty** — contains only docstring comments listing what students will write:
- `get_db()` — returns SQLite connection with `row_factory` and foreign keys enabled
- `init_db()` — creates all tables via `CREATE TABLE IF NOT EXISTS`
- `seed_db()` — inserts sample data for development

The SQLite file `expense_tracker.db` is gitignored. There is no `models/` or `schema.sql` yet.

### Templates — `templates/`
All extend `base.html`, which defines blocks: `title`, `head`, `content`, `scripts`.

- **`base.html`** — Navbar (Spendly brand, Sign in, Get started CTA), `{% block content %}`, dark footer with Terms/Privacy links, loads `static/js/main.js` + `{% block scripts %}`.
- **`landing.html`** — Hero (badge, headline with green accent line, subtitle, two CTAs), preview dashboard card (3 stat tiles + 3 category bars), features section, CTA section. Contains the **video modal** at the end with inline `<script>` in `{% block scripts %}` that opens on `#demo-trigger` click, closes via close button / overlay click / Escape, and stops the YouTube iframe by clearing+restoring `src`.
- **`register.html` / `login.html`** — Auth forms (currently GET-only stubs; POST handlers and `error` flash context not yet wired).
- **`terms.html` / `privacy.html`** — Legal pages styled via `.legal-page` / `.legal-inner` / `.legal-content` classes.

### Styling — `static/css/style.css`
Single monolithic CSS file (~830 lines) organized into commented sections:
1. **Variables** (`:root`) — `--ink`, `--paper`, `--accent: #1a472a` (deep green), `--accent-2: #c17f24` (warm orange), plus semantic colors (`--success`, `--warning`, `--info`, `--purple`, `--danger`). Two font stacks: `--font-display` (DM Serif Display) for headings, `--font-body` (DM Sans).
2. **Reset** — minimal box-sizing/normalize.
3. **Navbar**, **Main**, **Hero**, **Preview card**, **Buttons**, **Features**, **CTA**, **Auth**, **Footer**, **Legal pages**, **Video Modal**, **Responsive** (`@media (max-width: 900px)` and `600px`).

When adding components, reuse the existing CSS variables (`--border`, `--radius-md`, `--ink-muted`, etc.) rather than introducing new colors.

### Scripts — `static/js/main.js`
Currently a placeholder comment. **Per-feature JS lives inline in template `{% block scripts %}` blocks** (see the modal in `landing.html`). Follow this convention when adding new interactive components.

## Conventions

- **Routes use `url_for()`** in templates, never hardcoded paths.
- **Forms POST to the literal URL** (e.g. `action="/register"`), not `url_for` — preserve this for now.
- **Errors are rendered via a `{% if error %}<div class="auth-error">{{ error }}</div>{% endif %}` pattern** in auth templates; the `error` context variable is not yet passed from routes.
- **No JS framework, no CSS framework** — vanilla only. Modal interactions, focus management, and YouTube embed controls are hand-written.
- **DM Serif Display + DM Sans** Google Fonts are loaded in `base.html` — don't add other font families.

## Allowed permissions (`.claude/settings.local.json`)
- `WebSearch`
- `Bash(curl -s http://localhost:5001/)` — for hitting the local dev server.