import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import json

from navigator import AriaNavigator
from selenium.common.exceptions import WebDriverException as MockWebDriverException

class TestSessionRecovery(unittest.TestCase):
    def setUp(self):
        self.nav = AriaNavigator()
        self.test_session_file = self.nav.get_session_file_path("test_browser")
        if os.path.exists(self.test_session_file):
            os.remove(self.test_session_file)
        # Ensure current session file doesn't point to test_browser
        current_file = self.nav.get_session_file_path()
        if os.path.exists(current_file):
            os.remove(current_file)

    def tearDown(self):
        if os.path.exists(self.test_session_file):
            os.remove(self.test_session_file)

    @patch('navigator.AriaNavigator._is_process_running', return_value=False)
    def test_connect_to_dead_process_cleans_up(self, mock_is_running):
        # Create a fake session file
        session_data = {
            "session_id": "fake_id",
            "url": "http://localhost:9999",
            "browser": "test_browser",
            "driver_pid": 12345
        }
        with open(self.test_session_file, "w") as f:
            json.dump(session_data, f)
        
        # Should return None because process is dead
        result = self.nav.connect_to_session("test_browser")
        self.assertIsNone(result)
        # Should have removed the file
        self.assertFalse(os.path.exists(self.test_session_file))

    @patch('navigator.AriaNavigator._is_process_running', return_value=True)
    @patch('navigator.ReusableRemote')
    def test_connect_to_unhealthy_session_cleans_up(self, mock_remote, mock_is_running):
        # Connection attempt fails
        mock_remote.side_effect = MockWebDriverException("Unhealthy")
        
        session_data = {
            "session_id": "fake_id",
            "url": "http://localhost:9999",
            "browser": "test_browser",
            "driver_pid": 12345
        }
        with open(self.test_session_file, "w") as f:
            json.dump(session_data, f)
        
        # Should return None because connection fails
        result = self.nav.connect_to_session("test_browser")
        self.assertIsNone(result)
        # Should have removed the file
        self.assertFalse(os.path.exists(self.test_session_file))

    @patch('navigator.AriaNavigator.list_active_browsers', return_value=["test_browser"])
    @patch('navigator.AriaNavigator._load_session_data')
    @patch('navigator.ReusableRemote')
    def test_cleanup_orphaned_sessions(self, mock_remote, mock_load, mock_list):
        mock_load.return_value = {
            "session_id": "fake_id",
            "url": "http://localhost:9999",
            "browser": "test_browser",
            "driver_pid": 12345
        }
        # Connection fails during cleanup check
        mock_remote.side_effect = MockWebDriverException("Unhealthy")
        
        with patch('navigator.AriaNavigator.close_session') as mock_close:
            count = self.nav.cleanup_orphaned_sessions()
            self.assertEqual(count, 1)
            mock_close.assert_called_with("test_browser")

if __name__ == "__main__":
    unittest.main()