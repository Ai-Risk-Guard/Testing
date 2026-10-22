# Vulnerable baseline

This folder documents the starting state; the runnable app is at the repository root.

- SQL query construction concatenates user input into SQL.
- `config.py` contains a synthetic hardcoded secret marker.
- Tests in `tests/` intentionally confirm these weaknesses.

Run the app only on `127.0.0.1`. Never add real secrets or real records.
