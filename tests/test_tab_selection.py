import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add src to path

from navigator import AriaNavigator

class TestTabSelection(unittest.TestCase):
    def setUp(self):
        self.navigator = AriaNavigator()
        self.mock_driver = MagicMock()
        self.navigator.driver = self.mock_driver
        self.handles = ['handle0', 'handle1', 'handle2']
        self.mock_driver.window_handles = self.handles
        self.mock_driver.current_window_handle = 'handle0'

    def test_goto_by_handle_exact(self):
        self.assertTrue(self.navigator.goto_tab('handle1'))
        self.mock_driver.switch_to.window.assert_called_with('handle1')

    def test_goto_by_index(self):
        self.assertTrue(self.navigator.goto_tab(2))
        self.mock_driver.switch_to.window.assert_called_with('handle2')
        
        self.assertTrue(self.navigator.goto_tab('1'))
        self.mock_driver.switch_to.window.assert_called_with('handle1')

    def test_goto_by_partial_handle(self):
        # We need to make sure the loop doesn't find exact handle first
        # Identifier 'handle' is 6 chars, should match 'handle0'
        self.assertTrue(self.navigator.goto_tab('handle'))
        self.mock_driver.switch_to.window.assert_called_with('handle0')

        # 'ndle1' is 5 chars, should match 'handle1'
        self.assertTrue(self.navigator.goto_tab('ndle1'))
        self.mock_driver.switch_to.window.assert_called_with('handle1')

    def test_goto_by_title_exact(self):
        titles = {
            'handle0': 'Google',
            'handle1': 'Bing',
            'handle2': 'Yahoo'
        }
        def side_effect(h):
            self.mock_driver.title = titles[h]
            return MagicMock()
        self.mock_driver.switch_to.window.side_effect = side_effect
        
        self.assertTrue(self.navigator.goto_tab('Bing'))
        self.mock_driver.switch_to.window.assert_called_with('handle1')

    def test_goto_by_title_partial(self):
        titles = {
            'handle0': 'Google Search',
            'handle1': 'Bing Search',
            'handle2': 'Yahoo Search'
        }
        def side_effect(h):
            self.mock_driver.title = titles[h]
            self.mock_driver.current_url = f"http://{titles[h].split()[0].lower()}.com"
            return MagicMock()
        self.mock_driver.switch_to.window.side_effect = side_effect
        
        # Partial case-insensitive
        self.assertTrue(self.navigator.goto_tab('google'))
        self.mock_driver.switch_to.window.assert_called_with('handle0')
        
        self.assertTrue(self.navigator.goto_tab('Bing'))
        self.mock_driver.switch_to.window.assert_called_with('handle1')

    def test_goto_by_url_partial(self):
        titles = {
            'handle0': 'Google',
            'handle1': 'Bing',
            'handle2': 'Yahoo'
        }
        urls = {
            'handle0': 'https://www.google.com/search?q=test',
            'handle1': 'https://www.bing.com/search?q=test',
            'handle2': 'https://www.yahoo.com'
        }
        def side_effect(h):
            self.mock_driver.title = titles[h]
            self.mock_driver.current_url = urls[h]
            return MagicMock()
        self.mock_driver.switch_to.window.side_effect = side_effect
        
        self.assertTrue(self.navigator.goto_tab('bing.com'))
        self.mock_driver.switch_to.window.assert_called_with('handle1')

    def test_goto_not_found(self):
        self.mock_driver.current_window_handle = 'handle0'
        self.assertFalse(self.navigator.goto_tab('NonExistent'))
        # Should have switched back to handle0
        self.mock_driver.switch_to.window.assert_called_with('handle0')

    @patch('navigator.AriaNavigator._load_session_data')
    @patch('navigator.AriaNavigator._save_session')
    @patch('navigator.AriaNavigator._get_current_browser')
    def test_tagging(self, mock_get_browser, mock_save, mock_load):
        mock_get_browser.return_value = 'chrome'
        mock_load.return_value = {"session_id": "123", "url": "http://localhost:1", "tags": {}}
        self.mock_driver.current_window_handle = 'handle1'
        
        self.assertTrue(self.navigator.tag_tab('handle1', 'news'))
        
        # Check if save was called with the tag
        args, _ = mock_save.call_args
        self.assertEqual(args[0], 'chrome')
        self.assertEqual(args[1]['tags']['handle1'], ['news'])
        
        # Test get_tabs_by_tag
        mock_load.return_value = args[1] # Use the saved data
        handles = self.navigator.get_tabs_by_tag('news')
        self.assertEqual(handles, ['handle1'])

if __name__ == '__main__':
    unittest.main()
