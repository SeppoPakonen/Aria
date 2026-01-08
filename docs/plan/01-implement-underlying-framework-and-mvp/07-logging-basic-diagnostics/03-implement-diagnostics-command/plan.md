# Plan: 03-implement-diagnostics-command

## Objective
Implement a `diag` command to provide users with troubleshooting information about their Aria installation and environment.

## Proposed Changes

### 1. Update `src/aria.py`
- Add a new subcommand `diag`.
- Implementation of `diag`:
    - Print Aria version (maybe define it in a constant).
    - Print Python version and path.
    - Print path to `.aria` directory.
    - Check and report active session status.
    - Print the last 10 lines of `aria.log`.

## Verification Plan
1. Run `aria diag`.
2. Verify all information is correctly displayed.
