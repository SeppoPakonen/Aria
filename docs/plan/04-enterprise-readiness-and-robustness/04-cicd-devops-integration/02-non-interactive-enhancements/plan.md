# Task: Non-interactive Enhancements

## Outcome
All interactive prompts in Aria can be bypassed using flags or environment variables, enabling seamless non-interactive use in CI/CD.

## Requirements
- Ensure `SafetyManager.confirm` respects the `--force` flag.
- Add an environment variable (e.g., `ARIA_NON_INTERACTIVE`) that acts as a global `--force`.
- Update `CredentialManager` and `ScriptManager` to avoid interactive prompts when in non-interactive mode.

## Implementation Steps
1. **Update `src/safety_manager.py`**:
   - Update `confirm` and `ensure_disclaimer_accepted` to check for an environment variable `ARIA_NON_INTERACTIVE`.
2. **Update `src/script_manager.py`**:
   - In `run_script`, if a placeholder is missing and we are in non-interactive mode, raise an error instead of using `getpass`/`input`.
3. **Update `src/aria.py`**:
   - Ensure the `--force` flag is correctly propagated to all managers.
4. **Tests**:
   - Verify that Aria runs without prompting when `--force` or `ARIA_NON_INTERACTIVE=true` is set.

## Acceptance Criteria
- Running a script with missing placeholders fails immediately in non-interactive mode with a clear error.
- `aria open` doesn't prompt for the disclaimer if `ARIA_NON_INTERACTIVE=true`.
