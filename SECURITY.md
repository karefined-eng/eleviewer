# Security Policy

## Supported versions

Security fixes are prioritized for the latest `main` branch and the latest published EleViewer release. Older releases may not receive backported fixes.

| Version or channel | Security support |
|---|---|
| Latest published release | Supported |
| `main` | Supported for active development |
| Older releases | Best effort only |

## Reporting a vulnerability

Please do **not** report security vulnerabilities in a public GitHub issue, discussion, pull request, or release comment.

Use GitHub's private vulnerability reporting flow from the repository's **Security** tab. If that option is unavailable, contact the repository maintainers privately through GitHub and include the repository name, affected version or commit, operating system, reproduction steps, impact, and any proof-of-concept needed to verify the issue.

Please redact passwords, access tokens, signing credentials, personal data, and other secrets from reports. If a proof-of-concept requires sensitive values, describe the required shape and provide safe test values instead.

## Scope

This policy covers the EleViewer desktop application, document and presentation parsing, local file handling, installer and update artifacts, release packaging, code-signing integration, and the GitHub Actions build and release workflow.

Issues in third-party applications, operating systems, or unrelated repositories should be reported to their respective maintainers unless EleViewer creates a demonstrable security impact.

## Response expectations

The maintainers will acknowledge a report when practical, investigate the issue, and coordinate remediation or mitigation with the reporter. Please allow reasonable time for triage and release preparation before making details public.

When a fix is released, the project may publish a security note describing the affected versions, impact, and upgrade path. Reporter credit will be given only with permission.
