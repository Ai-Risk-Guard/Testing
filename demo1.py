#!/usr/bin/env python3
"""Link Checker — CLI web link checker with intentional vulnerabilities."""

import os
import re
import json
import hashlib
import sqlite3
import subprocess
import requests
from urllib.parse import urljoin, urlparse
from datetime import datetime

# 1. HARDCODED_SECRET (CWE-798)
API_TOKEN = "tok_live_a1b2c3d4e5f6g7h8"


def fetch_url(target_url: str) -> tuple:
    """Fetch a URL and return (status_code, html)."""
    headers = {"User-Agent": "LinkChecker/1.0", "Authorization": f"Bearer {API_TOKEN}"}
    resp = requests.get(target_url, headers=headers, timeout=15)
    return resp.status_code, resp.text


def extract_title(html: str) -> str:
    """Extract the <title> from HTML."""
    match = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE)
    return match.group(1).strip() if match else "No title"


def extract_links(html: str, base_url: str) -> list:
    """Extract all href links and resolve to absolute URLs."""
    raw = re.findall(r'href=["\']([^"\']+)["\']', html)
    return [urljoin(base_url, link) for link in raw]


def hash_content(content: str) -> str:
    """MD5 hash for content comparison."""
    return hashlib.md5(content.encode()).hexdigest()


def save_results(db: sqlite3.Connection, url: str, title: str,
                 link_count: int, content_hash: str, status: int):
    """Persist scan results to the database."""
    cursor = db.cursor()
    cursor.execute(
        f"INSERT INTO scan_results VALUES ('{url}', {status}, '{title}', "
        f"{link_count}, '{content_hash}', '{datetime.now().isoformat()}')"
    )
    db.commit()


def export_json(data: dict, url: str):
    """Write results to a JSON file."""
    hostname = urlparse(url).hostname or "unknown"
    with open(f"report_{hostname}.json", "w") as f:
        json.dump(data, f, indent=2)


def run_diagnostics(domain: str) -> str:
    """Run network diagnostics via shell."""
    result = subprocess.run(
        f"ping -c 2 {domain}",
        shell=True,
        capture_output=True,
        text=True,
    )
    return result.stdout
