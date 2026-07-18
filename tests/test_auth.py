"""
tests/test_auth.py — Integration tests for authentication routes.
Uses the Flask test client with an in-memory database.
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "BACKEND"))


class TestLoginPage:
    def test_get_login_renders_200(self, client):
        resp = client.get("/login")
        assert resp.status_code == 200
        assert b"Sign In" in resp.data

    def test_authenticated_user_is_redirected_from_login(self, auth_client):
        resp = auth_client.get("/login", follow_redirects=False)
        assert resp.status_code == 302
        assert "/dashboard" in resp.headers["Location"]


class TestLoginPost:
    def test_valid_credentials_redirect_to_dashboard(self, client):
        resp = client.post(
            "/login",
            data={"username": "john_doe", "password": "password123"},
            follow_redirects=False,
        )
        assert resp.status_code == 302
        assert "/dashboard" in resp.headers["Location"]

    def test_blank_username_stays_on_login(self, client):
        resp = client.post(
            "/login",
            data={"username": "", "password": "password123"},
            follow_redirects=True,
        )
        assert resp.status_code == 200
        assert b"Username is required" in resp.data

    def test_blank_password_stays_on_login(self, client):
        resp = client.post(
            "/login",
            data={"username": "john_doe", "password": ""},
            follow_redirects=True,
        )
        assert resp.status_code == 200
        assert b"Password is required" in resp.data

    def test_wrong_password_shows_generic_error(self, client):
        resp = client.post(
            "/login",
            data={"username": "john_doe", "password": "wrongpassword"},
            follow_redirects=True,
        )
        assert resp.status_code == 200
        assert b"Invalid username or password" in resp.data

    def test_unknown_username_shows_generic_error(self, client):
        resp = client.post(
            "/login",
            data={"username": "nobody", "password": "irrelevant"},
            follow_redirects=True,
        )
        assert resp.status_code == 200
        assert b"Invalid username or password" in resp.data

    def test_no_session_created_on_bad_login(self, client):
        with client:
            client.post(
                "/login",
                data={"username": "john_doe", "password": "bad"},
                follow_redirects=True,
            )
            from flask import session
            assert "user_id" not in session


class TestLogout:
    def test_logout_redirects_to_login(self, auth_client):
        resp = auth_client.get("/logout", follow_redirects=False)
        assert resp.status_code == 302
        assert "/login" in resp.headers["Location"]

    def test_session_cleared_after_logout(self, auth_client):
        with auth_client:
            auth_client.get("/logout")
            from flask import session
            assert "user_id" not in session
