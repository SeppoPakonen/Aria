import unittest
from unittest.mock import MagicMock, patch
import os
import shutil
from src.report_manager import ReportManager

class TestReportManager(unittest.TestCase):
    def setUp(self):
        self.test_reports_dir = "test_reports"
        self.report_manager = ReportManager(reports_dir=self.test_reports_dir)

    def tearDown(self):
        if os.path.exists(self.test_reports_dir):
            shutil.rmtree(self.test_reports_dir)

    def test_generate_markdown_report(self):
        title = "Test Report"
        content = "This is a test summary."
        sources = ["https://example.com", "https://google.com"]
        
        report_path = self.report_manager.generate_markdown_report(title, content, sources)
        
        self.assertTrue(os.path.exists(report_path))
        with open(report_path, "r", encoding="utf-8") as f:
            text = f.read()
            self.assertIn("# Test Report", text)
            self.assertIn("## Sources", text)
            self.assertIn("- https://example.com", text)
            self.assertIn("## Content", text)
            self.assertIn("This is a test summary.", text)

if __name__ == "__main__":
    unittest.main()
