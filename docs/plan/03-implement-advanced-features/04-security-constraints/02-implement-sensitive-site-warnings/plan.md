# Task: Implement Sensitive Site Warnings

## Outcome
Aria will automatically detect when the user is navigating to a potentially sensitive website (e.g., banking, healthcare, login pages) and issue a warning, requiring confirmation before proceeding if in interactive mode, or logging a warning if in automated mode.

## Requirements
- Define a list of "sensitive site" patterns (URLs or keywords).
- Hook into the navigation flow in `AriaNavigator`.
- Issue a warning message when a match is found.
- Implement a way to bypass or acknowledge the warning (e.g., `--force` flag or interactive prompt).
- Allow users to configure additional sensitive patterns.

## Implementation Sketch
1. Update `SafetyManager` to include a list of sensitive site patterns.
2. Add a `check_url_safety(url)` method to `SafetyManager`.
3. Modify `AriaNavigator.navigate()` to call `safety_manager.check_url_safety()`.
4. If a site is sensitive:
    - In interactive mode: Prompt for confirmation.
    - In non-interactive mode (or if `--force` is used): Log a warning but proceed.
5. Update `aria.py` to handle the confirmation logic or pass the force flag.

## Acceptance Criteria
- Navigating to a known sensitive site (e.g., `bank.com`, `login.microsoft.com`) triggers a warning.
- The user can proceed after acknowledging the warning.
- Navigation to non-sensitive sites remains uninterrupted.
- The warning mechanism respects the `--force` flag if implemented, or a similar bypass.
