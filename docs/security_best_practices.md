# Security Best Practices for Aria

Aria is a powerful tool for AI-driven web automation. Because it interacts with web browsers and external LLM providers, following security best practices is essential to protect your data and accounts.

## 1. API Key Management

Aria requires an API key for the Gemini API (and potentially other services).

- **Use Environment Variables:** Never hardcode your API keys in scripts or configuration files. Use environment variables (e.g., `GOOGLE_API_KEY`).
- **Secret Rotation:** Periodically rotate your API keys to minimize the impact of a potential leak.
- **Least Privilege:** If possible, use API keys with restricted permissions or usage quotas.

## 2. Sensitive Sites and Data

While Aria can navigate any website, you should exercise extreme caution when using it on sites containing highly sensitive information.

- **Avoid High-Stakes Sites:** We recommend **not** using Aria for automated interactions with banking, financial services, healthcare portals, or primary personal email accounts unless you have reviewed the scripts thoroughly and understand the risks.
- **Login Credentials:** Be careful when automating login flows. Aria may capture and process sensitive form fields.
- **Session Persistence:** Aria uses browser profiles. Be aware that being logged into a site in one session might persist to another if not managed carefully.

## 3. Data Privacy and LLMs

Aria works by sending page content, metadata, and screenshots (if configured) to an LLM provider (e.g., Google Gemini).

- **Content Exposure:** Any data visible on the pages Aria visits may be sent to the LLM provider. This includes personal information, private messages, or internal company data.
- **Provider Policies:** Review the privacy policy and terms of service of the LLM provider you are using to understand how they handle your data.
- **Sensitive Information:** Avoid navigating to pages that display sensitive PII (Personally Identifiable Information) or secrets while Aria is active.

## 4. Script Safety

Aria scripts are powerful and can perform actions on your behalf.

- **Review Third-Party Scripts:** Never run an Aria script from an untrusted source without reviewing its code first.
- **Audit Actions:** Use Aria's logging and report generation features to audit what a script did during its execution.
- **Local Development:** Test new scripts in a controlled environment before running them against important accounts or data.

## 5. Execution Environment

- **Sandboxing:** For maximum security, run Aria in a sandboxed environment or a dedicated virtual machine, especially when running complex or third-party scripts.
- **Updates:** Keep Aria and its dependencies (especially Selenium and browser drivers) updated to the latest versions to benefit from security patches.

## Summary

Security is a shared responsibility. By following these guidelines, you can leverage the power of Aria while minimizing risk to your digital identity and data.
