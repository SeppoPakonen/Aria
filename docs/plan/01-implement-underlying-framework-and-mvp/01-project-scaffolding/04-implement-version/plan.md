# Task 01.01.04: Implement `--version`

## Outcome
The `aria` CLI correctly responds to the `--version` flag by displaying the current version number of the application.

## Why it matters
Providing version information is essential for users to understand which release of `aria` they are running, which aids in troubleshooting, reporting bugs, and ensuring compatibility.

## User story
As a user, I want to be able to quickly check the version of `aria` I'm using, so that I can easily determine if I have the latest features or if I need to update.

## Requirements
- The `--version` flag should be recognized globally (e.g., `aria --version`).
- It should print a consistent version string to stdout.
- The version string should be configurable (e.g., read from `pyproject.toml` or a dedicated `__version__.py` file).

## Non-goals
- Implementing a complex versioning scheme (e.g., checking for updates).
- Displaying detailed build information beyond the version number.

## Implementation sketch
- Define a version string in `pyproject.toml` or `src/aria/__version__.py`.
- Configure the chosen CLI framework to expose a global `--version` flag.
- The `--version` action should print the version string and exit cleanly.

## CLI touchpoints
- `aria --version`

## Acceptance criteria
- Executing `aria --version` prints a valid version string (e.g., `aria, version 0.1.0`).
- The command exits with a success code (0).

## Diagnostics / observability
- Check stdout for the version string.
- Check exit code.

## Risks & mitigations
- **Risk**: Version string out of sync with actual release.
  - **Mitigation**: Automate version updates during release process; ensure a single source of truth for the version.
- **Risk**: Framework specific quirks in implementing global flags.
  - **Mitigation**: Consult framework documentation; start with a minimal example.

## Links
- [Back to Phase 01.01: Project Scaffolding](../../overview.md)
- [Track 01: Implement Underlying Framework and MVP](../../../overview.md)
- [Runbook: 40-settings-help-man.md](../../../../runbooks/40-settings-help-man.md): Mentions `version` in context of other utility commands.
