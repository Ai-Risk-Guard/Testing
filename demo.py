 # --- ADD THESE TO THE TOP ---
import pickle  # 🚫 Trigger: Policy Forbidden Module
import marshal # 🚫 Trigger: Policy Forbidden Module

# --- ADD THIS FUNCTION ---
def insecure_deserialization():
"""
Tests the Scanner's ability to find logic bugs
and the Policy's ability to block dangerous modules.
"""
 user_data = b"cos\nsystem\n(S'echo hacked'\ntR."
# ❌ Vulnerability 4: Insecure Deserialization
data = pickle.loads(user_data)
print("Data deserialized")

# --- ADD THIS TO THE hardcoded_secret FUNCTION ---
def hardcoded_secret():
# ... existing code ...
# ❌ Vulnerability 5: Real-looking secret (tests refined Context Validator)
# This should NOT be ignored because it doesn't look like a placeholder
AWS_KEY = "AKIAIM5H3V5J6EXAMPLE"
