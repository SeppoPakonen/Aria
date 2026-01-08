# Task: 03: Implement `aria page goto`

## Objective

Implement the `aria page goto <identifier>` command to switch focus to a specific tab (page) within the current browser session, using either its title or a 1-based index.

## Rationale

When multiple tabs are open, users need a way to switch between them programmatically. The `goto` command provides this essential functionality, allowing for more complex automation scripts that involve interacting with different pages.

## Implementation Details

1.  **CLI Subcommand (`src/aria.py`)**:
    *   Add a `goto` command to the `page` subparser.
    *   It will take one argument, `identifier`, which can be a 1-based index (an integer) or a string (the page title).

2.  **`AriaNavigator` Method (`src/navigator.py`)**:
    *   Create a new public method `goto_tab(self, identifier: str | int) -> bool`.
    *   This method will:
        1.  Connect to the active session. If no session is found, return `False`.
        2.  Get the list of all window handles.
        3.  If the `identifier` is an integer, it's a 1-based index. Switch to the window at `handles[identifier - 1]`. Handle `IndexError` if the index is out of bounds.
        4.  If the `identifier` is a string, iterate through the handles. For each handle, switch to it and check if `self.driver.title` matches the `identifier`. If a match is found, stop.
        5.  If the tab is successfully found and switched to, return `True`.
        6.  If no matching tab is found, print an error and return `False`.

3.  **Command Logic (`src/aria.py`)**:
    *   When `aria page goto <identifier>` is invoked:
        1.  Instantiate `AriaNavigator`.
        2.  Try to convert the `identifier` to an integer. If it works, pass the integer to `navigator.goto_tab()`.
        3.  If it's a string, pass the string to `navigator.goto_tab()`.
        4.  Print a confirmation message if the switch is successful, or an error message if it fails.

## Acceptance Criteria

*   `aria page goto 2` should switch focus to the second tab.
*   `aria page goto "Example Domain"` should switch focus to the tab with that exact title.
*   `aria page goto 99` (with fewer than 99 tabs open) should result in an "Invalid tab index" error.
*   `aria page goto "Non-existent Title"` should result in a "Tab not found" error.
*   Running `goto` with no active session should result in the standard "No active session" message.
