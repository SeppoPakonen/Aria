# Task: 01-enhance-logging-structured-data [DONE]

## Problem
Current logging in Aria is plain text, which is easy for humans to read but difficult for tools to parse or for extracting specific metrics/context reliably. As Aria grows more complex, we need a way to attach structured context to log messages.

## Implementation Summary
- **Enhanced `src/logger.py`**: Added `JsonFormatter` and updated `setup_logging` to support `--json-logs`.
- **Structured Context**: Enabled passing `extra` context to log statements.
- **Refactored Usage**: Key methods in `AriaNavigator` and `ScriptManager` now include structured context like `session_id`, `url`, and `duration_ms`.

## Verification
- Checked `aria.log` for JSON formatting when `--json-logs` is used.
- Verified `duration_ms` is present in logs for timed operations.
