# Plan: 02-enhance-command-feedback

## Objective
Ensure all Aria commands provide clear, consistent, and helpful feedback to the user. This includes fixing bugs that cause ungraceful crashes and standardizing output formats.

## Proposed Changes

### 1. Fix WebDriver Session Persistence Bug
- Investigating `navigator.py`: The access to `self.driver.command_executor._url` is failing in some Selenium versions.
- Change: Use a more robust way to get the remote URL or handle the attribute error.

### 2. Standardize CLI Output
- Update `src/aria.py` to ensure every command execution path ends with a clear message.
- For example, `aria close` should explicitly say "Aria session closed." (it does, but ensure others do too).
- `aria page new` should say "Navigated to [URL]".

### 3. Improve Error Messages
- Instead of raw exception tracebacks, show user-friendly error messages where possible.

## Verification Plan
1. Run various `aria` commands and verify they all provide clear feedback.
2. Specifically verify `aria open` no longer crashes with the `_url` error.
