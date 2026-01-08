# Task: 01: Implement Scope Handling for `open`

## Objective

Introduce a `--scope` argument to the `aria open` command to specify the context from which the target URL or resource is drawn.

## Rationale

To make `aria` a more powerful tool, it needs to be able to open more than just explicit URLs. By introducing scopes, we can create a system where `open` can target web URLs, browser bookmarks, local files, etc. This task lays the groundwork for that system.

## Implementation Details

1.  **CLI Argument (`src/aria.py`)**:
    *   Add a `--scope` argument to the `open` command.
    *   It will accept a choice of strings: `web`, `bookmarks`, `local`.
    *   The default value will be `web`.

2.  **Command Logic (`src/aria.py`)**:
    *   The logic for the `open` command will be updated to handle the `scope` argument.
    *   If `scope` is `web` (the default), the command will behave as it currently does, treating the argument as a URL.
    *   If `scope` is `bookmarks` or `local`, the command will print a "not yet implemented" message. This provides a placeholder for future functionality without breaking the command.

3.  **No `AriaNavigator` Changes**:
    *   No changes are required in `AriaNavigator` for this task, as we are only modifying the CLI logic that precedes the call to `navigator.start_session()` and `navigator.navigate()`.

## Acceptance Criteria

*   `aria open http://example.com --scope web` should open the URL in a browser.
*   `aria open http://example.com` (with `--scope` omitted) should also open the URL, defaulting to the `web` scope.
*   `aria open "My Bookmark" --scope bookmarks` should print a message indicating that this feature is not yet implemented.
*   `aria open "path/to/file.html" --scope local` should print a message indicating that this feature is not yet implemented.
*   Providing an invalid scope (e.g., `--scope invalid`) should result in an error from `argparse`.
