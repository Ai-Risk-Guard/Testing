import os
import tempfile

import pytest

import app as application


@pytest.fixture
def client(monkeypatch):
    """
    Provide an isolated test database for each test.

    Tests do not use the main demonstration database.
    """

    fd, database_path = tempfile.mkstemp(
        suffix=".db"
    )

    os.close(fd)

    monkeypatch.setattr(
        application,
        "DATABASE_PATH",
        database_path,
    )

    # database.py imported DATABASE_PATH separately,
    # so patch that reference as well.
    import database

    monkeypatch.setattr(
        database,
        "DATABASE_PATH",
        database_path,
    )

    test_app = application.create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "pytest-only-session-key",
        }
    )

    with test_app.test_client() as test_client:
        yield test_client

    if os.path.exists(database_path):
        os.remove(database_path)