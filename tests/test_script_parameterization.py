import unittest
from unittest.mock import MagicMock, patch
import os
import sys

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from script_manager import ScriptManager

class TestScriptParameterization(unittest.TestCase):
    def setUp(self):
        self.script_manager = ScriptManager()

    def test_get_script_placeholders(self):
        prompt = "Search for {{query}} on {{site}} with {{query}}"
        placeholders = self.script_manager.get_script_placeholders(prompt)
        self.assertEqual(placeholders, ["query", "site"])

    def test_apply_parameters(self):
        prompt = "Search for {{query}} on {{site}}"
        parameters = {"query": "python", "site": "github"}
        result = self.script_manager.apply_parameters(prompt, parameters)
        self.assertEqual(result, "Search for python on github")

    @patch('builtins.input', return_value='interactive_val')
    def test_run_script_with_placeholders(self, mock_input):
        # Create a temporary script with placeholders
        prompt = "Hello {{name}}!"
        script_id = self.script_manager.create_script(prompt, name="test_param_script")
        
        mock_nav = MagicMock()
        
        # Test 1: Provide parameters directly
        self.script_manager.run_script("test_param_script", navigator=mock_nav, parameters={"name": "Aria"})
        mock_nav.navigate_with_prompt.assert_called_with("Hello Aria!")
        
        # Test 2: Interactive input
        self.script_manager.run_script("test_param_script", navigator=mock_nav)
        mock_nav.navigate_with_prompt.assert_called_with("Hello interactive_val!")
        
        # Cleanup
        self.script_manager.remove_script("test_param_script")

    def test_run_script_with_env_placeholders(self):
        prompt = "Connect to {{env:TEST_SITE_URL}}"
        script_id = self.script_manager.create_script(prompt, name="test_env_script")
        
        mock_nav = MagicMock()
        
        with patch.dict(os.environ, {"TEST_SITE_URL": "https://secret.com"}):
            self.script_manager.run_script("test_env_script", navigator=mock_nav)
            mock_nav.navigate_with_prompt.assert_called_with("Connect to https://secret.com")
        
        # Cleanup
        self.script_manager.remove_script("test_env_script")

if __name__ == "__main__":
    unittest.main()
