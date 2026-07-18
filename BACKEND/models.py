"""
models.py — Data Access Layer
All SQLite read/write operations are encapsulated here.
No other module should contain raw SQL.

Test isolation strategy
-----------------------
When db_path is ":memory:", every sqlite3.connect(":memory:") call creates a
brand-new, empty database.  To share a single in-memory DB across all calls
during a test, pass a live sqlite3.Connection object instead of a string via
the db_path parameter.  conftest.py does this automatically through the
flask_app fixture.
"""

import os
import sqlite3
import logging
from werkzeug.security import generate_password_hash

logger = logging.getLogger(__name__)

# Resolve the path to the database file relative to this file's location
_DB_PATH = os.path.join(os.path.dirname(__file__), "db", "banking.db")


def _connect(db_path) -> tuple:
    """
    Return (connection, owned: bool).

    - If db_path is already an open sqlite3.Connection, return it as-is
      (owned=False — caller must NOT close it).
    - Otherwise open a fresh connection to the path string.
    """
    if isinstance(db_path, sqlite3.Connection):
        return db_path, False
    path = db_path or _DB_PATH
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn, True


def get_db_connection(db_path=None) -> sqlite3.Connection:
    """
    Open and return a SQLite connection.
    Rows are returned as dict-like objects (accessible by column name).
    Accepts an optional db_path for testing (e.g. ":memory:" or a live Connection).
    """
    conn, _ = _connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path=None) -> None:
    """
    Create tables if they do not exist and seed one demo customer.
    Safe to call on every app startup — uses IF NOT EXISTS guards.
    """
    conn, owned = _connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.cursor()

        # --- users table ---
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT    NOT NULL UNIQUE,
                password TEXT    NOT NULL,
                fullname TEXT    NOT NULL
            )
        """)

        # --- accounts table ---
        cur.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    INTEGER NOT NULL UNIQUE,
                balance    REAL    NOT NULL DEFAULT 0.0,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        # --- transactions table ---
        cur.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER NOT NULL,
                type       TEXT    NOT NULL CHECK(type IN ('deposit', 'withdrawal')),
                amount     REAL    NOT NULL,
                created_at TEXT    NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (account_id) REFERENCES accounts(id)
            )
        """)

        # Seed a demo customer only if the table is empty
        existing = cur.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        if existing == 0:
            hashed_pw = generate_password_hash("password123")
            cur.execute(
                "INSERT INTO users (username, password, fullname) VALUES (?, ?, ?)",
                ("john_doe", hashed_pw, "John Doe"),
            )
            user_id = cur.lastrowid
            cur.execute(
                "INSERT INTO accounts (user_id, balance) VALUES (?, ?)",
                (user_id, 5000.00),
            )

        conn.commit()
        logger.info("Database initialised successfully.")
    except Exception as exc:
        logger.error("init_db failed: %s", exc)
        raise
    finally:
        if owned:
            conn.close()


def get_user_by_username(username: str, db_path=None):
    """
    Return the users row matching `username`, or None if not found.
    Used by the login flow.
    """
    try:
        conn, owned = _connect(db_path)
        conn.row_factory = sqlite3.Row
        user = conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
        if owned:
            conn.close()
        return user
    except Exception as exc:
        logger.error("get_user_by_username error: %s", exc)
        return None


def get_account_by_user_id(user_id: int, db_path=None):
    """
    Return the accounts row for the given user_id, or None.
    Used by dashboard and transaction flows.
    """
    try:
        conn, owned = _connect(db_path)
        conn.row_factory = sqlite3.Row
        account = conn.execute(
            "SELECT * FROM accounts WHERE user_id = ?", (user_id,)
        ).fetchone()
        if owned:
            conn.close()
        return account
    except Exception as exc:
        logger.error("get_account_by_user_id error: %s", exc)
        return None


def update_balance(account_id: int, new_balance: float, db_path=None) -> bool:
    """
    Persist a new balance for the given account_id.
    Returns True on success, False on failure.
    """
    try:
        conn, owned = _connect(db_path)
        conn.execute(
            "UPDATE accounts SET balance = ? WHERE id = ?",
            (round(new_balance, 2), account_id),
        )
        conn.commit()
        if owned:
            conn.close()
        return True
    except Exception as exc:
        logger.error("update_balance error: %s", exc)
        return False


def record_transaction(
    account_id: int, tx_type: str, amount: float, db_path=None
) -> bool:
    """
    Insert a transaction record (type must be 'deposit' or 'withdrawal').
    Returns True on success, False on failure.
    """
    try:
        conn, owned = _connect(db_path)
        conn.execute(
            "INSERT INTO transactions (account_id, type, amount) VALUES (?, ?, ?)",
            (account_id, tx_type, round(amount, 2)),
        )
        conn.commit()
        if owned:
            conn.close()
        return True
    except Exception as exc:
        logger.error("record_transaction error: %s", exc)
        return False


def get_recent_transactions(account_id: int, limit: int = 5, db_path=None):
    """
    Return the most recent `limit` transactions for display on the dashboard.
    """
    try:
        conn, owned = _connect(db_path)
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT type, amount, created_at
            FROM   transactions
            WHERE  account_id = ?
            ORDER  BY id DESC
            LIMIT  ?
            """,
            (account_id, limit),
        ).fetchall()
        if owned:
            conn.close()
        return rows
    except Exception as exc:
        logger.error("get_recent_transactions error: %s", exc)
        return []
