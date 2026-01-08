# Track 02: Implement Intermediate Level Features

## Goal
Enhance the core `aria` CLI functionalities by improving user experience, adding more robust interaction patterns, and refining the output quality. This track focuses on improving tab selection, structured prompt outputs, local report generation, and ensuring higher reliability for existing features.

## Scope
- **In**: Improved tab selection and persistence (tab_id handling), structured outputs for prompts, richer local report generation templates, script parameterization patterns (using prompt patterns, not new CLI flags), reliability improvements, clearer error messages, and documentation for packaging/release workflows.
- **Out**: Multi-tab comparison, cross-site data synthesis, vendor comparison, resilience patterns (retries, backoff), advanced security, or full plugin architectures.

## Success Criteria
- Users can reliably select and persist tabs using `tab_id`.
- `summarize` commands provide more structured and actionable outputs.
- Custom report templates can be used to generate diverse local reports.
- Scripts can be written to accept and process simple parameters via prompt patterns.
- Error messages are clear, actionable, and consistent.
- Basic packaging and release documentation exists.

## Dependencies
- Successful completion of Track 01 (MVP features).
- Stable `aria` CLI commands for page and script management.
- External libraries for template rendering (if chosen for reports).

## Risks
- **Over-engineering prompt patterns**: Ensuring flexibility without excessive complexity.
- **Template engine integration**: Potential for dependencies or conflicts.
- **Maintaining CLI stability**: Introducing new features without breaking existing functionality.
- **User adoption**: New features must be intuitive and clearly documented.

## Phases

| ID | Name                                      | Objective                                                                     | Link                                                                                    | Status   |
|----|-------------------------------------------|-------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------|----------|
| 01 | Enhanced Tab Management                   | Improve `aria page` commands with robust `tab_id` handling and persistence.   | [Overview](./01-enhanced-tab-management/overview.md)                                    | Planned  |
| 02 | Structured Prompt Outputs                 | Generate more organized and machine-readable outputs from AI prompts.         | [Overview](./02-structured-prompt-outputs/overview.md)                                  | Planned  |
| 03 | Local Report Generation                   | Enable users to generate custom local reports from collected data.            | [Overview](./03-local-report-generation/overview.md)                                    | Planned  |
| 04 | Script Parameterization Patterns          | Document and enable patterns for passing parameters to `aria` scripts.        | [Overview](./04-script-parameterization-patterns/overview.md)                           | Planned  |
| 05 | Reliability and Error Handling            | Improve the overall stability and clarity of error messages within the CLI.   | [Overview](./05-reliability-error-handling/overview.md)                                 | Planned  |
| 06 | Packaging and Release Documentation       | Document the process for packaging and releasing new versions of `aria`.      | [Overview](./06-packaging-release-documentation/overview.md)                            | Planned  |

## Runbook Alignment
This track expands upon the basic operations covered in the runbooks, providing more advanced capabilities:
- **`10-pages.md`**: Enhances `aria page` commands with `tab_id` functionality (Phase 01).
- **`20-scripts.md`**: Directly relates to script parameterization (Phase 04).
- **`50-recipes.md`**: Improved outputs and reliability will enable more complex and stable recipes (Phases 02, 03, 05).
- **`90-troubleshooting.md`**: Clearer error messages and improved reliability reduce troubleshooting effort (Phase 05).
