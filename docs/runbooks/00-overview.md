# 00-overview.md

## What is aria?

`aria` is a command-line interface (CLI) tool designed to control web browsers, manage browser tabs (referred to as "pages"), store and execute reusable scripts, and provide access to settings, tutorials, and help documentation. It aims to streamline browser automation and interaction directly from your terminal.

### Core Concepts

*   **Page/Tab**: In `aria`, a "page" directly corresponds to a browser tab. Each page operates independently within the browser.
*   **`tab_num` vs `tab_id`**:
    *   `tab_num`: A zero-based index representing the order of tabs in the browser window. This can change if tabs are reordered or closed.
    *   `tab_id`: A persistent, unique identifier assigned to a tab. It remains constant even if the tab's position changes. Prefer `tab_id` for scripting stability.
*   **Scopes**: `aria` commands can operate within different data scopes:
    *   `default`/`web`: The standard web browsing context.
    *   `bookmarks`: Allows navigating or searching within your browser's saved bookmarks.
    *   `local`: For generating and interacting with temporary HTML pages containing local file system search results or other generated content.
*   **Prompts vs. URLs**:
    *   `--url`: Directly navigates to a specified URL.
    *   `--prompt`: Uses natural language queries to instruct `aria` to find or generate relevant content, which then often results in navigating to a URL or creating a local page.

## Quickstart

This quickstart demonstrates a basic `aria` workflow: opening a browser, creating a new page, navigating to a website, summarizing its content, and listing all open pages.

1.  **Open a browser**:
    ```bash
    aria open firefox
    ```
    *(Note: Replace `firefox` with `chrome`, `opera`, `edge`, or `safari` as needed.)*

2.  **Create a new page (tab)**:
    ```bash
    aria page new --url="about:blank"
    ```
    *(This opens a blank page. `aria` automatically selects this new page, typically `tab_num` 0 or 1 depending on your browser setup.)*

3.  **Navigate to a website**:
    ```bash
    aria page 0 goto --url="https://www.example.com"
    ```
    *(Here, `0` refers to the `tab_num` of the newly created page. Replace with the actual `tab_id` for more robustness.)*

4.  **Summarize the page content**:
    ```bash
    aria page 0 summarize "What is the main purpose of this page?"
    ```

5.  **List all open pages**:
    ```bash
    aria page list
    ```

## Conventions

*   **Quoting and Escaping**: Always enclose arguments containing spaces or special characters in double quotes.
    *   **Windows CMD**: Use double quotes (`"`). Example: `aria page 0 summarize "This is a prompt"`
    *   **Linux/macOS Shell**: Use double quotes (`"`) for prompts that might contain variables, or single quotes (`'`) for literal strings. Example: `aria page 0 summarize 'This is a prompt'`
*   **Placeholders**:
    *   `<tab_num|tab_id>`: Represents either a tab number (e.g., `0`, `1`) or a tab identifier (e.g., `f1a2b3c4`).
    *   `<url>`: A complete web address (e.g., `https://example.com`).
    *   `<prompt>`: A natural language query or instruction.
    *   `<text>`: Any free-form text input.
    *   `<browser>`: Browser name (e.g., `firefox`, `chrome`).
*   **Choosing a Tab Selector**: While `tab_num` is convenient for quick, interactive use, `tab_id` is highly recommended for scripts or repeatable workflows as it is stable.
*   **Idempotency Notes**: Many `aria` commands are designed to be idempotent where possible (e.g., `aria open firefox` will simply ensure Firefox is open if it already is). However, actions like `aria page new` will always create a new page. Be mindful of this when scripting.

## Further Reading

*   [Security Best Practices](../security_best_practices.md): Essential guidelines for safe operation.
*   [10-pages.md](10-pages.md): Detailed usage of `aria page` commands.
*   [20-scripts.md](20-scripts.md): Managing and refining automation scripts.
*   [30-browsers.md](30-browsers.md): Controlling browser instances and hybrid workflows.
*   [40-settings-help-man.md](40-settings-help-man.md): Accessing `aria`'s internal documentation and settings.
*   [50-recipes.md](50-recipes.md): End-to-end practical scenarios.
*   [90-troubleshooting.md](90-troubleshooting.md): Common issues and their solutions.
