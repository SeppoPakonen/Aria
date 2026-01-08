# 90-troubleshooting.md

This runbook addresses common issues encountered while using the `aria` CLI and provides diagnostic commands and strategies for resolving them.

## Common Issues and Fixes

### Wrong Tab Selected

*   **Problem**: `aria` commands are affecting the wrong browser tab, or `aria` reports that a specified tab does not exist.
*   **Cause**: This usually happens when relying on `tab_num` in a dynamic environment where tabs have been closed, reordered, or new tabs have opened.
*   **Fix**:
    1.  Always use `aria page list` to get an up-to-date list of `tab_num` and `tab_id`.
    2.  For any scripted or critical operations, **prefer using `tab_id`** as it is a stable identifier for a tab.
    3.  Manually confirm the active `tab_num` before executing interactive commands if you are not using `tab_id`.

### Prompts Produce Irrelevant Pages

*   **Problem**: When using `aria page goto --prompt="..."` or `aria script new --prompt="..."`, the browser navigates to or summarizes content that is not what you expected.
*   **Cause**: Natural language prompts can be ambiguous. `aria` interprets them based on its understanding and the context.
*   **Fix**:
    1.  **Be more specific** in your prompts. Add keywords, specify desired sources (e.g., "search Wikipedia for..."), or explicitly state the kind of information you need.
    2.  Break down complex prompts into smaller, more manageable steps.
    3.  If using scripts, iteratively refine the script's prompt using `aria script <id> edit --prompt="..."`.
    4.  **Heuristic caution**: Prompts can be ambiguous. Always validate results in the browser.

### Local Scope Page Not Created

*   **Problem**: Commands like `aria page new --scope=local --prompt="..."` fail to create a local HTML page or the page is empty/incorrect.
*   **Cause**: This could be due to incorrect prompt phrasing for local file searches, insufficient permissions, or the requested local files/information not being found on the system.
*   **Fix**:
    1.  Refine the prompt to be very specific about file types, locations, or content you are looking for (e.g., "find all `.pdf` files in `C:\reports` containing 'Q4 earnings'").
    2.  Ensure `aria` has the necessary file system access permissions.
    3.  Verify that the files or information you are searching for actually exist in the specified locations.
    4.  **Heuristic caution**: Local pages are temporary. Always confirm file contents or presence manually.

### Browser Not Opening/Closing

*   **Problem**: `aria open` fails to launch a browser, or `aria close` fails to shut down a browser.
*   **Cause**:
    *   Browser executable not found in system PATH or at a standard location.
    *   Browser profile issues (e.g., locked profile).
    *   Conflicts with existing browser instances or other automation tools.
*   **Fix**:
    1.  Ensure the browser you are trying to open (`firefox`, `chrome`, etc.) is correctly installed and its executable is accessible (e.g., in your system's PATH environment variable).
    2.  Close all other instances of the target browser manually and retry.
    3.  Check `aria settings` for any browser-specific configurations that might be incorrect.
    4.  If opening a specific profile, ensure that profile exists and is not corrupted.
    5.  **Heuristic caution**: Browser closing can sometimes be abrupt depending on the browser's state. Save your work before issuing `aria close`.

### Quoting Issues (Single vs. Double Quotes; Windows vs. Linux Shells)

*   **Problem**: Commands with arguments containing spaces or special characters result in parsing errors or unexpected behavior.
*   **Cause**: Differences in how various shells (Bash, PowerShell, CMD) handle quoting and escaping.
*   **Fix**:
    1.  **Windows CMD**: Always use double quotes (`"`) for arguments containing spaces or special characters.
        ```cmd
        aria page 0 summarize "This is a prompt with spaces and special characters!"
        ```
    2.  **Linux/macOS Shells (Bash, Zsh)**:
        *   Use double quotes (`"`) when you want shell variables or command substitutions to be expanded within the string.
        *   Use single quotes (`'`) when you want the string to be treated literally, without any shell interpretation. This is generally safer for prompts.
        ```bash
        aria page 0 summarize "This is a prompt with spaces and special characters!"
        aria page 0 summarize 'This is a prompt with spaces and special characters!'
        ```
    3.  If a prompt itself needs to contain quotes, you might need to escape them according to your shell's rules (e.g., `\"` in Bash/CMD, or change to single quotes if double quotes are within a string).

## Diagnostic Commands

These `aria` commands are essential for understanding the current state and debugging issues:

*   `aria page list`: Shows all active tabs with their `tab_num`, `tab_id`, and URLs. Crucial for verifying tab selection.
*   `aria settings`: Displays `aria`'s current configuration. Helps confirm browser paths, logging levels, and other system-level settings.
*   `aria help` / `aria man`: Provides detailed documentation on commands and their usage. Use these to verify command syntax and available options.
*   `aria version`: Reports the `aria` CLI version. Important for bug reporting and ensuring compatibility.

## "Minimal Repro" Templates and "What to Include in Bug Reports"

When reporting an issue, providing a "minimal reproducible example" greatly helps in diagnosis.

**Template for a Bug Report:**

```markdown
**Title:** [Brief, descriptive title of the bug]

**aria CLI Version:** (Output of `aria version`)

**Operating System:** [e.g., Windows 10, Ubuntu 22.04, macOS Sonoma]

**Browser and Version:** [e.g., Firefox 120, Chrome 120]

**Description:**
A clear and concise description of what the bug is, and what you expected to happen instead.

**Steps to Reproduce:**
1.  `aria open [browser]`
2.  `aria page new --url="[URL if applicable]"`
3.  `aria [problematic command] [arguments]`
4.  [Any other relevant steps, manual actions, or shell commands]

**Expected Behavior:**
[What you expected `aria` to do.]

**Actual Behavior:**
[What `aria` actually did, including any error messages or unexpected browser behavior.]

**Relevant Output:**
```
[Paste output from `aria page list`, `aria settings`, or any error messages from the terminal]
```

**Screenshots/Videos (Optional but helpful):**
[Link to any visual aids demonstrating the issue.]
```
*   **Heuristic caution**: Tab numbers can change. Prompts can be ambiguous. Local pages are temporary. Always validate results in the browser.
