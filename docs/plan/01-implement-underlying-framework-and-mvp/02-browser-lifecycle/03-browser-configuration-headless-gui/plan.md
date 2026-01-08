# Task 01.02.03: Browser Configuration (Headless/GUI)

## Goal
Add a `--headless` flag to the `aria open` command to allow running the browser in the background without a visible UI.

## Context
This feature is crucial for automated scripts, CI/CD pipelines, and other non-interactive environments where a visible browser is unnecessary or impossible.

## Steps
1.  Modify `src/aria.py` to add an optional `--headless` boolean flag to the `open` command.
2.  Pass the value of the `--headless` flag from `aria.py` to the `AriaNavigator` constructor in `navigator.py`.
3.  The `AriaNavigator` constructor should already handle the `headless` argument, so no changes are expected there, but this should be verified.

## Acceptance Criteria
*   `aria open <URL> --headless` successfully launches the browser in headless mode and navigates to the URL.
*   `aria open <URL>` (without the flag) launches the browser with a visible GUI.
*   The command functions correctly in both modes.

## Cross-references
*   Phase 01.02: [Browser Lifecycle](docs/plan/01-implement-underlying-framework-and-mvp/02-browser-lifecycle/overview.md)
*   Track 01: [Implement Underlying Framework and MVP](docs/plan/01-implement-underlying-framework-and-mvp/overview.md)
*   Related Runbook: [Browsers Runbook](docs/runbooks/30-browsers.md)
