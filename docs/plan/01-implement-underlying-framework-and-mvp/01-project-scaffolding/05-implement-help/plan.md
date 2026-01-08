# Task 01.01.05: Implement `--help`

## Outcome
The `aria` CLI correctly responds to the `--help` flag by displaying a comprehensive help message for the main command and subcommands.

## Why it matters
A good help system is crucial for user discoverability of commands, arguments, and options. It reduces the learning curve and provides immediate reference, making the CLI usable without constant external documentation lookups.

## User story
As a user, I want to be able to get inline help for `aria` commands and subcommands, so that I can understand their usage, available options, and arguments without leaving the terminal.

## Requirements
- The `--help` flag should be recognized globally (`aria --help`).
- Help messages should be available for subcommands (e.g., `aria page --help`, `aria page new --help`).
- Help messages should include a brief description of the command, its usage syntax, and a list of available options/arguments.
- Help output should be clear, well-formatted, and consistent.

## Non-goals
- Implementing a full `man` page equivalent (that's a separate task if needed).
- Dynamic, context-sensitive help beyond the command structure.

## Implementation sketch
- Leverage the chosen CLI framework's built-in help generation capabilities. Most frameworks (Click, Argparse) automatically generate help messages from command and argument definitions.
- Ensure all command, subcommand, and argument definitions include descriptive `help` strings.
- Test `aria --help`, `aria page --help` (once `page` subcommand exists), etc.

## CLI touchpoints
- `aria --help`
- `aria <subcommand> --help` (e.g., `aria page --help`)

## Acceptance criteria
- Executing `aria --help` displays a clear, well-formatted help message for the root `aria` command.
- The help message includes a description of `aria` and lists available subcommands (even if they are just placeholders initially).
- The command exits with a success code (0).

## Diagnostics / observability
- Review the output of `aria --help` for clarity, completeness, and formatting.
- Check exit code.

## Risks & mitigations
- **Risk**: Default help output from framework is not user-friendly or comprehensive enough.
  - **Mitigation**: Customize help templates or provide more detailed docstrings/help texts for commands and arguments.
- **Risk**: Inconsistent help messages across different commands as the CLI grows.
  - **Mitigation**: Establish clear guidelines for writing help text; automate checks for consistency if possible.

## Links
- [Back to Phase 01.01: Project Scaffolding](../../overview.md)
- [Track 01: Implement Underlying Framework and MVP](../../../overview.md)
- [Runbook: 40-settings-help-man.md](../../../../runbooks/40-settings-help-man.md): Directly relevant for `help` and `man` commands.
