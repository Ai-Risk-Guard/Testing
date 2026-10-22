
"""
AUREX Vulnerability Lab
Local-only banking portal with an intentional SQL injection flaw.

WARNING:
The /login route is intentionally vulnerable.
The /secure-login route demonstrates parameterized SQL.
The /lab/accounts route exposes fictional test data for demonstrations.

Educational use only. Never deploy the vulnerable application publicly.
"""

import os
import secrets
import sqlite3
from functools import wraps

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    jsonify,
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
        SECRET_KEY=os.environ.get("FLASK_SECRET_KEY")
        or secrets.token_hex(32),
        TESTING=False,

        # Explicitly disabled unless enabled for local testing.
        ENABLE_LAB_ACCOUNT_EXPOSURE=True,
    )

    if test_config:
        app.config.update(test_config)

    initialize_database()

    def get_database_connection():
        """Create a SQLite connection with named-column access."""
        connection = sqlite3.connect(DATABASE_PATH)
        connection.row_factory = sqlite3.Row
        return connection

    def local_lab_only(view):
        """
        Restrict sensitive lab routes to loopback clients.

        This is a demonstration safeguard, not a substitute for
        production authentication or authorization.
        """

        @wraps(view)
        def wrapped(*args, **kwargs):
            if request.remote_addr not in ("127.0.0.1", "::1"):
                return jsonify({
                    "error": "This lab endpoint is available locally only."
                }), 403

            if not app.config["ENABLE_LAB_ACCOUNT_EXPOSURE"]:
                return jsonify({
                    "error": (
                        "Lab account exposure is disabled. "
                        "Enable ENABLE_LAB_ACCOUNT_EXPOSURE "
                        "in local test configuration."
                    )
                }), 403

            return view(*args, **kwargs)

        return wrapped

    @app.route("/", methods=["GET"])
    def index():
        """Display the login page."""
        return render_template("index.html")

    @app.route("/login", methods=["POST"])
    def login():
        """
        INTENTIONALLY VULNERABLE LOGIN.

        User-supplied values are concatenated into SQL.
        This route exists only for controlled local demonstrations.
        """

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Please enter both username and password.", "error")
            return redirect(url_for("index"))

        connection = get_database_connection()

        try:
            # INTENTIONALLY VULNERABLE: do not use in real applications.
            query = (
                "SELECT id, username, full_name "
                "FROM users "
                #f"WHERE username = '{username}' "
                "WHERE username = ? "
                #f"AND password = '{password}' "
                "AND password = ? "
                "LIMIT 1"
            )

            #rows = connection.execute(query).fetchall()
            rows = connection.execute(query, (username, password)).fetchall()

            app.logger.warning(
                "[SQL INJECTION LAB] Matching accounts: %s",
                [row["username"] for row in rows],
            )

            user = rows[0] if rows else None

            if user:
                # Log only the selected account identifier, not credentials.
                app.logger.warning(
                    "[SQL INJECTION LAB] Query selected username=%s id=%s",
                    user["username"],
                    user["id"],
                )

        except sqlite3.Error:
            app.logger.warning(
                "[SQL INJECTION LAB] Login query failed.",
                exc_info=True,
            )

            flash("Login could not be completed.", "error")
            return redirect(url_for("index"))

        finally:
            connection.close()

        if user:
            session.clear()
            session["user_id"] = user["id"]
            session["auth_method"] = "vulnerable_login"

            return redirect(url_for("dashboard"))

        flash("Invalid username or password.", "error")
        return redirect(url_for("index"))

    @app.route("/secure-login", methods=["POST"])
    def secure_login():
        """
        Secure comparison route.

        Parameterized SQL treats submitted credentials as data,
        rather than executable SQL.
        """

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Please enter both username and password.", "error")
            return redirect(url_for("index"))

        connection = get_database_connection()

        try:
            user = connection.execute(
                """
                SELECT id, username, full_name
                FROM users
                WHERE username = ? AND password = ?
                LIMIT 1
                """,
                (username, password),
            ).fetchone()

        except sqlite3.Error:
            app.logger.exception("Secure login query failed.")
            flash("Login could not be completed.", "error")
            return redirect(url_for("index"))

        finally:
            connection.close()

        if user:
            session.clear()
            session["user_id"] = user["id"]
            session["auth_method"] = "parameterized_login"

            return redirect(url_for("dashboard"))

        flash(
            "Invalid username or password. SQL input is treated as data.",
            "error",
        )
        return redirect(url_for("index"))

    @app.route("/dashboard", methods=["GET"])
    def dashboard():
        """Display account details for the session's selected user."""

        user_id = session.get("user_id")

        if not user_id:
            flash("Please log in to access the dashboard.", "error")
            return redirect(url_for("index"))

        user = get_user_by_id(user_id)

        if not user:
            session.clear()
            flash("Your session is no longer valid.", "error")
            return redirect(url_for("index"))

        transactions = get_user_transactions(user_id)

        return render_template(
            "dashboard.html",
            user=user,
            transactions=transactions,
        )

    @app.route("/lab/accounts", methods=["GET"])
    @local_lab_only
    def lab_accounts():
        """
        Controlled account-exposure demonstration.

        Returns fictional account records for comparing the impact
        of unauthorized data access. This route does not use SQL
        injection and must remain disabled outside local testing.
        """

        connection = get_database_connection()

        try:
            accounts = connection.execute(
                """
                SELECT id, username, full_name
                FROM users
                ORDER BY id
                """
            ).fetchall()

            result = []

            for account in accounts:
                transactions = get_user_transactions(account["id"])

                result.append({
                    "id": account["id"],
                    "username": account["username"],
                    "full_name": account["full_name"],
                    "transactions": [
                        dict(transaction)
                        for transaction in transactions
                    ],
                })

            return jsonify({
                "warning": (
                    "LOCAL EDUCATIONAL DEMONSTRATION: "
                    "fictional account data only."
                ),
                "account_count": len(result),
                "accounts": result,
            }), 200

        except sqlite3.Error:
            app.logger.exception(
                "Unable to load lab demonstration accounts."
            )
            return jsonify({
                "error": "Unable to load lab account data."
            }), 500

        finally:
            connection.close()

    @app.route("/logout", methods=["POST"])
    def logout():
        """End the current session."""

        session.clear()
        flash("You have been logged out.", "success")

        return redirect(url_for("index"))

    @app.route("/security-status", methods=["GET"])
    def security_status():
        """Display the lab security status page."""
        return render_template("security_status.html")

    @app.route("/health", methods=["GET"])
    def health():
        """Basic application health check."""

        return {
            "status": "ok",
            "application": "AUREX Vulnerability Lab",
        }, 200

    return app


app = create_app()


if __name__ == "__main__":
    # Keep the vulnerable lab bound to the local machine.
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
    )
