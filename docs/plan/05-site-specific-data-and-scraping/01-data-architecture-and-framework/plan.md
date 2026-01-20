# Phase 01: Data Architecture & Framework

## Tasks
1. **01-implement-site-manager**: Create `src/site_manager.py` to handle the `~/.aria/sites/` storage and site-specific dispatching.
2. **02-add-site-command-to-cli**: Update `src/aria.py` to include the `site` subcommand and basic argument parsing.
3. **03-define-storage-schema**: Establish the standard directory and file structure for site data (e.g., `conversations.json`, `metadata.json`, `media/` folder).
4. **04-implement-local-query-engine**: Create internal functions to filter and print JSON data (e.g., for "show recent" commands).

## Completion Criteria
- `aria site <name>` command exists.
- Running a command creates the appropriate site directory in `~/.aria/sites/`.
- Basic JSON read/write utilities are available to other site-specific modules.
