# Task: 04: Implement `aria close`

## Objective

Implement a new `aria close` command that gracefully terminates the currently active browser instance managed by `AriaNavigator`.

## Rationale

The `aria open` command starts a new browser session. To provide a complete lifecycle for browser management, a corresponding `close` command is necessary. This allows users to explicitly end the session, which is crucial for resource management and scripting.

## Implementation Details

1.  **CLI Argument Parsing (`src/aria.py`)**:
    *   Add a new `close` sub-command to the `argparse` setup.
    *   This command will not require any arguments initially.

2.  **Navigator Method (`src/navigator.py`)**:
    *   Create a new public method `close(self)` within the `AriaNavigator` class.
    *   This method will call `self.driver.quit()` to close the browser and terminate the WebDriver session.
    *   Add a check to ensure `self.driver` is not `None` before attempting to close it, preventing errors if no browser is running.

3.  **Command Dispatching (`src/aria.py`)**:
    *   Update the main execution block in `aria.py` to call `navigator.close()` when the `close` command is invoked.

## Acceptance Criteria

*   Running `aria close` when a browser is open should cause the browser window to close.
*   Running `aria close` when no browser is open should not produce an error and should perhaps inform the user that no active browser was found.
*   The command should execute without errors.
