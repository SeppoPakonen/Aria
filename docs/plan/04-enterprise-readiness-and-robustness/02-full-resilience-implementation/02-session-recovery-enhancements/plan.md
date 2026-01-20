# Task: Session Recovery Enhancements

## Outcome
Improved robustness in handling stale browser sessions and cleaning up orphaned WebDriver processes.

## Requirements
- Robust detection of unhealthy sessions (beyond just PID check).
- Automated cleanup of orphaned processes on startup or on failure.
- A `cleanup` command in `aria settings` (optional but good).
- Integration with `AriaNavigator.connect_to_session` to handle more failure modes.

## Implementation Steps
1. **Enhance `AriaNavigator.connect_to_session`**:
   - Add a timeout to the health check command (`driver.current_url`).
   - If a session is unhealthy, ensure the PID is killed before deleting the session file.
2. **Implement `AriaNavigator.cleanup_orphaned_sessions()`**:
   - Iterate through all session files in `~/.aria/`.
   - For each, check health and PID.
   - Kill processes that are running but unhealthy or not associated with an active Aria command.
3. **Add `aria settings cleanup` command**:
   - Expose the cleanup logic to the user.
4. **Tests**:
   - Create `tests/test_session_recovery.py` to simulate stale sessions and verify cleanup.

## Acceptance Criteria
- If a WebDriver process is killed manually, `aria` detects it and removes the stale session file on next attempt.
- If a WebDriver process hangs, `aria` eventually times out trying to connect and cleans it up.
- `aria settings cleanup` removes all stale session files and kills orphaned processes.
