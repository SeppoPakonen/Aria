# Phase 04: Script Parameterization Patterns

## Goal
Enable users to pass parameters to saved scripts using simple prompt patterns, making scripts more reusable and flexible without adding complex CLI flag management.

## Objectives
- Implement a pattern for identifying placeholders in script prompts (e.g., `{{query}}`).
- Update `script run` to prompt for missing parameters or accept them as arguments.
- Document common patterns for script parameterization.

## Tasks
1. **01-implement-basic-prompt-parameterization**: Add logic to `ScriptManager` to identify and replace placeholders in prompts.
2. **02-update-script-run-for-parameters**: Modify `aria script run` to handle scripts that require parameters.
3. **03-document-parameterization-patterns**: Add examples and documentation for using parameters in scripts.
