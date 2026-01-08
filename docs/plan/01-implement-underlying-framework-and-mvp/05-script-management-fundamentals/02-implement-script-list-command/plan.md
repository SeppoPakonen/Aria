# Task: 02: Implement `script list` Command

## Objective

Implement the `aria script list` command to display all available scripts in the user's script directory.

## Rationale

After creating scripts, users need a way to see all the scripts they have available to run. The `list` command provides this essential visibility, making it easy to manage and execute scripts.

## Implementation Details

1.  **CLI Subcommand (`src/aria.py`)**:
    *   Add a `list` command to the `script` subparser.
    *   This command will not take any arguments.

2.  **`ScriptManager` Method (`src/script_manager.py`)**:
    *   Create a new public method `list_scripts(self) -> list[str]`.
    *   This method will:
        1.  Read the contents of the `~/.aria/scripts` directory.
        2.  Filter the contents to include only files (not subdirectories).
        3.  Return a list of the filenames.

3.  **Command Logic (`src/aria.py`)**:
    *   When `aria script list` is invoked:
        1.  Instantiate `ScriptManager`.
        2.  Call `script_manager.list_scripts()`.
        3.  If the list is not empty, print each script name to the console.
        4.  If the list is empty, print a message indicating that no scripts were found.

## Acceptance Criteria

*   Running `aria script list` should print a list of all `.py` files in the `~/.aria/scripts` directory.
*   If there are no scripts, it should print a "No scripts found" message.
*   The command should not list subdirectories.
