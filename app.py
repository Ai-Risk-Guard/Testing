"""
AUREX Vulnerability Lab
Local-only banking portal with an intentional SQL injection flaw.

WARNING:
The login implementation is intentionally vulnerable.
This application is for controlled educational demonstrations only.
"""

import os
import secrets
import sqlite3

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
)

from config import DATABASE_PATH
from database import (
    initialize_database,
    get_user_by_id,
    get_user_transactions,
)


def create_app(test_config=None):
    """Create and configure the Flask application."""

    app = Flask(__name__)

    app.config.update(
        SECRET_KEY=os.environ.get(
            "FLASK_SECRET_KEY"
        ) or secrets.token_hex(32),

        TESTING=False,
    )

    if test_config:
        app.config.update(test_config)

    initialize_database()

    @app.route("/", methods=["GET"])
    def index():
        """Display the login page."""

        return render_template("index.html")

    @app.route("/login", methods=["POST"])
    def login():
        """
        INTENTIONALLY VULNERABLE LOGIN.

        The username and password are inserted directly into the SQL
        statement using string formatting.

        This permits SQL injection.

        Do not use this implementation in a real application.
        """

        username = request.form.get(
            "username", ""
        ).strip()

        password = request.form.get(
            "password", ""
        )

        if not username or not password:
            flash(
                "Please enter both username and password.",
                "error",
            )

            return redirect(url_for("index"))

        connection = sqlite3.connect(DATABASE_PATH)
        connection.row_factory = sqlite3.Row

        try:
            # INTENTIONALLY VULNERABLE:
            # Untrusted input is concatenated into the SQL query.
            query = (
                "SELECT id, username, full_name "
                "FROM users "
                f"WHERE username = '{username}' "
                f"AND password = '{password}' "
                "LIMIT 1"
            )

            user = connection.execute(query).fetchone()

        except sqlite3.Error:
            # Avoid exposing internal SQL errors to the browser.
            app.logger.warning(
                "Login query failed.",
                exc_info=True,
            )

            flash(
                "Login could not be completed.",
                "error",
            )

            return redirect(url_for("index"))

        finally:
            connection.close()

        if user:
            session.clear()

            session["user_id"] = user["id"]

            return redirect(url_for("dashboard"))

        flash(
            "Invalid username or password.",
            "error",
        )

        return redirect(url_for("index"))

    @app.route("/dashboard", methods=["GET"])
    def dashboard():
        """Display account details after login."""

        user_id = session.get("user_id")

        if not user_id:
            flash(
                "Please log in to access the dashboard.",
                "error",
            )

            return redirect(url_for("index"))

        user = get_user_by_id(user_id)

        if not user:
            session.clear()

            flash(
                "Your session is no longer valid.",
                "error",
            )

            return redirect(url_for("index"))

        transactions = get_user_transactions(user_id)

        return render_template(
            "dashboard.html",
            user=user,
            transactions=transactions,
        )

    @app.route("/logout", methods=["POST"])
    def logout():
        """End the current session."""

        session.clear()

        flash(
            "You have been logged out.",
            "success",
        )

        return redirect(url_for("index"))

    @app.route("/security-status", methods=["GET"])
    def security_status():
        """Display a simple lab status page."""

        return render_template("security_status.html")

    @app.route("/health", methods=["GET"])
    def health():
        """Basic local application health check."""

        return {
            "status": "ok",
            "application": "AUREX Vulnerability Lab",
        }, 200

    return app


app = create_app()


if __name__ == "__main__":
    # Bind only to the local machine.
    # Do not change this to 0.0.0.0 for the vulnerable demonstration.
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
    )