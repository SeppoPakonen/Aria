# Task: Robust Element Handling

## Outcome
Enhanced reliability for element discovery and interaction in `AriaNavigator`, reducing flakiness caused by page load timing.

## Requirements
- Refactor `Navigator.get_page_content` and other interaction methods to use explicit waits where appropriate.
- Implement a helper for "waiting for element" before interaction.
- Integrate retry logic for element interactions that might fail due to transient DOM states (e.g., "stale element reference").

## Implementation Steps
1. **Update `src/navigator.py`**:
   - Import `WebDriverWait` and `expected_conditions`.
   - Add a `wait_for_element(selector, by=By.CSS_SELECTOR, timeout=10)` method.
   - Refactor `get_page_content` to ensure the body is loaded.
2. **Enhance existing methods**:
   - Ensure `list_tabs` and `goto_tab` handle potential `WebDriverException` during switch or access more gracefully.
3. **Tests**:
   - Update `tests/test_reliability.py` to include tests for element waiting and stale element retries.

## Acceptance Criteria
- Operations that previously might have failed if an element wasn't immediately present now wait for a configurable timeout.
- Stale element references are automatically handled by a retry (if using the `@retry` decorator correctly).
