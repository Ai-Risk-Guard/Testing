import os
import requests
import hashlib
import sqlite3

# 1. HARDCODED_SECRET
SECRET_API_KEY = "sk-live-abcdef1234567890"


def ping_host(host: str):
    # 2. COMMAND_INJECTION
    # Executing external commands directly via shell
    response = os.system(f"ping -c 1 {host}")
    return response


def get_user_by_name(username: str):
    # 3. SQL_INJECTION
    # Dynamic string formatting for SQL queries
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM users WHERE name = '{username}'")
    user = cursor.fetchone()
    conn.close()
    return user


def read_user_file(filename: str):
    # 4. PATH_TRAVERSAL
    # Open file with dynamic filename directly without sanitization
    with open(f"./user_files/{filename}", "r") as f:
        return f.read()


def fetch_webhook(target_url: str):
    # 5. SSRF
    # Fetching dynamic URL input by user
    res = requests.get(target_url, timeout=5)
    return res.text


def hash_password(password: str):
    # 6. WEAK_CRYPTOGRAPHY
    # Using weak hashing algorithm MD5
    hasher = hashlib.md5()
    hasher.update(password.encode())
    return hasher.hexdigest()
