# Task: 07: Optional: Browser Selection (`--browser`)

## Objective

Extend the `aria open` command to allow users to specify which browser they want to use for the session.

## Rationale

Currently, `aria` only supports Google Chrome. To make the tool more flexible, users should be able to choose other major browsers like Firefox or Edge. This increases the utility of the tool for different testing and automation scenarios.

## Implementation Details

1.  **CLI Argument (`src/aria.py`)**:
    *   Add a new optional argument `--browser` to the `open` command.
    *   This argument will accept a string (e.g., `chrome`, `firefox`, `edge`).
    *   Set a default value of `chrome`.

2.  **`AriaNavigator` Modifications (`src/navigator.py`)**:
    *   The `start_session` method will be updated to accept a `browser_name` parameter.
    *   Inside `start_session`, a conditional block will determine which WebDriver to initialize based on the `browser_name`.
    *   **Chrome**: Use `webdriver.Chrome` with `ChromeDriverManager`.
    *   **Firefox**: Use `webdriver.Firefox` with `GeckoDriverManager`. This will require adding `from webdriver_manager.firefox import GeckoDriverManager`.
    *   **Edge**: Use `webdriver.Edge` with `EdgeChromiumDriverManager`. This will require adding `from webdriver_manager.microsoft import EdgeChromiumDriverManager`.
    *   The chosen browser and its options will be used to create the `self.driver` instance.
    *   The session data saved to `aria_session.json` should also include the browser name.

3.  **Dependency Management (`requirements.txt`)**:
    *   The `webdriver-manager` package already includes support for different browsers, so no new packages are needed.

## Acceptance Criteria

*   `aria open <URL> --browser firefox` should open the URL in Firefox.
*   `aria open <URL> --browser edge` should open the URL in Microsoft Edge.
*   `aria open <URL>` (without the `--browser` flag) should default to opening in Chrome.
*   `aria close` should work correctly for sessions opened with any supported browser.
