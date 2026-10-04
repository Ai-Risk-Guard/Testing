"""Tests for the Task Tracker demo application (root ``demo.py``)."""

from unittest.mock import MagicMock, patch

from demo import (
    DB_PASSWORD,
    add_preview_note,
    create_task,
    delete_task,
    export_all_tasks,
    export_matches,
    get_task,
    hash_api_token,
    init_db,
    list_tasks,
    load_preview_cache,
    read_attachment,
    save_preview_cache,
    search_tasks,
    update_task_status,
    verify_api_token,
)


def _conn():
    conn = MagicMock()
    conn.execute.return_value.fetchall.return_value = [
        {"id": 1, "title": "Ship demo", "owner": "alice", "status": "open"}
    ]
    conn.execute.return_value.fetchone.return_value = {
        "id": 1,
        "title": "Ship demo",
        "owner": "alice",
        "status": "open",
    }
    conn.execute.return_value.rowcount = 1
    conn.execute.return_value.lastrowid = 42
    return conn


def test_secret_exists():
    assert DB_PASSWORD == "9kF2#qLz!pRdWx7v"


def test_init_db_runs_schema():
    conn = MagicMock()
    init_db(conn)
    sql = conn.execute.call_args[0][0]
    assert "CREATE TABLE IF NOT EXISTS tasks" in sql
    conn.commit.assert_called_once()


def test_create_task_uses_parameterized_insert():
    conn = _conn()
    task_id = create_task(conn, "Review PR", "check the diff", "bob")
    assert task_id == 42
    sql = conn.execute.call_args[0][0]
    assert "VALUES (?, ?, ?, 'open', ?)" in sql
    params = conn.execute.call_args[0][1]
    assert params[:3] == ("Review PR", "check the diff", "bob")


def test_list_tasks_returns_dicts():
    conn = _conn()
    tasks = list_tasks(conn)
    assert tasks == [{"id": 1, "title": "Ship demo", "owner": "alice", "status": "open"}]


def test_list_tasks_filters_by_status():
    conn = _conn()
    list_tasks(conn, status="done")
    sql = conn.execute.call_args[0][0]
    assert "WHERE status = ?" in sql


def test_get_task_returns_dict():
    conn = _conn()
    task = get_task(conn, 1)
    assert task["title"] == "Ship demo"
    assert "WHERE id = ?" in conn.execute.call_args[0][0]


def test_search_tasks_builds_like_query():
    conn = _conn()
    search_tasks(conn, "rush")
    sql = conn.execute.call_args[0][0]
    assert sql == "SELECT * FROM tasks WHERE title LIKE '%rush%'"


def test_update_task_status():
    conn = _conn()
    assert update_task_status(conn, 1, "done") is True
    sql, params = conn.execute.call_args[0]
    assert "UPDATE tasks SET status = ?" in sql
    assert params == ("done", 1)


def test_delete_task():
    conn = _conn()
    assert delete_task(conn, 1) is True
    assert "DELETE FROM tasks" in conn.execute.call_args[0][0]


def test_read_attachment():
    with patch("builtins.open") as mock_open:
        mock_open.return_value.__enter__.return_value.read.return_value = "content"
        assert read_attachment(7) == "content"
    assert mock_open.call_args[0][0] == "./task_attachments/7.txt"


@patch("demo.os.path.isdir", return_value=True)
@patch("demo.requests.get")
@patch("builtins.open")
def test_add_preview_note(mock_open, mock_get, mock_isdir):
    mock_resp = MagicMock()
    mock_resp.text = "<html><title>Preview</title></html>"
    mock_get.return_value = mock_resp

    snippet = add_preview_note(3, "https://example.com/page")

    mock_get.assert_called_once_with("https://example.com/page", timeout=5)
    assert snippet == "<html><title>Preview</title></html>"
    mock_isdir.assert_called_once()


def test_save_preview_cache_writes_json():
    with patch("demo.os.path.isdir", return_value=True), patch("builtins.open") as mock_open:
        save_preview_cache(3, {"url": "x"})
    assert mock_open.call_args[0][0] == "./previews/3.json"


def test_load_preview_cache_missing():
    with patch("demo.os.path.exists", return_value=False):
        assert load_preview_cache(99) is None


def test_export_matches_uses_shell():
    conn = _conn()
    with patch("demo.subprocess.run") as mock_run:
        mock_run.return_value.stdout = "3:urgent fix\n"
        out = export_matches(conn, "urgent")
    assert out == "3:urgent fix\n"
    mock_run.assert_called_once_with(
        'grep -n "urgent" task_report.csv',
        shell=True,
        capture_output=True,
        text=True,
    )


def test_export_all_tasks_writes_csv():
    conn = _conn()
    with patch("builtins.open") as mock_open:
        handle = mock_open.return_value.__enter__.return_value
        count = export_all_tasks(conn, "report.csv")
    assert count == 1
    handle.writelines.assert_called_once()
    (lines,) = handle.writelines.call_args[0]
    assert list(lines) == ["1,Ship demo,alice,open\n"]


def test_hash_api_token():
    assert hash_api_token("hello") == "5d41402abc4b2a76b9719d911017c592"


def test_verify_api_token():
    digest = hash_api_token("s3cret")
    assert verify_api_token("s3cret", digest) is True
    assert verify_api_token("wrong", digest) is False
