# Task: 01: Implement `script new` Command

## Objective

Implement the `aria script new <name>` command to create a new, empty script file in a dedicated scripts directory.

## Rationale

A core feature of `aria` will be the ability to execute pre-written scripts. The `script new` command is the first step in this process, providing users with a standardized way to create script files in the correct location, ready for editing.

## Implementation Details

1.  **Script Storage Directory**:
    *   A dedicated directory for storing user scripts will be created at `~/.aria/scripts`.
    *   This logic can be added to a new module, e.g., `src/script_manager.py`, which will handle all script-related filesystem operations.

2.  **CLI Subcommand (`src/aria.py`)**:
    *   Create a new subparser for the `script` command.
    *   Add a `new` command to the `script` subparser.
    *   The `new` command will take a required `name` argument, which will be the filename for the new script (e.g., `my-automation`).

3.  **Script Manager (`src/script_manager.py`)**:
    *   Create a new file `src/script_manager.py`.
    *   Inside, create a `ScriptManager` class.
    *   The `ScriptManager` will have a method `create_script(self, name: str) -> str | None`.
    *   This method will:
        1.  Construct the full path for the new script (e.g., `~/.aria/scripts/my-automation.py`). A `.py` extension will be assumed for now.
        2.  Check if a file with that name already exists to prevent overwriting.
        3.  Create an empty file at that path.
        4.  Return the full path of the created file, or `None` if it failed.

4.  **Command Logic (`src/aria.py`)**:
    *   When `aria script new <name>` is invoked:
        1.  Instantiate `ScriptManager`.
        2.  Call `script_manager.create_script(name)`.
        3.  Print a confirmation message with the path to the new script if successful.

## Acceptance Criteria

*   Running `aria script new my-first-script` should create a new empty file at `~/.aria/scripts/my-first-script.py`.
*   The command should print the full path of the newly created script.
*   If a script with the same name already exists, the command should print an error message and not overwrite the existing file.
*   The `~/.aria/scripts` directory should be created if it doesn't exist.
