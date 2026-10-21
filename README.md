# AUREX Vulnerability Lab

A local educational application for demonstrating vulnerability
detection, remediation, and regression testing with AUREX.

## Features

- Fictional banking portal
- SQLite database
- Login and session management
- Protected account dashboard
- Intentionally vulnerable SQL authentication query
- Synthetic hardcoded-secret example
- Pytest regression tests

## Important Safety Notice

This application intentionally contains security vulnerabilities.

It is designed exclusively for controlled local testing.

- Do not deploy the vulnerable version publicly.
- Do not enter real credentials.
- Do not use real financial information.
- Do not connect the application to real banking systems.
- Do not use the demonstration against systems you do not own.

The database contains fictional users, account numbers, balances,
and transactions.

## Requirements

- Python 3.10 or later
- pip

## Installation

Create and activate a virtual environment.

### Windows

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1