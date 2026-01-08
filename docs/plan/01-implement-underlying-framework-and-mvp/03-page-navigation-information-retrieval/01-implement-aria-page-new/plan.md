# Task: 01: Implement `aria page new`

## Objective

Implement the `aria page new <URL>` command to navigate the active browser session to a new URL.

## Rationale

This command is the foundation of the `page` subcommand, providing the primary mechanism for users to direct the browser to a specific web page. It builds upon the existing browser lifecycle management by adding a clear and intuitive command for page navigation.

## Implementation Details

1.  **CLI Subcommand (`src/aria.py`)**:
    *   Create a new subparser for the `page` command.
    *   Add a `new` command to the `page` subparser.
    *   The `new` command will take a required `url` argument.

2.  **Command Logic (`src/aria.py`)**:
    *   When `aria page new <URL>` is invoked, the main function will:
        1.  Instantiate `AriaNavigator`.
        2.  Call the existing `navigate(url)` method with the provided URL.

3.  **`AriaNavigator` (`src/navigator.py`)**:
    *   The existing `navigate(self, url)` method already contains the necessary logic to navigate an active session. No changes are expected to be needed in `navigator.py` for this task. It will connect to the session if `self.driver` is `None`.

## Acceptance Criteria

*   Running `aria page new http://example.com` when a browser session is active should navigate the browser to `http://example.com`.
*   Running `aria page new http://example.com` when no session is active should result in the "No active session" message from `AriaNavigator`.
*   The command should gracefully handle navigation errors (e.g., invalid URL), relying on the error handling already implemented in `AriaNavigator.navigate`.
