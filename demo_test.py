from unittest.mock import patch, MagicMock
from tests.demo import (
    ping_host,
    get_user_by_name,
    read_user_file,
    fetch_webhook,
    hash_password,
    SECRET_API_KEY,
)


def test_secret_exists():
    assert SECRET_API_KEY == "sk-live-abcdef1234567890"


@patch("os.system")
def test_ping_host(mock_system):
    mock_system.return_value = 0
    res = ping_host("127.0.0.1")
    assert res == 0
    mock_system.assert_called_once_with("ping -c 1 127.0.0.1")


@patch("sqlite3.connect")
def test_get_user_by_name(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = ("Alice", "alice@example.com")

    res = get_user_by_name("Alice")
    assert res == ("Alice", "alice@example.com")
    mock_cursor.execute.assert_called_once_with("SELECT * FROM users WHERE name = 'Alice'")


@patch("builtins.open", create=True)
def test_read_user_file(mock_open):
    # Setup mock file context manager
    mock_file = MagicMock()
    mock_open.return_value.__enter__.return_value = mock_file
    mock_file.read.return_value = "file contents"

    res = read_user_file("data.txt")
    assert res == "file contents"
    mock_open.assert_called_once_with("./user_files/data.txt", "r")


@patch("requests.get")
def test_fetch_webhook(mock_get):
    mock_res = MagicMock()
    mock_res.text = "success"
    mock_get.return_value = mock_res

    res = fetch_webhook("http://example.com")
    assert res == "success"
    mock_get.assert_called_once_with("http://example.com", timeout=5)


def test_hash_password():
    res = hash_password("mypassword")
    # MD5 hash of 'mypassword'
    assert res == "34819d7beeabb9260a5c854bc85b3e44"
