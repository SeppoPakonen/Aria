# Task: 02: Implement `aria page list`

## Objective

Implement the `aria page list` command to display all open tabs (pages) in the current browser session, showing their title and URL.

## Rationale

After opening a browser and navigating to pages, users need a way to see what pages are currently open. The `list` command provides this visibility, making it easier to manage multiple tabs and understand the state of the browser session.

## Implementation Details

1.  **CLI Subcommand (`src/aria.py`)**:
    *   Add a `list` command to the `page` subparser.
    *   This command will not take any arguments.

2.  **`AriaNavigator` Method (`src/navigator.py`)**:
    *   Create a new public method `list_tabs(self) -> list[dict]`.
    *   This method will:
        1.  Connect to the active session if `self.driver` is not already set.
        2.  If no session is found, return an empty list.
        3.  Iterate through `self.driver.window_handles`.
        4.  For each handle, switch to that tab (`self.driver.switch_to.window(handle)`).
        5.  Get the tab's `title` (`self.driver.title`) and `url` (`self.driver.current_url`).
        6.  Store this information in a list of dictionaries, e.g., `[{'title': 'Page Title', 'url': 'http://...'}]`.
        7.  Return the list.

3.  **Command Logic (`src/aria.py`)**:
    *   When `aria page list` is invoked:
        1.  Instantiate `AriaNavigator`.
        2.  Call `navigator.list_tabs()`.
        3.  Format and print the returned list to the console in a user-friendly way (e.g., as a simple table or a numbered list).

## Acceptance Criteria

*   Running `aria page list` with an active session should print a list of all open tabs with their titles and URLs.
*   If only one tab is open, it should list that single tab.
*   If multiple tabs are open, it should list all of them.
*   Running `aria page list` with no active session should print a message indicating that no session is active, and not raise an error.
