# Task: 01-enhance-logging-structured-data

## Problem
Current logging in Aria is plain text, which is easy for humans to read but difficult for tools to parse or for extracting specific metrics/context reliably. As Aria grows more complex, we need a way to attach structured context to log messages.

## Proposed Solution
- Update `src/logger.py` to support structured logging.
- Use a custom JSON formatter for the file handler (optional, but recommended for advanced diagnostics).
- Update the `get_logger` or create a wrapper that allows passing structured context (extra fields).
- Refactor key log statements in `navigator.py` and `aria.py` to include structured context (e.g., `session_id`, `tab_id`, `duration`).

## Implementation Plan
1.  **Enhance `src/logger.py`**:
    - Add a `JsonFormatter` class or use an existing library (if appropriate, but we prefer minimal dependencies, so a simple custom formatter is better).
    - Update `setup_logging` to allow switching between human-readable and JSON format for the file handler.
2.  **Refactor Logger Usage**:
    - Update `AriaNavigator` to include contextual information in its logs.
    - Ensure that errors include relevant state (URL, active tab, etc.) in the log context.
3.  **Verification**:
    - Check the `aria.log` file to ensure logs are correctly formatted.
    - Verify that adding "extra" context works as expected.

## Verification Plan
- Run `aria` with various commands.
- Inspect `~/.aria/aria.log`.
- Add a test case to `tests/` that verifies logging output if feasible, or manually verify.
