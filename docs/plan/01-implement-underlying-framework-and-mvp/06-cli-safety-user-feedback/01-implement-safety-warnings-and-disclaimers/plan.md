# Plan: 01-implement-safety-warnings-and-disclaimers

## Objective
Implement a safety disclaimer that users must acknowledge before using certain Aria features (like opening a browser or running scripts) for the first time.

## Proposed Changes

### 1. Create `src/safety_manager.py`
- Define a `SafetyManager` class.
- Store safety-related state in `~/.aria/safety.json`.
- Method `check_disclaimer()`:
    - If disclaimer not accepted, display it and prompt for acceptance.
    - If accepted, proceed silently.
    - If rejected, exit the application.
- Method `accept_disclaimer()`: Update state to record acceptance.

### 2. Update `src/aria.py`
- Integrate `SafetyManager`.
- Call `safety_manager.ensure_disclaimer_accepted()` before executing `open` or `script run` commands.

### 3. Add Global Safety Flags (Optional/Future)
- Add a `--skip-disclaimer` flag for CI/CD or advanced users (maybe not yet for MVP).

## Verification Plan
1. Run `aria open http://google.com`.
    - Verify disclaimer is shown on first run.
    - Verify user can accept/reject.
    - Verify rejecting exits.
    - Verify accepting allows the command to proceed.
2. Run `aria open http://google.com` again.
    - Verify disclaimer is NOT shown.
3. Verify `aria script run` also triggers the disclaimer if not already accepted.
