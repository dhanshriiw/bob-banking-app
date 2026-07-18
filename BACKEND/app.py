"""
app.py — Flask Application Entry Point
Initialises the app, registers blueprints, and starts the dev server.
"""

import os
import logging
from flask import Flask
from dotenv import load_dotenv

# Load environment variables from .env (if present)
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

# ── Logging ────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ── Resolve paths so Flask finds templates/static in FRONTEND/ ─────────
_BASE_DIR     = os.path.dirname(__file__)          # .../BACKEND
_FRONTEND_DIR = os.path.join(_BASE_DIR, "..", "FRONTEND")

# ── Application Factory ─────────────────────────────────────────────────
def create_app(db_path: str = None) -> Flask:
    """
    Create and configure the Flask application.
    Accepts an optional db_path so tests can inject an in-memory database.
    """
    app = Flask(
        __name__,
        template_folder=os.path.join(_FRONTEND_DIR, "templates"),
        static_folder=os.path.join(_FRONTEND_DIR, "static"),
        static_url_path="/static",
    )

    # ── Configuration ──────────────────────────────────────────────────
    app.config["SECRET_KEY"] = os.environ.get(
        "SECRET_KEY", "dev-secret-key-change-in-production-32chars!!"
    )
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    # Store db_path on app config so blueprints can pass it to models if needed
    if db_path:
        app.config["DB_PATH"] = db_path

    # ── Database Initialisation ────────────────────────────────────────
    from models import init_db
    init_db(db_path)
    logger.info("Database ready.")

    # ── Blueprint Registration ─────────────────────────────────────────
    from auth         import auth_bp
    from dashboard    import dashboard_bp
    from transactions import transactions_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(transactions_bp)

    # ── Custom Error Handlers ──────────────────────────────────────────
    from flask import render_template as rt

    @app.errorhandler(404)
    def not_found(e):
        return rt("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        logger.error("500 error: %s", e)
        return rt("errors/500.html"), 500

    logger.info("Blueprints registered. App ready.")
    return app


# ── Dev Server Entry Point ─────────────────────────────────────────────
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="127.0.0.1", port=5000)
