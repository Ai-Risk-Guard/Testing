# 🚨 AI Risk Guard - Security Stress Test File
# This file is designed to test Multi-Agent innovation and Policy Enforcement.
import os
import pickle   # 🚫 Policy Violation: Forbidden Module
import marshal  # 🚫 Policy Violation: Forbidden Module

def run_user_command():
# 🚫 Policy Violation: Forbidden Function (input)
 user_input = input("Enter a command to run: ")
# ❌ Vulnerability 1: Command Injection
 os.system(user_input)
def unsafe_eval():
# 🚫 Policy Violation: Forbidden Function (input)
 data = input("Enter Python logic to evaluate: ")
# ❌ Vulnerability 2: Code Injection
# Note: Baseline AST should fix this, but LLM might suggest a better refactor.
 result = eval(data)
 print(f"Result: {result}")
def insecure_deserialization():
# ❌ Vulnerability 3: Insecure Deserialization
# This is a high-risk bug that is hard to fix with templates.
# LLM innovation will shine here.
 malicious_payload = b"cos\nsystem\n(S'echo hacked'\ntR."
 data = pickle.loads(malicious_payload)
 print("Data recovered successfully.")
def hardcoded_secret():
  # ❌ Vulnerability 4: Simple Hardcoded Secret
  # Context Validator might ignore "super_secret_123" if patterns are too loose.
 password = "super_secret_123"
    # ❌ Vulnerability 5: Professional-looking Hardcoded Secret
     # This AKIA string looks like a real AWS key.
     # It tests if your system can distinguish real risks from placeholders.
 AWS_KEY = "AKIAIM5H3V5J6EXAMPLE"
 api_token = "token_ABC123XYZ"
 print("Secrets loaded into memory.")
  
if __name__ == "__main__":
 print("--- STARTING SECURITY STRESS TEST ---")
 # Triggering all vulnerable paths
 run_user_command()
 unsafe_eval()
 insecure_deserialization()
 hardcoded_secret()
 print("--- TEST COMPLETE ---")
