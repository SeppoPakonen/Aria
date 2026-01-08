# 30-browsers.md

This runbook covers how to control browser instances using `aria open` and `aria close` commands, as well as recommended workflows for integrating `aria` with manual browser usage.

## `aria open` / `aria close` Usage

### `aria open {firefox|chrome|opera|edge|safari}`

This command launches the specified browser. If the browser is already running, `aria` will simply connect to it (ensuring idempotency where possible).

```bash
# Linux/macOS: Open Google Chrome
aria open chrome

# Windows CMD: Open Mozilla Firefox
aria open firefox
```

### `aria close [{firefox|chrome|opera|edge|safari}]`

This command closes browser instances.

*   If a specific browser is named (e.g., `firefox`), only that browser instance (or instances) will be closed.
*   If no browser is specified, `aria` attempts to close all browser instances it currently manages.

```bash
# Linux/macOS: Close only Chrome
aria close chrome

# Windows CMD: Close all managed browser instances
aria close
```

## Recommended Hybrid Workflow

The power of `aria` is amplified when combined with manual browser interaction. This "hybrid" workflow allows you to seamlessly switch between automated tasks and your own manual browsing.

1.  **Open Dedicated Automation Profile in Browser (Manual Note)**:
    It's highly recommended to configure your browser (Chrome, Firefox, etc.) to use a dedicated profile for `aria` automation. This keeps your personal browsing history, cookies, and extensions separate from automation tasks.
    *   **Firefox**: You can launch Firefox with `firefox -P <profile_name>` or manage profiles via `about:profiles`.
    *   **Chrome**: Use `chrome.exe --profile-directory="Profile Name"` or manage profiles via `chrome://settings/manageProfile`.
    This step is done manually, but `aria` will connect to the active profile.

2.  **User Does Interactive Steps**: Perform any initial manual setup, logins, or navigation within the dedicated browser profile.

3.  **`aria` Drives Navigation/Summaries**: Once you've set the stage, use `aria` commands to automate specific tasks: navigate to complex URLs, summarize lengthy articles, extract data, or run scripts.

### Hybrid Workflow Example: Researching a Product

*   **Goal**: Manually browse for a product on an e-commerce site, then use `aria` to summarize reviews.
*   **Workflow**:
    1.  **Manual**: Open Firefox with your `aria`-specific profile. Manually navigate to Amazon and search for a "Smartwatch X". Click on the product page.
    2.  **`aria`**: Once on the product page, use `aria` to summarize reviews:
        ```bash
        aria page 0 summarize "What are the common complaints and praises about this smartwatch from customer reviews?"
        ```
    3.  **Manual**: Review the summary provided by `aria` in your terminal, and continue browsing other products or pages as needed.

## Example Workflows

### Chrome-focused Workflow

*   **Goal**: Perform several tasks specifically within a Chrome browser.
```bash
# 1. Ensure Chrome is open
aria open chrome
# 2. Create a new page in Chrome
aria page new --url="https://www.google.com"
# 3. Search for something
aria page 0 goto --prompt="latest tech news"
# 4. Summarize the first result
aria page 0 summarize "What is the most significant news story?"
```

### Firefox-focused Workflow

*   **Goal**: Use Firefox for all `aria`-driven automation.
```bash
# 1. Ensure Firefox is open
aria open firefox
# 2. Create a new page in Firefox and navigate to a specific article
aria page new --url="https://en.wikipedia.org/wiki/Artificial_intelligence"
# 3. Extract key historical milestones
aria page 0 summarize "List the five most important historical milestones in AI development."
```

### Switching Browsers

*   **Goal**: Start a task in one browser, then switch to another for a different task.
```bash
# 1. Start with Chrome for a specific task
aria open chrome
aria page new --url="https://my-internal-dashboard.com"
# ... interact with dashboard using aria ...

# 2. Now switch to Firefox for a public web search
aria open firefox
aria page new --prompt="best practices for cloud security"
# ... continue with Firefox tasks ...

# 3. Close only Chrome when done with its tasks
aria close chrome
```

### Closing Only One Browser

*   **Goal**: Close a specific browser without affecting others `aria` might be managing.
```bash
# Assume Chrome and Firefox are open via aria
# 1. Perform tasks in both
# ...
# 2. Only close Firefox
aria close firefox
# Chrome remains open and managed by aria.
```

### Closing All Managed Browsers

*   **Goal**: Terminate all browser instances that `aria` has opened or connected to.
```bash
# Assume multiple browsers are open via aria
# 1. Complete all tasks
# ...
# 2. Close everything
aria close
```
*   **Heuristic caution**: Browser closing can sometimes be abrupt depending on the browser's state. Save your work before issuing `aria close`.
