"""
tests/test_dashboard.py — Integration tests for the dashboard route.
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "BACKEND"))


class TestDashboard:
    def test_unauthenticated_redirects_to_login(self, client):
        resp = client.get("/dashboard", follow_redirects=False)
        assert resp.status_code == 302
        assert "/login" in resp.headers["Location"]

    def test_authenticated_returns_200(self, auth_client):
        resp = auth_client.get("/dashboard")
        assert resp.status_code == 200

    def test_balance_displayed_on_dashboard(self, auth_client):
        resp = auth_client.get("/dashboard")
        # The seeded balance is 5000.00
        assert b"5000.00" in resp.data

    def test_username_displayed_on_dashboard(self, auth_client):
        resp = auth_client.get("/dashboard")
        assert b"John Doe" in resp.data

    def test_deposit_button_present(self, auth_client):
        resp = auth_client.get("/dashboard")
        assert b"Deposit" in resp.data

    def test_withdraw_button_present(self, auth_client):
        resp = auth_client.get("/dashboard")
        assert b"Withdraw" in resp.data
