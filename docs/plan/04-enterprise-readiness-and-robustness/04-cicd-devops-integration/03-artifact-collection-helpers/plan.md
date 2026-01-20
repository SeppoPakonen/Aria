# Task: Artifact Collection Helpers

## Outcome
A mechanism to easily package all execution artifacts (logs, reports, session info) into a single archive for easy collection by CI/CD systems.

## Requirements
- A command `aria settings export-artifacts` (or similar) that creates a zip/tar archive.
- Support for specifying an output path.
- Include `aria.log`, `reports/`, and current session metadata.

## Implementation Steps
1. **Update `src/aria.py`**:
   - Add `settings export-artifacts` command.
2. **Implement export logic**:
   - Use `shutil.make_archive` to package `~/.aria/`.
   - Exclude sensitive files (like `credentials.json`!).
3. **Tests**:
   - Verify that an archive is created and contains the expected files, but NOT secrets.

## Acceptance Criteria
- `aria settings export-artifacts --path my-run.zip` creates a zip file.
- The zip file contains `aria.log` and the `reports` directory.
- The zip file DOES NOT contain `credentials.json` or `safety.json`.
