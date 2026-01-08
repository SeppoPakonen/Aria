# Task: 04: Implement `aria page summarize`

## Objective

Implement the `aria page summarize` command, which extracts the text content of the current page and uses a generative AI model to provide a concise summary.

## Rationale

Manually reading through long web pages can be time-consuming. An AI-powered summarize command provides immediate value to the user by distilling the essential information from the page content, significantly speeding up research and information gathering.

## Implementation Details

1.  **CLI Subcommand (`src/aria.py`)**:
    *   Add a `summarize` command to the `page` subparser.
    *   This command will not require any arguments, as it will act on the currently active tab.

2.  **Page Content Extraction (`src/navigator.py`)**:
    *   Create a new public method `get_page_content(self) -> str`.
    *   This method will:
        1.  Connect to the active session.
        2.  If a session is active, get the page source using `self.driver.page_source`.
        3.  To get a cleaner text representation, it will extract the text from the `<body>` tag of the HTML. A simple way to do this without adding heavy dependencies is to use `self.driver.find_element(By.TAG_NAME, 'body').text`. This will need `from selenium.webdriver.common.by import By`.
        4.  Return the extracted text. If no session is active or an error occurs, return an empty string.

3.  **AI Summarization (`src/aria.py`)**:
    *   A new function, let's call it `summarize_text(text: str) -> str`, will be created.
    *   This function will use the `google.generativeai` library to send the extracted page content to a model (e.g., 'gemini-pro').
    *   It will require an API key, which should be configured by the user through an environment variable (e.g., `GEMINI_API_KEY`). The code should handle the case where the key is not set.
    *   The `google-generativeai` package will need to be added to `requirements.txt`.

4.  **Command Logic (`src/aria.py`)**:
    *   When `aria page summarize` is invoked:
        1.  Instantiate `AriaNavigator` and call `get_page_content()`.
        2.  If content is returned, pass it to `summarize_text()`.
        3.  Print the returned summary to the console.
        4.  Handle potential errors, such as a missing API key.

## Acceptance Criteria

*   Running `aria page summarize` on a page with text should print a concise summary of the content.
*   Running the command with no active browser session should result in an appropriate error message.
*   Running the command without the `GEMINI_API_KEY` environment variable set should result in a user-friendly message explaining how to configure it.
*   The `google-generativeai` package is added to `requirements.txt`.
