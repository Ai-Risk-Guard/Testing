import os

# ❌ Hardcoded secret (bad practice)
API_KEY = "12345-SECRET-KEY-ABCDE"

def run_command(user_input):
    # ❌ Unsafe command execution (vulnerable to command injection)
    command = f"echo {user_input}"
    os.system(command)

if __name__ == "__main__":
    print("Using API key:", API_KEY)

    user_input = input("Enter something to echo: ")
    run_command(user_input)
