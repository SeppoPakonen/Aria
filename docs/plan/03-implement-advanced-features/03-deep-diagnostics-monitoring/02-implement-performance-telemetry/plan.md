# Task: Implement Performance Telemetry [DONE]

## Goal
Track and log execution times for major browser operations to identify bottlenecks and provide performance insights.

## Implementation Details
1. **Utility for Timing**: Created a `@time_it` decorator in `src/logger.py` to measure execution time.
2. **Instrument Navigator**: Applied `@time_it` to key `AriaNavigator` and `ScriptManager` methods.
3. **Structured Logging**: Logged `duration_ms` in structured log output.
4. **Report Integration**: Integrated performance metrics into `ReportManager`, including them in generated HTML and Markdown reports.

## Verification
1. Run commands with `--json-logs` and verify `duration_ms` is in `aria.log`.
2. Generate a report (e.g., `aria page summarize --report`) and verify the "Performance Metrics" section is present.
