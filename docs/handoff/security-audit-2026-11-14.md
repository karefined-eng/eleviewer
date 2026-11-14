# Security audit handoff

## Scope

Reviewed injection surfaces, authentication boundaries, embedded secrets, update verification, local HTML/Markdown rendering, subprocess calls, and declared Python dependencies.

## Findings and changes

- Markdown preview now fails closed if `bleach` is unavailable instead of rendering generated HTML without sanitization.
- Update hash manifests are accepted only from trusted HTTPS GitHub hosts and only when they contain a 64-character hexadecimal SHA-256 digest.
- Windows Explorer is launched with an argument list rather than a shell-like command string containing a user-controlled path.
- No embedded credentials, access tokens, private keys, or application authentication bypass were found.

## Remaining risk

`requirements.txt` now pins the direct runtime dependencies to versions validated in this environment. Package hashes are still not recorded, so a future release process should generate a platform-specific hashed lockfile.

## Validation

Focused security tests and syntax checks should be run with:

```text
python -m pytest -q test_security_hardening.py
python -m py_compile markdown_renderer.py updater.py web_downloads.py
```

## Follow-up plan

1. **Done:** Added `requirements.lock.txt` with deterministic direct runtime pins and configured CI to install and audit it.
2. **Done:** Added regression coverage for sanitizer-unavailable behavior and updater metadata validation.
3. **Pending:** Generate platform-specific package hashes from a clean release environment; local hash resolution stalled.
4. **Pending:** Review local HTML/WebEngine isolation separately, especially cookie persistence and JavaScript behavior.
