"""
tests/test_models.py — Unit tests for models.py (data access layer).
All tests use a shared in-memory SQLite connection for correct isolation.
"""

import os
import sys
import sqlite3
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "BACKEND"))

from models import (
    init_db,
    get_user_by_username,
    get_account_by_user_id,
    update_balance,
    record_transaction,
    get_recent_transactions,
)
from werkzeug.security import check_password_hash


@pytest.fixture()
def db():
    """
    A fresh, seeded in-memory SQLite connection for each test.
    Passing the live Connection to every model call ensures they all
    share the same database state.
    """
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    init_db(conn)
    yield conn
    conn.close()


# ── get_user_by_username ──────────────────────────────────────────────

class TestGetUserByUsername:
    def test_returns_user_for_valid_username(self, db):
        user = get_user_by_username("john_doe", db)
        assert user is not None
        assert user["username"] == "john_doe"
        assert user["fullname"] == "John Doe"

    def test_returns_none_for_unknown_username(self, db):
        user = get_user_by_username("nobody", db)
        assert user is None

    def test_password_is_hashed(self, db):
        user = get_user_by_username("john_doe", db)
        # The stored value must be a hash — not the plain text
        assert user["password"] != "password123"
        assert check_password_hash(user["password"], "password123")


# ── get_account_by_user_id ────────────────────────────────────────────

class TestGetAccountByUserId:
    def test_returns_account_for_seeded_user(self, db):
        user = get_user_by_username("john_doe", db)
        account = get_account_by_user_id(user["id"], db)
        assert account is not None
        assert account["balance"] == 5000.00

    def test_returns_none_for_nonexistent_user_id(self, db):
        account = get_account_by_user_id(99999, db)
        assert account is None


# ── update_balance ────────────────────────────────────────────────────

class TestUpdateBalance:
    def test_balance_is_updated(self, db):
        user = get_user_by_username("john_doe", db)
        account = get_account_by_user_id(user["id"], db)

        success = update_balance(account["id"], 7500.00, db)
        assert success is True

        updated = get_account_by_user_id(user["id"], db)
        assert updated["balance"] == 7500.00

    def test_balance_rounds_to_two_decimal_places(self, db):
        user = get_user_by_username("john_doe", db)
        account = get_account_by_user_id(user["id"], db)

        update_balance(account["id"], 1234.5678, db)
        updated = get_account_by_user_id(user["id"], db)
        assert updated["balance"] == 1234.57


# ── record_transaction ────────────────────────────────────────────────

class TestRecordTransaction:
    def test_deposit_is_recorded(self, db):
        user = get_user_by_username("john_doe", db)
        account = get_account_by_user_id(user["id"], db)

        success = record_transaction(account["id"], "deposit", 100.00, db)
        assert success is True

        txs = get_recent_transactions(account["id"], limit=1, db_path=db)
        assert len(txs) == 1
        assert txs[0]["type"] == "deposit"
        assert txs[0]["amount"] == 100.00

    def test_withdrawal_is_recorded(self, db):
        user = get_user_by_username("john_doe", db)
        account = get_account_by_user_id(user["id"], db)

        record_transaction(account["id"], "withdrawal", 50.00, db)
        txs = get_recent_transactions(account["id"], limit=1, db_path=db)
        assert txs[0]["type"] == "withdrawal"
        assert txs[0]["amount"] == 50.00

    def test_recent_transactions_order(self, db):
        user = get_user_by_username("john_doe", db)
        account = get_account_by_user_id(user["id"], db)

        record_transaction(account["id"], "deposit",    200.00, db)
        record_transaction(account["id"], "withdrawal", 300.00, db)

        txs = get_recent_transactions(account["id"], limit=5, db_path=db)
        # Most recent first
        assert txs[0]["type"] == "withdrawal"
        assert txs[1]["type"] == "deposit"
