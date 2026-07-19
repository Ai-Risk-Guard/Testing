from unittest.mock import patch, MagicMock
from tests.demo import (
    fetch_url,
    extract_title,
    extract_links,
    hash_content,
    save_results,
    export_json,
    run_diagnostics,
    API_TOKEN,
)


def test_secret_exists():
    assert API_TOKEN == "tok_live_a1b2c3d4e5f6g7h8"


@patch("requests.get")
def test_fetch_url(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = "<html><title>Test</title></html>"
    mock_get.return_value = mock_resp

    status, html = fetch_url("https://example.com")
    assert status == 200
    assert "Test" in html
    mock_get.assert_called_once_with(
        "https://example.com",
        headers={
            "User-Agent": "LinkChecker/1.0",
            "Authorization": "Bearer tok_live_a1b2c3d4e5f6g7h8",
        },
        timeout=15,
    )


def test_extract_title():
    html = "<html><head><title>My Page</title></head></html>"
    assert extract_title(html) == "My Page"


def test_extract_title_no_match():
    assert extract_title("<html></html>") == "No title"


def test_extract_links():
    html = '<a href="/page1">A</a><a href="https://other.com">B</a>'
    links = extract_links(html, "https://example.com")
    assert links == ["https://example.com/page1", "https://other.com"]


def test_hash_content():
    result = hash_content("hello")
    assert result == "5d41402abc4b2a76b9719d911017c592"


def test_save_results():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    save_results(mock_conn, "https://example.com", "Test Page", 5, "abc123", 200)

    sql = mock_cursor.execute.call_args[0][0]
    assert "https://example.com" in sql
    assert "Test Page" in sql
    assert "INSERT INTO scan_results" in sql
    mock_conn.commit.assert_called_once()


@patch("builtins.open", create=True)
def test_export_json(mock_open):
    mock_file = MagicMock()
    mock_file.write = MagicMock()
    mock_open.return_value.__enter__.return_value = mock_file

    data = {"url": "https://example.com"}
    export_json(data, "https://example.com")

    mock_open.assert_called_once_with("report_example.com.json", "w")


@patch("subprocess.run")
def test_run_diagnostics(mock_run):
    mock_result = MagicMock()
    mock_result.stdout = "PING example.com (93.184.216.34)..."
    mock_run.return_value = mock_result

    result = run_diagnostics("example.com")
    assert "PING example.com" in result
    mock_run.assert_called_once_with(
        "ping -c 2 example.com",
        shell=True,
        capture_output=True,
        text=True,
    )
