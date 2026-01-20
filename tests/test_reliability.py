import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add src to path

from exceptions import NavigationError, SessionError
from navigator import AriaNavigator

class TestReliability(unittest.TestCase):
    @patch('navigator.webdriver.Remote')
    def test_navigate_raises_navigation_error(self, mock_remote):
        nav = AriaNavigator()
        # Mock successful connection
        mock_driver = MagicMock()
        nav.driver = mock_driver
        
        from selenium.common.exceptions import WebDriverException
        mock_driver.get.side_effect = WebDriverException("Simulated failure")
        
        with self.assertRaises(NavigationError):
            nav.navigate("https://example.com")

    def test_navigate_without_session_raises_session_error(self):
        nav = AriaNavigator()
        # Ensure no session
        with patch.object(AriaNavigator, 'connect_to_session', return_value=None):
            with self.assertRaises(SessionError):
                nav.navigate("https://example.com")

if __name__ == "__main__":
    unittest.main()
