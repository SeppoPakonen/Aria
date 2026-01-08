# Plan: 01-implement-basic-logging-system

## Objective
Implement a centralized logging system for Aria to track operations and errors, storing them in a persistent log file.

## Proposed Changes

### 1. Create `src/logger.py`
- Define a `setup_logging()` function.
- Configure `logging` module to:
    - Write to `~/.aria/aria.log`.
    - Use a format like: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`.
    - Set default level to `INFO`.
    - Provide a way to get a logger instance.

### 2. Update `src/aria.py`
- Call `setup_logging()` at the start of `main()`.

## Verification Plan
1. Run several `aria` commands.
2. Verify that `~/.aria/aria.log` is created and contains relevant entries.
