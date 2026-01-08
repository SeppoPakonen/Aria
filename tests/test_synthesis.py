import unittest
from unittest.mock import MagicMock
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from aria import resolve_prompt_and_get_content

class TestSynthesis(unittest.TestCase):
    def test_resolve_prompt_with_tabs(self):
        mock_navigator = MagicMock()
        mock_navigator.get_tabs_content.return_value = [
            {'identifier': '0', 'title': 'Page 0', 'url': 'http://0.com', 'content': 'Content 0'},
            {'identifier': '1', 'title': 'Page 1', 'url': 'http://1.com', 'content': 'Content 1'}
        ]
        
        prompt = "Compare tab 0 and tab 1"
        refined_prompt, context = resolve_prompt_and_get_content(prompt, mock_navigator)
        
        self.assertEqual(refined_prompt, prompt)
        self.assertIn("Content from Tab 0", context)
        self.assertIn("Content from Tab 1", context)
        self.assertIn("Page 0", context)
        self.assertIn("Page 1", context)
        
        mock_navigator.get_tabs_content.assert_called_once()
        # Note: the order might vary if identifiers set is used, but we check presence
        call_args = mock_navigator.get_tabs_content.call_args[0][0]
        self.assertIn('0', call_args)
        self.assertIn('1', call_args)

    def test_resolve_prompt_no_tabs(self):
        mock_navigator = MagicMock()
        prompt = "Just a regular prompt"
        refined_prompt, context = resolve_prompt_and_get_content(prompt, mock_navigator)
        
        self.assertEqual(refined_prompt, prompt)
        self.assertEqual(context, "")
        mock_navigator.get_tabs_content.assert_not_called()

if __name__ == '__main__':
    unittest.main()
