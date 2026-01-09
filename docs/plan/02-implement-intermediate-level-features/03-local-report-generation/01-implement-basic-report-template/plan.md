# Task 01: Implement Basic Report Template

## Goal
Create a mechanism to generate local reports using a basic Markdown template.

## Proposed Changes

### `src/report_manager.py` (New File)
- Create a `ReportManager` class to handle template loading and report generation.
- Use simple string formatting or a lightweight template engine (if already in use, otherwise stick to simple formatting first) for basic Markdown reports.

### `src/aria.py`
- Add a new command `aria report generate` (or similar) or integrate it into `summarize`.
- For now, let's add `aria report` as a top-level command for managing reports.

## Implementation Steps
1. Create `src/report_manager.py` with basic Markdown template logic.
2. Define a standard report structure:
    - Title
    - Date/Time
    - Source (URLs/Tabs)
    - Content (The AI generated summary or data)
3. Add `aria report generate` command to `src/aria.py`.
4. Verify with a test.
