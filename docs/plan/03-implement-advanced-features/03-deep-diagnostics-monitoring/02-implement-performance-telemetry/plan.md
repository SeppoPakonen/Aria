# Task: Implement Performance Telemetry

## Goal
Track and log execution times for major browser operations to identify bottlenecks and provide performance insights.

## Implementation Plan
1. **Utility for Timing**: Create a utility (e.g., a decorator or context manager) to measure the execution time of functions.
2. **Instrument Navigator**: Apply timing to key `AriaNavigator` methods:
    - `start_session` / `connect_to_session`
    - `navigate`
    - `summarize_page` (once implemented or relevant)
    - `execute_script` (in `script_manager.py`)
3. **Structured Logging**: Log the duration in milliseconds (`duration_ms`) as part of the structured log output.
4. **Report Integration**: Ensure the `ReportManager` can receive and store performance data for inclusion in the final HTML/Markdown report.

## Verification
1. Run commands with `--json-logs` and verify `duration_ms` is present in the logs.
2. Check the generated report to see if performance metrics are included.
