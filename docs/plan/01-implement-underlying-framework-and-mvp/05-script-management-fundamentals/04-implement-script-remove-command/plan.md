# Task: 04: Implement `script remove` Command

## Objective

Implement the `aria script remove <name>` command to delete an existing script from the script directory.

## Rationale

Users need a way to clean up scripts they no longer need. The `remove` command provides this functionality directly from the CLI.

## Implementation Details

1.  **CLI Subcommand (`src/aria.py`)**:
    *   Add a `remove` command to the `script` subparser.
    *   The command will take a required `name` argument.
    *   Add an optional `--force` or similar if we want to bypass confirmation (optional for now).

2.  **`ScriptManager` Method (`src/script_manager.py`)**:
    *   Implement a method `remove_script(self, name: str) -> bool`.
    *   This method will:
        1.  Construct the full path.
        2.  Check if the file exists.
        3.  Delete the file using `os.remove()`.
        4.  Return `True` if successful, `False` otherwise.

3.  **Command Logic (`src/aria.py`)**:
    *   When `aria script remove <name>` is invoked:
        1.  Ask for confirmation (e.g., "Are you sure you want to remove script 'name'? [y/N]").
        2.  If confirmed, call `script_manager.remove_script(name)`.
        3.  Print a success message or an error message if the script wasn't found or couldn't be deleted.

## Acceptance Criteria

*   Running `aria script remove my-script` should delete the `my-script.py` file after confirmation.
*   If the script does not exist, it should print an error message.
*   If the user cancels confirmation, the file should not be deleted.
