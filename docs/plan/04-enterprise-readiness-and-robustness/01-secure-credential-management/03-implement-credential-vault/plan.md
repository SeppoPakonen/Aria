# Task: Implement Credential Vault

## Outcome
A functional local credential vault that allows users to store and retrieve sensitive information securely (via system-level or simple file-based storage) for use in Aria scripts.

## Requirements
- `CredentialManager` class to manage `~/.aria/credentials.json`.
- Support for `{{vault:KEY}}` placeholders in `ScriptManager`.
- CLI commands: `aria settings credentials set KEY VALUE`, `list`, and `remove`.
- Integration with `run_script` to resolve vault placeholders.

## Implementation Steps
1. **Create `src/credential_manager.py`**:
   - Implement `load()`, `save()`, `get(key)`, `set(key, value)`, `remove(key)`, and `list_keys()`.
   - Ensure the directory exists and set file permissions (if possible on the OS).
2. **Update `src/script_manager.py`**:
   - Update `run_script` to check for `vault:` prefix.
   - Use `CredentialManager` to resolve these values.
3. **Update `src/aria.py`**:
   - Add the `settings credentials` subcommands.
4. **Tests**:
   - Create `tests/test_credential_manager.py`.
   - Update `tests/test_script_parameterization.py` to include vault tests.

## Acceptance Criteria
- Users can store a credential with `aria settings credentials set MY_PASS secret123`.
- A script with `{{vault:MY_PASS}}` successfully resolves the value without prompting if it's in the vault.
- `aria settings credentials list` shows `MY_PASS` but not `secret123`.
- `aria settings credentials remove MY_PASS` deletes the entry.
