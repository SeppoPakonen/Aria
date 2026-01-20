import unittest
from unittest.mock import MagicMock, patch
import os
import shutil
from report_manager import ReportManager

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

    def test_generate_markdown_report_with_metrics(self):
        title = "Metrics Report"
        content = "Report with metrics."
        metrics = [{"operation": "test_op", "duration_ms": 123.45}]
        
        report_path = self.report_manager.generate_markdown_report(title, content, metrics=metrics)
        
        self.assertTrue(os.path.exists(report_path))
        with open(report_path, "r", encoding="utf-8") as f:
            text = f.read()
            self.assertIn("## Performance Metrics", text)
            self.assertIn("| test_op | 123.45 |", text)

    def test_generate_html_report(self):
        title = "Test HTML Report"
        content = "This is a test summary for HTML."
        sources = ["https://example.com"]
        
        report_path = self.report_manager.generate_html_report(title, content, sources)
        
        self.assertTrue(os.path.exists(report_path))
        self.assertTrue(report_path.endswith(".html"))
        with open(report_path, "r", encoding="utf-8") as f:
            text = f.read()
            self.assertIn("<title>Test HTML Report</title>", text)
            self.assertIn("<h1>Test HTML Report</h1>", text)
            self.assertIn("<li>https://example.com</li>", text)
            self.assertIn("This is a test summary for HTML.", text)
            self.assertIn("class=\"content\"", text)

    def test_generate_html_report_with_metrics(self):
        title = "HTML Metrics Report"
        content = "HTML content with metrics."
        metrics = [{"operation": "html_op", "duration_ms": 456.78}]
        
        report_path = self.report_manager.generate_html_report(title, content, metrics=metrics)
        
        self.assertTrue(os.path.exists(report_path))
        with open(report_path, "r", encoding="utf-8") as f:
            text = f.read()
            self.assertIn("<h3>Performance Metrics</h3>", text)
            self.assertIn("<td>html_op</td>", text)
            self.assertIn("<td>456.78</td>", text)

if __name__ == "__main__":
    unittest.main()
