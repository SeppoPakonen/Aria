# Task 01.01.06: Command Dispatching

## Outcome
A functional mechanism for dispatching calls from the main `aria` command to specific subcommands (e.g., `page`, `script`, `open`). This allows for a modular and extensible command structure.

## Why it matters
Effective command dispatching is fundamental for building a structured CLI. It keeps the codebase organized, allows for independent development of subcommands, and makes the CLI easier for users to navigate and understand.

## User story
As a developer, I want to define `aria` subcommands (like `page` or `script`) and have the main `aria` executable correctly route arguments to them, so that I can build out functionality modularly.

## Requirements
- The chosen CLI framework must support subcommand registration and dispatching.
- Root `aria` command should successfully delegate to a placeholder subcommand.
- Error handling for unknown subcommands (e.g., `aria non-existent-command`).

## Non-goals
- Implementing the full logic for any specific subcommand. This task focuses on the routing mechanism.
- Complex argument parsing within subcommands.

## Implementation sketch
- Define a dummy subcommand (e.g., `aria hello`).
- Register this subcommand with the main `aria` entry point using the chosen CLI framework's API.
- The subcommand should simply print a message (e.g., "Hello from aria hello command!").
- Test invoking the dummy subcommand and invoking an unknown subcommand.

## CLI touchpoints
- `aria <subcommand>` (e.g., `aria hello`)
- `aria <unknown-subcommand>`

## Acceptance criteria
- Executing `aria hello` (or similar dummy subcommand) successfully invokes its associated function.
- Executing `aria unknown-command` results in an appropriate error message from the CLI framework, indicating an invalid command.

## Diagnostics / observability
- Review command output for correct dispatching and error messages.
- Check exit codes for success (0) and failure (non-zero) for valid/invalid commands, respectively.

## Risks & mitigations
- **Risk**: Framework complexities in subcommand implementation.
  - **Mitigation**: Consult framework documentation and examples extensively; start with the simplest possible subcommand.
- **Risk**: Inconsistent subcommand API or usage patterns.
  - **Mitigation**: Establish clear guidelines for subcommand definition and argument handling from the outset.

## Links
- [Back to Phase 01.01: Project Scaffolding](../../overview.md)
- [Track 01: Implement Underlying Framework and MVP](../../../overview.md)
- [Runbook: 00-overview.md](../../../../runbooks/00-overview.md): High-level context for `aria` commands.
