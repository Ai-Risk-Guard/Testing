"""
Database utilities for the AUREX Vulnerability Lab.

All records are fictional and created locally.
"""

import sqlite3

from config import DATABASE_PATH


def get_connection():
    """Create a connection to the local SQLite database."""

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    return connection


def initialize_database():
    """
    Create the database and insert fictional demonstration users.

    This lab intentionally uses plaintext demo passwords so that
    the SQL injection vulnerability can be demonstrated clearly.

    Never store plaintext passwords in a real application.
    """

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                full_name TEXT NOT NULL,
                account_number TEXT NOT NULL,
                balance REAL NOT NULL
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                description TEXT NOT NULL,
                amount REAL NOT NULL,
                transaction_type TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            """
        )

        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]

        if user_count == 0:
            users = [
                (
                    "alice",
                    "alice-demo-123",
                    "Alice Johnson",
                    "DEMO-1001",
                    12500.50,
                ),
                (
                    "bob",
                    "bob-demo-456",
                    "Bob Williams",
                    "DEMO-1002",
                    8300.00,
                ),
                (
                    "charlie",
                    "charlie-demo-789",
                    "Charlie Brown",
                    "DEMO-1003",
                    21950.75,
                ),
            ]

            cursor.executemany(
                """
                INSERT INTO users (
                    username,
                    password,
                    full_name,
                    account_number,
                    balance
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                users,
            )

            cursor.execute(
                "SELECT id, username FROM users"
            )

            user_ids = {
                row["username"]: row["id"]
                for row in cursor.fetchall()
            }

            transactions = [
                (
                    user_ids["alice"],
                    "Monthly salary",
                    5000.00,
                    "CREDIT",
                ),
                (
                    user_ids["alice"],
                    "Grocery purchase",
                    150.25,
                    "DEBIT",
                ),
                (
                    user_ids["bob"],
                    "Online purchase",
                    99.99,
                    "DEBIT",
                ),
                (
                    user_ids["bob"],
                    "Account deposit",
                    1200.00,
                    "CREDIT",
                ),
                (
                    user_ids["charlie"],
                    "Monthly salary",
                    6500.00,
                    "CREDIT",
                ),
            ]

            cursor.executemany(
                """
                INSERT INTO transactions (
                    user_id,
                    description,
                    amount,
                    transaction_type
                )
                VALUES (?, ?, ?, ?)
                """,
                transactions,
            )

        connection.commit()

    finally:
        connection.close()


def get_user_by_id(user_id):
    """Return a user's fictional account details."""

    connection = get_connection()

    try:
        return connection.execute(
            """
            SELECT
                id,
                username,
                full_name,
                account_number,
                balance
            FROM users
            WHERE id = ?
            """,
            (user_id,),
        ).fetchone()

    finally:
        connection.close()


def get_user_transactions(user_id):
    """Return transactions belonging to one fictional user."""

    connection = get_connection()

    try:
        return connection.execute(
            """
            SELECT
                description,
                amount,
                transaction_type
            FROM transactions
            WHERE user_id = ?
            ORDER BY id DESC
            """,
            (user_id,),
        ).fetchall()

    finally:
        connection.close()