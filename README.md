# Banking Web Application

> **Stack:** Python Flask · Bootstrap 5 · SQLite
> A lightweight, session-based banking demo with login, balance view, deposit, and withdrawal.

---

## Project Structure

```
banking-app/
├── FRONTEND/
│   ├── templates/          # Jinja2 HTML templates
│   │   ├── base.html
│   │   ├── login.html
│   │   ├── dashboard.html
│   │   ├── deposit.html
│   │   ├── withdraw.html
│   │   └── errors/
│   │       ├── 404.html
│   │       └── 500.html
│   └── static/
│       ├── css/custom.css
│       └── bootstrap/      # Bootstrap 5 local bundle
│
├── BACKEND/
│   ├── app.py              # App factory & entry point
│   ├── auth.py             # Login / logout routes
│   ├── dashboard.py        # Dashboard route
│   ├── transactions.py     # Deposit & withdrawal routes
│   ├── models.py           # SQLite data access layer
│   ├── utils.py            # @login_required + validate_amount
│   └── db/
│       └── banking.db      # Auto-created on first run
│
├── tests/
│   ├── conftest.py         # Shared pytest fixtures
│   ├── test_models.py      # Unit tests — data layer
│   ├── test_utils.py       # Unit tests — validation
│   ├── test_auth.py        # Integration tests — auth
│   ├── test_dashboard.py   # Integration tests — dashboard
│   └── test_transactions.py# Integration tests — deposit/withdraw
│
├── venv/                   # Python virtual environment
├── requirements.txt        # Pinned dependencies
├── .env.example            # Environment variable template
├── .gitignore
├── README.md
├── IMPLEMENTATION_PLAN.md
└── STEP_BY_STEP_IMPLEMENTATION_GUIDE.md
```

---

## Quick Start

### 1. Prerequisites

- Python 3.10 or higher
- pip

### 2. Clone / enter the project

```bash
cd banking-app
```

### 3. Create & activate the virtual environment

```bash
# Create (already done if venv/ exists)
python -m venv venv

# Activate — Windows PowerShell
.\venv\Scripts\Activate.ps1

# Activate — Windows CMD
.\venv\Scripts\activate.bat

# Activate — macOS / Linux
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. (Optional) Configure environment variables

```bash
# Copy the example file and edit values
copy .env.example .env
```

The only required variable is `SECRET_KEY`. A development fallback is provided automatically — **replace it before any real deployment**.

### 6. Run the application

```bash
cd BACKEND
python app.py
```

Open your browser at **http://localhost:5000**

### 7. Demo Credentials

| Field    | Value         |
|----------|---------------|
| Username | `john_doe`    |
| Password | `password123` |

The demo account starts with a **$5,000.00** balance.

---

## Running Tests

From the `banking-app/` root (with venv active):

```bash
python -m pytest tests/ -v
```

For a coverage report:

```bash
pip install pytest-cov
python -m pytest tests/ -v --cov=BACKEND --cov-report=term-missing
```

---

## Features

| Feature | Route | Method |
|---|---|---|
| Login | `/login` | GET, POST |
| Dashboard + Balance | `/dashboard` | GET |
| Deposit | `/deposit` | GET, POST |
| Withdraw | `/withdraw` | GET, POST |
| Logout | `/logout` | GET |

---

## Security Notes

- Passwords are stored as **bcrypt-compatible hashes** (Werkzeug `generate_password_hash`).
- Login errors use a **generic message** to prevent username enumeration.
- All protected routes use the `@login_required` decorator.
- Session cookies are `HttpOnly` and `SameSite=Lax`.
- All SQL queries use **parameterised placeholders** (`?`) to prevent SQL injection.
- Input is stripped and validated **server-side** before any database operation.

---

## Production Checklist

- [ ] Set `SECRET_KEY` to a random 32-byte value via environment variable.
- [ ] Set `debug=False` in `app.run()` or use a WSGI server (Gunicorn / Waitress).
- [ ] Enable HTTPS via a reverse proxy (Nginx / Caddy).
- [ ] Set `SESSION_COOKIE_SECURE = True` in Flask config.
- [ ] Consider migrating to PostgreSQL for multi-user concurrency.
