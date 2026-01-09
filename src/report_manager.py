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

    def generate_html_report(self, title, content, sources=None):
        """
        Generates a basic HTML report.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        filename_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        sources_html = ""
        if sources:
            sources_html = "<h3>Sources</h3><ul>"
            for source in sources:
                sources_html += f"<li>{source}</li>"
            sources_html += "</ul>"
            
        html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 40px 20px;
            background-color: #f9f9f9;
        }}
        .report-container {{
            background-color: #fff;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }}
        .metadata {{
            color: #7f8c8d;
            font-size: 0.9em;
            margin-bottom: 30px;
        }}
        .sources {{
            margin-bottom: 30px;
            padding: 15px;
            background-color: #ecf0f1;
            border-radius: 4px;
        }}
        .content {{
            white-space: pre-wrap;
            background-color: #fff;
            padding: 20px;
            border: 1px solid #eee;
            border-radius: 4px;
        }}
    </style>
</head>
<body>
    <div class="report-container">
        <h1>{title}</h1>
        <p class="metadata">Generated on: {timestamp}</p>
        <div class="sources">
            {sources_html}
        </div>
        <div class="content">{content}</div>
    </div>
</body>
</html>"""
        
        safe_title = "".join(c for c in title if c.isalnum() or c in (" ", "_")).rstrip().replace(" ", "_")
        filename = f"report_{safe_title}_{filename_timestamp}.html"
        file_path = os.path.join(self.reports_dir, filename)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_template)
        
        return file_path
