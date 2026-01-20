import unittest
from unittest.mock import MagicMock, patch
import sys
import os
from io import StringIO

try:
    from google import genai
    import selenium
    DEPENDENCIES_INSTALLED = True
except ImportError:
    DEPENDENCIES_INSTALLED = False

# Add src to path

@unittest.skipUnless(DEPENDENCIES_INSTALLED, "Dependencies for aria.py not installed")
class TestAriaCredentials(unittest.TestCase):
    def setUp(self):
        from aria import main
        self.main = main

    @patch('aria.CredentialManager')
    def test_settings_credentials_set(self, mock_cm):
        mock_cm_inst = mock_cm.return_value
        
        # Test command: aria settings credentials set mykey myval
        with patch('sys.argv', ['aria', 'settings', 'credentials', 'set', 'mykey', 'myval']):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                self.main()
                output = fake_out.getvalue()
                self.assertIn("Credential 'mykey' set successfully.", output)
                mock_cm_inst.set_credential.assert_called_with("mykey", "myval")

    @patch('aria.CredentialManager')
    def test_settings_credentials_list(self, mock_cm):
        mock_cm_inst = mock_cm.return_value
        mock_cm_inst.list_keys.return_value = ["key1", "key2"]
        
        # Test command: aria settings credentials list
        with patch('sys.argv', ['aria', 'settings', 'credentials', 'list']):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                self.main()
                output = fake_out.getvalue()
                self.assertIn("Stored Credentials (keys only):", output)
                self.assertIn("- key1", output)
                self.assertIn("- key2", output)

    @patch('aria.CredentialManager')
    def test_settings_credentials_remove(self, mock_cm):
        mock_cm_inst = mock_cm.return_value
        mock_cm_inst.remove_credential.return_value = True
        
        # Test command: aria settings credentials remove key1
        with patch('sys.argv', ['aria', 'settings', 'credentials', 'remove', 'key1']):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                self.main()
                output = fake_out.getvalue()
                self.assertIn("Credential 'key1' removed successfully.", output)
                mock_cm_inst.remove_credential.assert_called_with("key1")

if __name__ == "__main__":
    unittest.main()
