# Task: Implement `aria script run <name>`

## Goal
Enable the execution of local scripts stored in `~/.aria/scripts` using the `aria script run` command.

## Proposed Changes

### `src/script_manager.py`
- Add a `run_script(self, name: str)` method.
- This method should:
    - Locate the script file using `get_script_path`.
    - Execute the script as a separate process or by importing it if appropriate. Since these are likely automation scripts that might use the `navigator`, we need to decide how to pass the `navigator` instance or if the script should create its own.
    - For now, let's start by executing it as a subprocess to keep it simple and decoupled.

### `src/aria.py`
- Add a `run` subcommand to the `script` parser.
- The `run` command should take a `name` argument.
- Update the command dispatching logic to call `script_manager.run_script(args.name)`.

## Implementation Details
- Using `subprocess.run([sys.executable, script_path])` is a safe way to run these scripts.
- We might want to provide some environment variables or arguments to the script if we want it to interact with an active Aria session, but for the first iteration, just running the script is enough.

## Verification Plan
1. Create a simple test script using `aria script new test_run`.
2. Edit the script to include a print statement (e.g., `print("Hello from Aria script!")`).
3. Run the script using `aria script run test_run`.
4. Verify that the output of the script is displayed in the terminal.
