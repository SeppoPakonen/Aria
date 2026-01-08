# Task: 03: Implement `script edit` Command

## Objective

Implement the `aria script edit <name>` command to open an existing script in the system's default text editor.

## Rationale

After creating a script, the user needs to write code in it. The `edit` command provides a convenient shortcut to open the script file directly from the CLI, improving the developer workflow.

## Implementation Details

1.  **CLI Subcommand (`src/aria.py`)**:
    *   Add an `edit` command to the `script` subparser.
    *   The command will take a required `name` argument (the script name without extension).

2.  **`ScriptManager` Method (`src/script_manager.py`)**:
    *   Implement a method `get_script_path(self, name: str) -> str | None`.
    *   This method will:
        1.  Construct the full path (e.g., `~/.aria/scripts/name.py`).
        2.  Check if the file exists.
        3.  Return the path if it exists, otherwise return `None`.

3.  **Command Logic (`src/aria.py`)**:
    *   When `aria script edit <name>` is invoked:
        1.  Call `script_manager.get_script_path(name)`.
        2.  If the path exists:
            *   On Windows, use `os.startfile(path)`.
            *   On other systems (for future-proofing), use `subprocess.run` with the appropriate opener (e.g., `open` on macOS, `xdg-open` on Linux).
        3.  If the path does not exist, print an error message.

## Acceptance Criteria

*   Running `aria script edit my-script` (where `my-script.py` exists) should open the file in the default system editor.
*   If the script does not exist, it should print an error message: "Error: Script 'my-script' not found."
*   The command should handle script names both with and without the `.py` extension if possible, or strictly enforce one (simplest is to enforce name without extension and add it).
