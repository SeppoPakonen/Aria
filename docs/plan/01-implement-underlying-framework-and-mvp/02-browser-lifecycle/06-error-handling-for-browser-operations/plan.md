# Task: 06: Error Handling for Browser Operations

## Objective

Enhance the robustness of `AriaNavigator` by implementing comprehensive error handling for common browser and WebDriver operations.

## Rationale

Interacting with a web browser is prone to errors. The browser might crash, network issues can prevent page loading, and WebDriver might lose connection. Currently, such issues would cause the `aria` CLI to crash with an unhandled exception. Proper error handling will make the tool more reliable and provide better feedback to the user.

## Implementation Details

1.  **Identify Critical Operations**: The following methods in `AriaNavigator` (`src/navigator.py`) are critical and need error handling:
    *   `start_session`: When `webdriver.Chrome()` is called.
    *   `connect_to_session`: When `webdriver.Remote()` is called and when we check if the session is valid.
    *   `navigate`: When `self.driver.get(url)` is called.
    *   `close_session`: When `driver.quit()` is called.

2.  **Implement `try...except` Blocks**:
    *   Wrap the critical operations identified above in `try...except` blocks.
    *   Catch specific Selenium exceptions where possible (e.g., `WebDriverException`).
    *   Also, include a general `Exception` catch as a fallback.

3.  **Provide User-Friendly Messages**:
    *   In each `except` block, print a clear, user-friendly error message to the console.
    *   For example, if `navigate` fails, instead of a stack trace, the user should see something like: "Error: Failed to navigate to {url}. Please check the URL and your network connection."

4.  **Graceful Failure**:
    *   When an error occurs, the application should fail gracefully. For example, if `connect_to_session` fails because the session is no longer valid, it should clean up the stale session file. This is already implemented. We should review other methods for similar graceful failure patterns.

## Acceptance Criteria

*   Invalid URL passed to `aria open` should result in a user-friendly error message, not a crash.
*   Attempting to `aria close` a session that has been externally terminated (e.g., user manually closed the browser) should be handled gracefully.
*   Loss of network connectivity during a `navigate` operation should result in a clear error message.
