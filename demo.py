# 🚨 AI Risk Guard Demo File
# This file intentionally contains vulnerabilities for testing

import os


def run_user_command():
    user_input = input("Enter a command: ")
    
    # ❌ Vulnerability 1: Command Injection
    os.system(user_input)


def unsafe_eval():
    data = input("Enter Python expression: ")
    
    # ❌ Vulnerability 2: Code Injection
    result = eval(data)
    print(result)


def hardcoded_secret():
    # ❌ Vulnerability 3: Hardcoded Secret
    password = "super_secret_123"
    api_token = "token_ABC123XYZ"

    print("Secrets loaded")


if __name__ == "__main__":
    print("Running vulnerable demo file...\n")

    run_user_command()
    unsafe_eval()
    hardcoded_secret()
