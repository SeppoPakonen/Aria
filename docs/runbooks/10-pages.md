# 10-pages.md

This runbook details the usage of `aria page` commands, which are central to interacting with browser tabs.

## Create a Page (`new`)

Create new browser tabs.

### Create with a URL

Opens a new page and navigates to the specified URL.

```bash
# Linux/macOS
aria page new --url="https://duckduckgo.com"

# Windows CMD
aria page new --url="https://duckduckgo.com"
```

### Create a Local Results Page (`new --scope=local`)

Generates a temporary HTML page with local search results and opens it in a new tab. This is useful for summarizing local file system content.

```bash
# Linux/macOS: Find largest files in home directory
aria page new --scope=local --prompt="find largest files in my home directory"

# Windows CMD: Find all Word documents on C: drive
aria page new --scope=local --prompt="find all docx files on C:"
```

## Navigate Pages (`goto`)

Commands for navigating existing browser tabs.

### Navigate to a URL (`goto --url`)

Directs an existing page to a specified URL.

```bash
# Linux/macOS: Navigate tab 0 to Google
aria page 0 goto --url="https://google.com"

# Windows CMD: Navigate a specific tab ID to a news site
aria page <tab_id> goto --url="https://www.bbc.com/news"
```

### Navigate using a Prompt (`goto --prompt`)

Uses a natural language prompt to navigate or search, allowing `aria` to determine the best course of action (e.g., performing a search and opening the first result).

```bash
# Linux/macOS: Search for cat image websites on tab 0
aria page 0 goto --prompt="search cat image websites"

# Windows CMD: Find a recipe for lasagna on a specific tab
aria page <tab_num|tab_id> goto --prompt="lasagna recipe"
```

### Navigate using Bookmarks Scope (`goto --scope=bookmarks`)

Searches your browser's bookmarks for a relevant link and navigates to it.

```bash
# Linux/macOS: Find a bookmarked download page
aria page <tab_num|tab_id> goto --scope=bookmarks --prompt="download pages"

# Windows CMD: Open a bookmarked development resource
aria page 0 goto --scope=bookmarks --prompt="dev documentation"
```

## Summarize Page Content (`summarize`)

Extracts and summarizes content from a page based on a given text prompt.

```bash
# Linux/macOS: Summarize the main points of the current page for a specific audience
aria page 0 summarize "What is the most important thing for a Finnish person?"

# Windows CMD: Get key takeaways from an article
aria page <tab_id> summarize "summarize this article for a 5th grader"
```

## List Pages (`list`)

Displays all currently open pages (tabs) with their `tab_num`, `tab_id`, and current URL/title. Useful for identifying `tab_num` or `tab_id` for subsequent commands.

```bash
# Linux/macOS & Windows CMD
aria page list
```

## Realistic Recipes

Here are some practical, copy/paste-friendly examples combining `aria page` commands.

### Open Google and Search via Prompt

Goal: Open Google, then use a prompt to search for something.
```bash
# 1. Open a new blank page
aria page new --url="about:blank"
# 2. Get the tab list to identify the new tab (e.g., tab 0)
aria page list
# 3. Use the new tab to search for "cute puppies"
aria page 0 goto --prompt="search for cute puppies"
```

### Jump to a URL and Summarize for a Target Audience

Goal: Navigate to a specific news article and get a summary tailored for a business audience.
```bash
# 1. Open Firefox if not already open
aria open firefox
# 2. Navigate an existing page (e.g., tab 0) to a news article
aria page 0 goto --url="https://www.nytimes.com/2023/01/01/business/economy-outlook.html"
# 3. Summarize the article for a business context
aria page 0 summarize "What are the key implications of this article for small businesses?"
```

### Use Bookmarks Scope to Find a Download Page, then Open Local Results

Goal: Find a bookmarked software download page, then use a local scope to find associated documentation on your machine.
```bash
# 1. Use bookmarks to find a download page (e.g., for "MySoftware")
#    aria will open this in a new tab or an existing one if available.
aria page <tab_num|tab_id> goto --scope=bookmarks --prompt="MySoftware download"
# 2. Assume the download page was opened on tab 1. Now, search local docs for "MySoftware user manual"
aria page new --scope=local --prompt="find 'MySoftware user manual' in my documents"
# Heuristic caution: Always validate results in the browser.
```

### Find Large Files via Local Scope and Summarize What to Delete

Goal: Identify large files on your system and get suggestions on what can be safely deleted.
```bash
# 1. Generate a local page listing large files
aria page new --scope=local --prompt="list files larger than 1GB in my home directory"
# 2. Assume the local page is tab 2. Summarize suggestions for deletion.
aria page 2 summarize "Which of these files are temporary or can be safely deleted?"
# Heuristic caution: Local pages are temporary. Always confirm file operations.
```

### Create Multiple Pages and Interact

Goal: Open three different websites in separate tabs and summarize each.
```bash
# 1. Open Google
aria page new --url="https://google.com"
# 2. Open Wikipedia
aria page new --url="https://wikipedia.org"
# 3. Open DuckDuckGo
aria page new --url="https://duckduckgo.com"
# 4. List pages to confirm tab numbers/IDs
aria page list
# (Example output might be: 0: Google, 1: Wikipedia, 2: DuckDuckGo)
# 5. Summarize Google
aria page 0 summarize "What is the core mission of Google?"
# 6. Summarize Wikipedia
aria page 1 summarize "Describe the content available on Wikipedia."
# 7. Summarize DuckDuckGo
aria page 2 summarize "What is DuckDuckGo's privacy policy?"
```

### Navigate to an Internal Tool and Take Action

Goal: Go to an internal dashboard and prompt for specific data.
```bash
# Assume an internal tool is bookmarked or known by URL
# 1. Navigate to the internal dashboard
aria page 0 goto --url="https://internal-dashboard.mycompany.com/reports"
# 2. Ask for specific data from the dashboard
aria page 0 summarize "Show me the sales figures for Q4 2023 for the EMEA region."
```

### Open a Product Page and Find Reviews

Goal: Navigate to a product page and then find customer reviews.
```bash
# 1. Open a new page for a product
aria page new --url="https://www.amazon.com/dp/B0BDR9QG9H"
# 2. Assuming the new page is tab 0, prompt to find reviews on the page
aria page 0 summarize "What are the common pros and cons mentioned in the customer reviews?"
```

### Research a Topic with Multiple Prompts

Goal: Use iterative prompts to refine research on a topic.
```bash
# 1. Start with a broad search
aria page new --prompt="history of artificial intelligence"
# 2. After the page loads (assume tab 0), refine the search with a more specific question
aria page 0 summarize "Focus on the development of neural networks in the 1980s."
# 3. Further refine
aria page 0 summarize "What were the key breakthroughs in deep learning after 2012?"
```

### Consolidate Information from Multiple Tabs

Goal: Open several related pages, then use a new tab to summarize information across them.
```bash
# 1. Open Page A
aria page new --url="https://example.com/topic-a"
# 2. Open Page B
aria page new --url="https://example.com/topic-b"
# 3. Open Page C
aria page new --url="https://example.com/topic-c"
# 4. List pages to get IDs
aria page list
# 5. Open a new tab (e.g., tab 3) and instruct aria to synthesize information
aria page new --prompt="Compare and contrast the key arguments from tab 0, tab 1, and tab 2."
# Heuristic caution: Prompts can be ambiguous; verify the synthesis.
```

### Navigate to an Article and Check for Updates

Goal: Go to an article and summarize recent developments related to its topic.
```bash
# 1. Navigate to an article
aria page 0 goto --url="https://techcrunch.com/article-on-ai-ethics"
# 2. Summarize recent news on the same topic
aria page 0 summarize "What are the most recent developments or counter-arguments to the points made in this article?"
```

### Open a New Tab and Directly Search for Images

Goal: Open a new tab and immediately perform an image search.
```bash
# 1. Open a new tab and search for images
aria page new --prompt="find images of aurora borealis"
# Heuristic caution: Always validate results in the browser.
```

### Use Local Scope to Explore Codebase and Summarize

Goal: Use local scope to find relevant files in a project and summarize their purpose.
```bash
# 1. Generate a local page with relevant code files
aria page new --scope=local --prompt="list python files related to 'database access' in current project"
# 2. Assuming local page is tab 0, summarize the purpose of these files
aria page 0 summarize "Explain the role of each of these Python files in database access."
# Heuristic caution: Local pages are temporary. Always confirm source code details.
```

## Tab Selection Mini-Guide

Understanding how to select and refer to tabs is crucial for effective `aria` usage.

### How to Get Tab List

Always use `aria page list` to see the current state of your open tabs. This command will output something similar to:

```
0: (f1a2b3c4) "Google" - https://www.google.com
1: (d5e6f7g8) "Wikipedia" - https://www.wikipedia.org
```
Here, `0` and `1` are `tab_num`, and `f1a2b3c4` and `d5e6f7g8` are `tab_id`.

### When to Prefer `tab_num` vs `tab_id`

*   **`tab_num`**:
    *   **Pros**: Easier to remember and type for quick, interactive commands (e.g., "the first tab").
    *   **Cons**: Unstable. If a tab is closed or new tabs are opened/reordered, the `tab_num` of other tabs can change, leading to commands acting on the wrong tab.
    *   **Best Use**: Ad-hoc commands where you are visually confirming the tab's position.

*   **`tab_id`**:
    *   **Pros**: Stable and unique. The `tab_id` remains constant for a tab throughout its lifecycle, regardless of its position. Ideal for scripting and automated workflows.
    *   **Cons**: Longer and less human-readable. Requires first running `aria page list` to find the ID.
    *   **Best Use**: Any script, automation, or sequence of commands where stability is paramount.

### Common Failure Modes

*   **Tab Closed**: If you try to interact with a `tab_num` or `tab_id` that no longer exists, `aria` will report an error. Always verify the tab exists with `aria page list` before critical operations.
*   **Tab Index Changed (`tab_num` only)**: Relying on `tab_num` in a dynamic browser environment (e.g., where other processes or manual actions might open/close tabs) can lead to unintended operations on the wrong tab.
    *   **Heuristic caution**: Tab numbers can change. Always validate results in the browser. For critical operations, use `tab_id`.
