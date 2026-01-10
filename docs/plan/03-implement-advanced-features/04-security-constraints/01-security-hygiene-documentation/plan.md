# Task: Security Hygiene Documentation

## Outcome
A comprehensive set of security best practices and hygiene guidelines for Aria users, documented in a new `docs/security_best_practices.md` file and integrated into the CLI's help/documentation system.

## Requirements
- Identify key security risks associated with AI-driven web automation.
- Provide clear, actionable advice on managing API keys and secrets.
- Define "Safe Usage Zones" and list types of websites/data that should be avoided.
- Explain the privacy implications of sharing browser content with an LLM.
- Provide guidance on reviewing and running custom scripts.

## Implementation Sketch
1. Create `docs/security_best_practices.md` with the following sections:
    - Introduction: Importance of security in web automation.
    - API Key Management: Using environment variables, avoiding hardcoding.
    - Sensitive Sites: Why banking, healthcare, and personal email should be handled with extreme caution or avoided.
    - Data Privacy: Understanding that page content is sent to an LLM provider.
    - Script Safety: Best practices for writing and reviewing Aria scripts.
2. Link the new document from `README.md` and `docs/runbooks/00-overview.md`.
3. (Optional but recommended) Add a `security` command to Aria that displays a summary of these best practices or links to the doc.

## Acceptance Criteria
- `docs/security_best_practices.md` exists and is well-structured.
- The documentation covers API keys, sensitive sites, data privacy, and script safety.
- The document is linked from the project's main README and runbook overview.
- The content is reviewed for clarity and professional tone.
