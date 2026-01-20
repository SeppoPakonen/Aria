# Task: Custom Navigator Plugins

## Outcome
A pluggable navigation system where users can register and use alternative browser automation engines (Playwright, Puppeteer, or custom Selenium wrappers) via plugins.

## Requirements
- Define `BaseNavigator` interface (likely by making `AriaNavigator` inherit from it or renaming it).
- Registry for Navigators in `PluginManager`.
- Update `aria.py` to allow selecting a custom navigator via CLI (e.g., `--navigator`).
- Ensure `PluginManager` context provides the selected navigator.

## Implementation Steps
1. **Refactor `src/navigator.py`**:
   - Introduce `BaseNavigator` abstract base class.
   - Make `AriaNavigator` inherit from `BaseNavigator`.
2. **Update `PluginManager`**:
   - Add `register_navigator(name, navigator_class)`.
   - Add `get_navigator(name)`.
3. **Update `src/aria.py`**:
   - Add `--navigator` CLI flag.
   - In `_run_cli`, instantiate the selected navigator from the registry.
   - Register the default `aria` navigator (AriaNavigator).
4. **Tests**:
   - Verify that a plugin can register and Aria can use a custom navigator.

## Acceptance Criteria
- `aria open --navigator aria` works as before.
- A plugin can register a new navigator named `mock`.
- `aria open --navigator mock` uses the plugin's navigator class.
