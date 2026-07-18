"""
tests/conftest.py — Shared pytest fixtures.
Uses a persistent in-memory SQLite connection shared across the app for full isolation.
"""

import os
import sys
import sqlite3
import pytest

# Ensure the BACKEND package is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "BACKEND"))


@pytest.fixture(scope="function")
def flask_app():
    """
    Create a test application instance backed by a single in-memory SQLite
    connection that is shared for the entire duration of the test function.
    Passing a live Connection object as db_path ensures all model calls
    share the same database state (rather than each call opening a new
    ':memory:' DB that starts empty).
    """
    from app import create_app

    # Create one shared in-memory connection for this test
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    app = create_app(db_path=conn)
    app.config["TESTING"] = True

    yield app

    conn.close()


@pytest.fixture(scope="function")
def client(flask_app):
    """Provide a Flask test client."""
    return flask_app.test_client()


@pytest.fixture(scope="function")
def auth_client(client):
    """
    A test client that is pre-authenticated as the seeded demo user.
    """
    client.post(
        "/login",
        data={"username": "john_doe", "password": "password123"},
        follow_redirects=True,
    )
    return client
