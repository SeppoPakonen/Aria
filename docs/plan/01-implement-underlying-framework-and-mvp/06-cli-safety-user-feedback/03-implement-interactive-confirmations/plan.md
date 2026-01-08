# Plan: 03-implement-interactive-confirmations

## Objective
Implement interactive confirmation prompts for sensitive or state-changing operations to prevent accidental data loss or unintended side effects.

## Proposed Changes

### 1. Update `src/safety_manager.py`
- Add a static method `confirm(prompt, default=False)` to handle interactive (y/N) prompts consistently.

### 2. Update `src/navigator.py`
- Modify `start_session` to ask for confirmation if a session is already active.

### 3. Update `src/aria.py`
- Update `script remove` to use the new `SafetyManager.confirm` method.

## Verification Plan
1. Run `aria open http://example.com`.
2. While session is active, run `aria open http://google.com`.
    - Verify it asks to restart.
    - Verify 'n' aborts.
    - Verify 'y' closes old session and starts new one.
3. Run `aria script remove <name>` and verify it uses the standardized prompt.
