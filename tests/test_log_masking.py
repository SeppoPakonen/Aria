import unittest
import os
import logging
from logger import setup_logging, get_logger, add_secret, redact, secrets_var, RedactingFilter
from script_manager import ScriptManager
from credential_manager import CredentialManager

class TestLogMasking(unittest.TestCase):
    def setUp(self):
        # Reset secrets for each test
        secrets_var.set(set())
        
        # Configure logging for the tests
        self.logger = get_logger("test_masking")
        self.logger.setLevel(logging.INFO)
        if not any(isinstance(f, RedactingFilter) for f in self.logger.filters):
            self.logger.addFilter(RedactingFilter())

    def test_basic_redaction(self):
        add_secret("my_super_secret_password")
        with self.assertLogs("test_masking", level="INFO") as cm:
            self.logger.info("The password is my_super_secret_password")
            self.assertIn("The password is [REDACTED]", cm.output[0])

    def test_multiple_secrets(self):
        add_secret("secret1")
        add_secret("secret2")
        with self.assertLogs("test_masking", level="INFO") as cm:
            self.logger.info("Here are secret1 and secret2")
            self.assertIn("Here are [REDACTED] and [REDACTED]", cm.output[0])

    def test_substring_redaction(self):
        add_secret("password")
        add_secret("password123")
        with self.assertLogs("test_masking", level="INFO") as cm:
            self.logger.info("Using password123")
            self.assertIn("Using [REDACTED]", cm.output[0])

    def test_short_string_no_redaction(self):
        # We added a check for len(secret) > 3
        add_secret("abc")
        with self.assertLogs("test_masking", level="INFO") as cm:
            self.logger.info("This is abc")
            self.assertIn("This is abc", cm.output[0])

    def test_script_manager_redaction(self):
        # Mock vault and env
        os.environ["ARIA_TEST_SECRET"] = "env_secret_val"
        cm = CredentialManager()
        cm.set_credential("test_vault_key", "vault_secret_val")
        
        sm = ScriptManager()
        
        # Create a script that uses these
        prompt = "Login with {{env:ARIA_TEST_SECRET}} and {{vault:test_vault_key}}"
        script_id = sm.create_script(prompt, "test_masking_script")
        
        # Mock navigator
        class MockNavigator:
            def navigate_with_prompt(self, p):
                sm_logger = logging.getLogger("script_manager")
                if not any(isinstance(f, RedactingFilter) for f in sm_logger.filters):
                    sm_logger.addFilter(RedactingFilter())
                sm_logger.info(f"Executing: {p}")
        
        with self.assertLogs("script_manager", level="INFO") as cm_logs:
            sm.run_script("test_masking_script", navigator=MockNavigator())
            
            combined_output = "\n".join(cm_logs.output)
            self.assertIn("Executing: Login with [REDACTED] and [REDACTED]", combined_output)
            self.assertNotIn("env_secret_val", combined_output)
            self.assertNotIn("vault_secret_val", combined_output)

if __name__ == "__main__":
    unittest.main()