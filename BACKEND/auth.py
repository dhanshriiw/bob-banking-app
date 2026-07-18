"""
auth.py — Authentication Blueprint
Handles: GET /login, POST /login, GET /logout
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
from werkzeug.security import check_password_hash
from flask import current_app
from models import get_user_by_username

auth_bp = Blueprint("auth", __name__)


def _db():
    """Return the configured db_path (file path or shared Connection)."""
    return current_app.config.get("DB_PATH", None)


@auth_bp.route("/", methods=["GET"])
def index():
    """Root URL — redirect to login or dashboard based on session state."""
    if "user_id" in session:
        return redirect(url_for("dashboard.dashboard"))
    return redirect(url_for("auth.login"))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """
    GET  — Render the login form. Redirect to dashboard if already logged in.
    POST — Validate credentials, create session on success.
    """
    # Already authenticated — go straight to dashboard
    if "user_id" in session:
        return redirect(url_for("dashboard.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        # --- Field presence validation ---
        if not username:
            flash("Username is required.", "danger")
            return render_template("login.html")

        if not password:
            flash("Password is required.", "danger")
            return render_template("login.html", username=username)

        # --- Database lookup ---
        user = get_user_by_username(username, _db())

        # Use the same generic message for both "not found" and "wrong password"
        # to prevent username enumeration.
        if user is None or not check_password_hash(user["password"], password):
            flash("Invalid username or password.", "danger")
            return render_template("login.html", username=username)

        # --- Success: build session ---
        session.clear()  # rotate session to prevent fixation
        session["user_id"] = user["id"]
        session["username"] = user["username"]
        session["fullname"] = user["fullname"]

        flash(f"Welcome back, {user['fullname']}!", "success")
        return redirect(url_for("dashboard.dashboard"))

    # GET request
    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    """Clear the session and redirect to the login page."""
    session.clear()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for("auth.login"))
