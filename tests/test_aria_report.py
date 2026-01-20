import unittest
from unittest.mock import MagicMock, patch
import sys
import os
from io import StringIO

# Add src to path

from aria import main

class TestAriaReport(unittest.TestCase):
    @patch('aria.AriaNavigator')
    @patch('aria.ReportManager')
    @patch('aria.generate_ai_response')
    def test_report_generate_command(self, mock_ai, mock_report_manager, mock_nav):
        # Mocking
        mock_ai.return_value = "AI generated report content."
        mock_rm_inst = mock_report_manager.return_value
        mock_rm_inst.generate_markdown_report.return_value = "/path/to/report.md"
        mock_rm_inst.reports_dir = "/tmp/reports"
        
        mock_nav_inst = mock_nav.return_value
        mock_nav_inst.resolve_prompt.return_value = ("Some prompt", "")
        
        # Test command: aria report generate "Some prompt" --title "My Title"
        with patch('sys.argv', ['aria', 'report', 'generate', 'Some prompt', '--title', 'My Title']):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                main()
                output = fake_out.getvalue()
                self.assertIn("Report generated: /path/to/report.md", output)
                mock_rm_inst.generate_markdown_report.assert_called_once()
                args, kwargs = mock_rm_inst.generate_markdown_report.call_args
                self.assertEqual(args[0], "My Title")
                self.assertEqual(args[1], "AI generated report content.")

    @patch('aria.AriaNavigator')
    @patch('aria.ReportManager')
    @patch('aria.summarize_text')
    def test_page_summarize_with_report(self, mock_summarize, mock_report_manager, mock_nav):
        # Mocking
        mock_summarize.return_value = "Summary text."
        mock_nav_inst = mock_nav.return_value
        mock_nav_inst.get_page_content.return_value = "Page content."
        mock_nav_inst.get_current_url.return_value = "https://example.com"
        
        mock_rm_inst = mock_report_manager.return_value
        mock_rm_inst.generate_markdown_report.return_value = "/path/to/summary.md"
        
        # Test command: aria page 0 summarize --report
        with patch('sys.argv', ['aria', 'page', '0', 'summarize', '--report']):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                main()
                output = fake_out.getvalue()
                self.assertIn("Report generated: /path/to/summary.md", output)
                mock_rm_inst.generate_markdown_report.assert_called_once()

    @patch('aria.AriaNavigator')
    @patch('aria.ReportManager')
    def test_page_export_command(self, mock_report_manager, mock_nav):
        # Mocking
        mock_nav_inst = mock_nav.return_value
        mock_nav_inst.get_page_content.return_value = "Full page content."
        mock_nav_inst.get_current_url.return_value = "https://example.com"
        mock_nav_inst._driver.title = "Example Title"
        
        mock_rm_inst = mock_report_manager.return_value
        mock_rm_inst.generate_markdown_report.return_value = "/path/to/export.md"
        
        # Test command: aria page export 0
        with patch('sys.argv', ['aria', 'page', '0', 'export']):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                main()
                output = fake_out.getvalue()
                self.assertIn("Page exported to: /path/to/export.md", output)
                mock_rm_inst.generate_markdown_report.assert_called_once()

    @patch('aria.AriaNavigator')
    @patch('aria.ReportManager')
    @patch('aria.generate_ai_response')
    def test_report_generate_html_command(self, mock_ai, mock_report_manager, mock_nav):
        # Mocking
        mock_ai.return_value = "AI generated HTML content."
        mock_rm_inst = mock_report_manager.return_value
        mock_rm_inst.generate_html_report.return_value = "/path/to/report.html"
        
        mock_nav_inst = mock_nav.return_value
        mock_nav_inst.resolve_prompt.return_value = ("Some prompt", "")
        
        # Test command: aria report generate "Some prompt" --format html
        with patch('sys.argv', ['aria', 'report', 'generate', 'Some prompt', '--format', 'html']):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                main()
                output = fake_out.getvalue()
                self.assertIn("Report generated: /path/to/report.html", output)
                mock_rm_inst.generate_html_report.assert_called_once()

if __name__ == "__main__":
    unittest.main()
