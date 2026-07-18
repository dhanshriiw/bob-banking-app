"""
tests/test_transactions.py — Integration tests for deposit and withdrawal routes.
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "BACKEND"))


class TestDepositForm:
    def test_get_deposit_page_returns_200(self, auth_client):
        resp = auth_client.get("/deposit")
        assert resp.status_code == 200
        assert b"Deposit" in resp.data

    def test_unauthenticated_redirects(self, client):
        resp = client.get("/deposit", follow_redirects=False)
        assert resp.status_code == 302
        assert "/login" in resp.headers["Location"]


class TestDeposit:
    def test_valid_deposit_increases_balance(self, auth_client):
        # Starting balance is 5000.00
        resp = auth_client.post(
            "/deposit",
            data={"amount": "500"},
            follow_redirects=True,
        )
        assert resp.status_code == 200
        assert b"5500.00" in resp.data

    def test_blank_amount_shows_error(self, auth_client):
        resp = auth_client.post(
            "/deposit",
            data={"amount": ""},
            follow_redirects=True,
        )
        assert b"required" in resp.data.lower()

    def test_zero_amount_shows_error(self, auth_client):
        resp = auth_client.post(
            "/deposit",
            data={"amount": "0"},
            follow_redirects=True,
        )
        assert b"greater than zero" in resp.data.lower()

    def test_negative_amount_shows_error(self, auth_client):
        resp = auth_client.post(
            "/deposit",
            data={"amount": "-100"},
            follow_redirects=True,
        )
        assert b"greater than zero" in resp.data.lower()

    def test_non_numeric_amount_shows_error(self, auth_client):
        resp = auth_client.post(
            "/deposit",
            data={"amount": "abc"},
            follow_redirects=True,
        )
        assert b"valid number" in resp.data.lower()

    def test_excess_amount_shows_error(self, auth_client):
        resp = auth_client.post(
            "/deposit",
            data={"amount": "9999999"},
            follow_redirects=True,
        )
        assert b"maximum" in resp.data.lower()


class TestWithdrawForm:
    def test_get_withdraw_page_returns_200(self, auth_client):
        resp = auth_client.get("/withdraw")
        assert resp.status_code == 200
        assert b"Withdraw" in resp.data

    def test_balance_shown_on_withdraw_page(self, auth_client):
        resp = auth_client.get("/withdraw")
        assert b"5000.00" in resp.data


class TestWithdraw:
    def test_valid_withdrawal_decreases_balance(self, auth_client):
        resp = auth_client.post(
            "/withdraw",
            data={"amount": "1000"},
            follow_redirects=True,
        )
        assert resp.status_code == 200
        assert b"4000.00" in resp.data

    def test_insufficient_funds_shows_error(self, auth_client):
        resp = auth_client.post(
            "/withdraw",
            data={"amount": "99999"},
            follow_redirects=True,
        )
        assert b"Insufficient funds" in resp.data

    def test_blank_amount_shows_error(self, auth_client):
        resp = auth_client.post(
            "/withdraw",
            data={"amount": ""},
            follow_redirects=True,
        )
        assert b"required" in resp.data.lower()

    def test_zero_amount_shows_error(self, auth_client):
        resp = auth_client.post(
            "/withdraw",
            data={"amount": "0"},
            follow_redirects=True,
        )
        assert b"greater than zero" in resp.data.lower()

    def test_exact_balance_withdrawal_succeeds(self, auth_client):
        resp = auth_client.post(
            "/withdraw",
            data={"amount": "5000"},
            follow_redirects=True,
        )
        assert resp.status_code == 200
        assert b"0.00" in resp.data
