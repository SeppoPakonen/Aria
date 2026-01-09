# Task 02: Implement Markdown Report Export

## Goal
Add a dedicated `export` command to save the current page content or a session summary directly to a Markdown file.

## Proposed Changes

### `src/aria.py`
- Add `aria page export` command.
- This command will take an identifier and a filename/path.
- It will fetch the page content and save it as a Markdown file using `ReportManager`.

## Implementation Steps
1. Add `parser_page_export` to `src/aria.py`.
2. Implement the logic to fetch content and call `report_manager.generate_markdown_report`.
3. Add a test case for `aria page export`.
