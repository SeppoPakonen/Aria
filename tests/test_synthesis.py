import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add src to path

from aria import generate_ai_response, summarize_text
from navigator import AriaNavigator

class TestSynthesis(unittest.TestCase):
    @patch('aria.genai.Client')
    @patch.dict(os.environ, {'GEMINI_API_KEY': 'dummy_key'})
    def test_generate_ai_response_json(self, mock_client_class):
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.models.generate_content.return_value.text = "```json\n{\"test\": 1}\n```"
        
        result = generate_ai_response("test prompt", output_format="json")
        
        # Check if JSON cleanup worked
        self.assertEqual(result, "{\"test\": 1}")
        
        # Check if prompt was enhanced
        _, kwargs = mock_client.models.generate_content.call_args
        self.assertIn("ONLY valid JSON", kwargs['contents'])

    @patch('aria.genai.Client')
    @patch.dict(os.environ, {'GEMINI_API_KEY': 'dummy_key'})
    def test_summarize_text_json(self, mock_client_class):
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.models.generate_content.return_value.text = "{\"summary\": \"ok\"}"
        
        result = summarize_text("some text", output_format="json")
        self.assertEqual(result, "{\"summary\": \"ok\"}")
        
        _, kwargs = mock_client.models.generate_content.call_args
        self.assertIn("valid JSON with keys", kwargs['contents'])

    def test_resolve_prompt_with_tabs(self):
        mock_navigator = MagicMock()
        mock_navigator.get_tabs_content.return_value = [
            {'identifier': '0', 'title': 'Page 0', 'url': 'http://0.com', 'content': 'Content 0'},
            {'identifier': '1', 'title': 'Page 1', 'url': 'http://1.com', 'content': 'Content 1'}
        ]
        
        prompt = "Compare tab 0 and tab 1"
        refined_prompt, context = AriaNavigator.resolve_prompt(mock_navigator, prompt)
        
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

    def test_resolve_prompt_with_quoted_tabs(self):
        mock_navigator = MagicMock()
        mock_navigator.get_tabs_content.return_value = [
            {'identifier': 'Google Search', 'title': 'Google', 'url': 'http://google.com', 'content': 'Google Content'}
        ]
        
        prompt = "Look at tab \"Google Search\" and summarize"
        refined_prompt, context = AriaNavigator.resolve_prompt(mock_navigator, prompt)
        
        self.assertIn("Google Content", context)
        mock_navigator.get_tabs_content.assert_called_with(['Google Search'])

    def test_resolve_prompt_with_named_tab(self):
        mock_navigator = MagicMock()
        mock_navigator.get_tabs_content.return_value = [
            {'identifier': 'google', 'title': 'Google', 'url': 'http://google.com', 'content': 'Google Content'}
        ]
        
        prompt = "Look at tab google and summarize"
        refined_prompt, context = AriaNavigator.resolve_prompt(mock_navigator, prompt)
        
        self.assertIn("Google Content", context)
        mock_navigator.get_tabs_content.assert_called_with(['google'])

    def test_resolve_prompt_multiple_mixed(self):
        mock_navigator = MagicMock()
        mock_navigator.get_tabs_content.return_value = []
        
        prompt = "Compare tab 0, tab \"My Page\" and tab news."
        AriaNavigator.resolve_prompt(mock_navigator, prompt)
        
        call_args = set(mock_navigator.get_tabs_content.call_args[0][0])
        self.assertEqual(call_args, {'0', 'My Page', 'news'})

    def test_resolve_prompt_with_tag(self):
        mock_navigator = MagicMock()
        mock_navigator.get_tabs_by_tag.return_value = ['handle_news_1']
        mock_navigator.get_tabs_content.return_value = [
            {'identifier': 'handle_news_1', 'title': 'News', 'url': 'http://news.com', 'content': 'News Content'}
        ]
        
        prompt = "Look at tag:news and summarize"
        refined_prompt, context = AriaNavigator.resolve_prompt(mock_navigator, prompt)
        
        self.assertIn("News Content", context)
        mock_navigator.get_tabs_by_tag.assert_called_with('news')
        mock_navigator.get_tabs_content.assert_called_with(['handle_news_1'])

    def test_resolve_prompt_no_tabs(self):
        mock_navigator = MagicMock()
        prompt = "Just a regular prompt"
        refined_prompt, context = AriaNavigator.resolve_prompt(mock_navigator, prompt)
        
        self.assertEqual(refined_prompt, prompt)
        self.assertEqual(context, "")
        mock_navigator.get_tabs_content.assert_not_called()

if __name__ == '__main__':
    unittest.main()
