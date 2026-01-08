# Task 01.02.02: Implement `aria open` basic functionality

## Goal
Implement the basic `aria open <URL>` command to launch a browser and navigate to the specified URL.

## Context
This task builds upon the WebDriver integration by providing the first user-facing command to interact with browsers. It will focus on the simplest form of opening a URL without advanced options.

## Steps
1.  Define the `open` command in the CLI framework.
2.  Parse the URL argument.
3.  Initialize a WebDriver instance (reusing or adapting the work from Task 01.02.01).
4.  Use WebDriver to navigate to the provided URL.
5.  Handle basic error cases (e.g., invalid URL).

## Acceptance Criteria
*   `aria open <URL>` successfully launches a browser and navigates to `<URL>`.
*   The command completes without errors for valid URLs.
*   Basic error handling is in place for invalid input.

## Cross-references
*   Phase 01.02: [Browser Lifecycle](docs/plan/01-implement-underlying-framework-and-mvp/02-browser-lifecycle/overview.md)
*   Track 01: [Implement Underlying Framework and MVP](docs/plan/01-implement-underlying-framework-and-mvp/overview.md)
*   Related Runbook: [Browsers Runbook](docs/runbooks/30-browsers.md)
