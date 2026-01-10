# Task: Design Credential Management Patterns

## Outcome
A documented design for how Aria will handle sensitive information like usernames, passwords, and API keys, ensuring they are never hardcoded in scripts or exposed in logs.

## Requirements
- Support for environment variable injection (e.g., `{{env:MY_SECRET}}`).
- Support for an optional local encrypted vault for storing credentials.
- Automatic masking of sensitive values in logs.
- Integration with `ScriptManager` to prompt for missing credentials if not provided.

## Proposed Patterns

### 1. Environment Variable Placeholders
Scripts can use a special prefix for placeholders:
`"Login to site with username {{env:SITE_USER}} and password {{env:SITE_PASS}}"`
`ScriptManager` will check for these env vars before running the prompt.

### 2. The Credential Vault
A new `credentials.json` (encrypted) or a system-specific keychain integration.
Command: `aria settings credentials set SITE_USER value`

### 3. Log Masking
Update `logger.py` to identify and mask strings that match known credentials.

## Implementation Sketch
1. Update `ScriptManager.get_script_placeholders` to identify `env:` and `vault:` prefixes.
2. Implement a `CredentialManager` to handle vault operations.
3. Update `aria.py` to add commands for credential management.
4. Enhance `JsonFormatter` in `logger.py` to perform masking.

## Acceptance Criteria
- Design document exists and covers the above requirements.
- The community agrees on the chosen approach (for this POC, I'll proceed with environment variables first).
