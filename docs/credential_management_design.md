# Design: Secure Credential Management in Aria

## Overview
Aria needs a secure way to handle sensitive information such as usernames, passwords, and API keys. This design ensures that credentials are never hardcoded in scripts, never exposed in logs, and can be easily managed by the user.

## Core Components

### 1. Environment Variable Injection
Scripts can use placeholders with the `env:` prefix to pull values from the system environment.
- **Syntax:** `{{env:VARIABLE_NAME}}`
- **Resolution:** `ScriptManager` will check `os.environ` for the variable. If not found, it will prompt the user to provide it (and optionally save it to the vault).

### 2. Local Credential Vault
A local, (optionally) encrypted store for credentials that are frequently used but shouldn't be in environment variables.
- **Storage:** `~/.aria/credentials.json`
- **Security:** In the initial version, this will be a simple JSON file. Future iterations will include encryption using a master password or system-specific keychain (like `keyring`).
- **Commands:**
  - `aria settings credentials set KEY VALUE`: Store a credential.
  - `aria settings credentials list`: List stored keys (never values).
  - `aria settings credentials remove KEY`: Delete a credential.

### 3. Log Masking
To prevent accidental leakage of sensitive data, the logging system must redact any strings known to be credentials.
- **Mechanism:** `Logger` will maintain a set of "sensitive strings" collected during credential resolution.
- **Redaction:** Any occurrence of these strings in log messages or JSON log data will be replaced with `[REDACTED]`.

## Implementation Plan

### Step 1: `CredentialManager`
Create a new module `src/credential_manager.py` to handle:
- Loading and saving `~/.aria/credentials.json`.
- Getting and setting credential values.
- Identifying if a placeholder refers to a vault entry (e.g., `{{vault:KEY}}`).

### Step 2: Update `ScriptManager`
Enhance `ScriptManager.run_script` to:
1. Identify `env:` and `vault:` placeholders.
2. Resolve values using `os.environ` or `CredentialManager`.
3. If missing, prompt the user and offer to save to the vault.
4. Pass the resolved values to the `Logger` for masking.

### Step 3: Enhance `Logger`
Update `src/logger.py` to:
- Accept a list of sensitive strings.
- Implement a filter or formatter that redacts these strings.

### Step 4: CLI Integration
Add credential management commands to `src/aria.py` under `aria settings credentials`.

## Security Considerations
- **File Permissions:** Ensure `~/.aria/credentials.json` has restrictive permissions (e.g., `600` on Linux).
- **Encryption:** While the first version might be plain JSON for simplicity, encryption is a high priority for "Enterprise Readiness".
- **Prompting:** Ensure that when prompting for passwords, input is masked (e.g., using `getpass`).
