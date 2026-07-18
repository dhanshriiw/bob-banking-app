"""
dashboard.py — Dashboard Blueprint
Handles: GET /dashboard
"""

from flask import Blueprint, render_template, session, redirect, url_for, flash, current_app
from models import get_account_by_user_id, get_recent_transactions
from utils import login_required

dashboard_bp = Blueprint("dashboard", __name__)


def _db():
    return current_app.config.get("DB_PATH", None)


@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    """
    Render the customer dashboard with current balance and recent transactions.
    Guarded by @login_required.
    """
    user_id = session["user_id"]
    account = get_account_by_user_id(user_id, _db())

    # If account record is missing the session data is inconsistent — log out
    if account is None:
        session.clear()
        flash("Account data could not be found. Please log in again.", "danger")
        return redirect(url_for("auth.login"))

    transactions = get_recent_transactions(account["id"], limit=5, db_path=_db())

    return render_template(
        "dashboard.html",
        username=session.get("fullname", session.get("username")),
        balance=account["balance"],
        transactions=transactions,
    )
