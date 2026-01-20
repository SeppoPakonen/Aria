# Task: Implement Resilience Patterns (Exponential Backoff)

## Outcome
A centralized, reusable retry mechanism with exponential backoff and jitter, integrated into Aria's navigation and interaction logic.

## Requirements
- A `retry` decorator or utility function in `src/utils.py` (or similar).
- Support for configurable retries, initial delay, multiplier, and jitter.
- Integration into `Navigator.navigate_with_prompt` or related methods.
- Integration into API calls (e.g., Gemini API interactions).

## Implementation Steps
1. **Create `src/utils.py`**:
   - Implement `retry(exceptions, tries=3, delay=1, backoff=2, jitter=0.1)` decorator.
2. **Update `src/navigator.py`**:
   - Apply the retry mechanism to browser navigation and element interactions where appropriate.
3. **Update API interactions**:
   - If applicable, wrap AI provider calls with retries.
4. **Tests**:
   - Create `tests/test_reliability.py` (or update existing) to verify retry logic.

## Acceptance Criteria
- A function decorated with `@retry` will execute multiple times if specified exceptions occur.
- The delay between retries increases exponentially.
- The system eventually fails with a clear error after all retries are exhausted.
