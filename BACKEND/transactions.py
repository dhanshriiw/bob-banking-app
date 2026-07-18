"""
transactions.py — Transactions Blueprint
Handles: GET/POST /deposit  and  GET/POST /withdraw
All routes are protected by @login_required.
"""

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
)
from flask import current_app
from models import get_account_by_user_id, update_balance, record_transaction
from utils import login_required, validate_amount

transactions_bp = Blueprint("transactions", __name__)


def _db():
    return current_app.config.get("DB_PATH", None)


# ──────────────────────────────────────────────
# Deposit
# ──────────────────────────────────────────────

@transactions_bp.route("/deposit", methods=["GET"])
@login_required
def deposit_form():
    """Render the deposit form."""
    return render_template("deposit.html")


@transactions_bp.route("/deposit", methods=["POST"])
@login_required
def deposit():
    """
    Process a deposit:
    1. Validate the amount.
    2. Fetch the account.
    3. Update the balance.
    4. Record the transaction.
    5. Redirect to dashboard with a success flash.
    """
    raw_amount = request.form.get("amount", "")
    amount, error = validate_amount(raw_amount)

    if error:
        flash(error, "danger")
        return redirect(url_for("transactions.deposit_form"))

    user_id = session["user_id"]
    account = get_account_by_user_id(user_id, _db())

    if account is None:
        flash("Something went wrong. Please try again.", "danger")
        return redirect(url_for("dashboard.dashboard"))

    new_balance = round(account["balance"] + amount, 2)

    if not update_balance(account["id"], new_balance, _db()):
        flash("Something went wrong while updating your balance. Please try again.", "danger")
        return redirect(url_for("dashboard.dashboard"))

    record_transaction(account["id"], "deposit", amount, _db())

    flash(f"Successfully deposited ${amount:,.2f}. New balance: ${new_balance:,.2f}.", "success")
    return redirect(url_for("dashboard.dashboard"))


# ──────────────────────────────────────────────
# Withdraw
# ──────────────────────────────────────────────

@transactions_bp.route("/withdraw", methods=["GET"])
@login_required
def withdraw_form():
    """Render the withdrawal form, passing the current balance for display."""
    user_id = session["user_id"]
    account = get_account_by_user_id(user_id, _db())
    balance = account["balance"] if account else 0.0
    return render_template("withdraw.html", balance=balance)


@transactions_bp.route("/withdraw", methods=["POST"])
@login_required
def withdraw():
    """
    Process a withdrawal:
    1. Validate the amount (numeric + positive).
    2. Fetch the account.
    3. Check sufficient funds.
    4. Update the balance.
    5. Record the transaction.
    6. Redirect to dashboard with a success flash.
    """
    raw_amount = request.form.get("amount", "")
    amount, error = validate_amount(raw_amount)

    if error:
        flash(error, "danger")
        return redirect(url_for("transactions.withdraw_form"))

    user_id = session["user_id"]
    account = get_account_by_user_id(user_id, _db())

    if account is None:
        flash("Something went wrong. Please try again.", "danger")
        return redirect(url_for("dashboard.dashboard"))

    # Insufficient funds check
    if amount > account["balance"]:
        flash(
            f"Insufficient funds. Your current balance is ${account['balance']:,.2f}.",
            "danger",
        )
        return redirect(url_for("transactions.withdraw_form"))

    new_balance = round(account["balance"] - amount, 2)

    if not update_balance(account["id"], new_balance, _db()):
        flash("Something went wrong while updating your balance. Please try again.", "danger")
        return redirect(url_for("dashboard.dashboard"))

    record_transaction(account["id"], "withdrawal", amount, _db())

    flash(f"Successfully withdrew ${amount:,.2f}. New balance: ${new_balance:,.2f}.", "success")
    return redirect(url_for("dashboard.dashboard"))
