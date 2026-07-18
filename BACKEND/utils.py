"""
utils.py — Shared Utilities
Contains the @login_required decorator used by all protected routes.
"""

import functools
from flask import session, redirect, url_for, flash


def login_required(f):
    """
    Decorator that guards a route to authenticated users only.
    If the session does not contain 'user_id', redirects to /login.

    Usage:
        @dashboard_bp.route('/dashboard')
        @login_required
        def dashboard():
            ...
    """
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access that page.", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function


def validate_amount(raw_value: str, max_limit: float = 1_000_000.0):
    """
    Validate and parse a transaction amount string.

    Returns (amount: float, error: str | None).
    - amount is None when validation fails.
    - error is None when validation passes.
    """
    if not raw_value or not raw_value.strip():
        return None, "Amount is required."

    try:
        amount = float(raw_value.strip())
    except ValueError:
        return None, "Amount must be a valid number."

    if amount <= 0:
        return None, "Amount must be greater than zero."

    if amount > max_limit:
        return None, f"Amount exceeds the maximum transaction limit of ${max_limit:,.2f}."

    return round(amount, 2), None
