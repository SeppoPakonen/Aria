# Task: 05: Active Browser State Management

## Objective

Implement a mechanism to manage the state of the active browser session, allowing different `aria` command invocations to interact with the same browser instance.

## Rationale

The current implementation of `aria open` creates a new browser instance, but the reference to this instance is lost once the command finishes. This makes it impossible for other commands, like `aria close`, to control the same browser. A state management system is needed to persist the browser session details between commands.

## Implementation Details

1.  **Session State File**:
    *   We will use a file to store the session details of the active browser. A simple approach is to store the session ID and the URL of the WebDriver service.
    *   The file will be stored in a temporary directory. We can name it `aria_session.json`.

2.  **`AriaNavigator` Modifications (`src/navigator.py`)**:
    *   The `AriaNavigator` class will be refactored. Instead of always creating a new driver instance, it will have methods to start a new session or connect to an existing one.
    *   `start_session(self, headless=False)`: This method will start a new WebDriver session and save the `session_id` and `command_executor._url` to `aria_session.json`.
    *   `connect_to_session(self)`: This method will read `aria_session.json` and use the `session_id` and `command_executor._url` to reconnect to the existing browser session.
    *   `close_session(self)`: This method will close the browser, terminate the WebDriver session, and delete `aria_session.json`.

3.  **Command Modifications (`src/aria.py`)**:
    *   **`open` command**:
        *   It will call `AriaNavigator.start_session()`.
        *   If a session is already active, it should inform the user.
    *   **`close` command**:
        *   It will call `AriaNavigator.close_session()`.
        *   If no session is active, it should inform the user.

## Acceptance Criteria

*   Running `aria open <URL>` should start a browser and create an `aria_session.json` file.
*   Running `aria open <URL>` again while a session is active should result in an error message.
*   Running `aria close` should close the browser and delete the `aria_session.json` file.
*   Running `aria close` when no session is active should result in a message and no error.
