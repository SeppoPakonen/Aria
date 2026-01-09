import os
from datetime import datetime

class ReportManager:
    def __init__(self, reports_dir=None):
        if reports_dir is None:
            self.reports_dir = os.path.expanduser("~/.aria/reports")
        else:
            self.reports_dir = reports_dir
        
        if not os.path.exists(self.reports_dir):
            os.makedirs(self.reports_dir)

    def generate_markdown_report(self, title, content, sources=None):
        """
        Generates a basic Markdown report.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        filename_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        report_lines = [
            f"# {title}",
            f"\n**Generated on:** {timestamp}",
        ]
        
        if sources:
            report_lines.append("\n## Sources")
            for source in sources:
                report_lines.append(f"- {source}")
        
        report_lines.append("\n## Content")
        report_lines.append(content)
        
        report_content = "\n".join(report_lines)
        
        safe_title = "".join(c for c in title if c.isalnum() or c in (" ", "_")).rstrip().replace(" ", "_")
        filename = f"report_{safe_title}_{filename_timestamp}.md"
        file_path = os.path.join(self.reports_dir, filename)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(report_content)
        
        return file_path
