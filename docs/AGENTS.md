# EleViewer Agent Guide

This is the documentation-directory entry point for agent guidance. The established repository guide is [`.agents/AGENTS.md`](../.agents/AGENTS.md); read it for architecture, implementation, validation, copywriting, and release rules.

## Architecture map

- `main.py` starts the desktop app and first-run onboarding.
- `ui.py` contains the main window and welcome screen.
- `workspace_services.py` provides the application-level boundary for viewer construction and session persistence.
- `async_loader.py` provides the shared Qt worker used by heavy document viewers.
- `vault_index.py` stores local vault filename metadata for background search.
- `onboarding.py` contains first-run onboarding hooks.
- `getting_started/` contains user-facing tutorials and guides.
- Root-level `test_*.py` files contain the Python test suite.
- `releases/` contains operational package-manager release instructions.
- `.github/workflows/test.yml` runs pull-request and `main` branch tests without invoking the release pipeline.
- `handoff/` contains durable summaries of substantial work phases.

## Search and validation

- Search narrowly by file glob, for example `rg "welcome" -g "ui.py"`.
- Run focused tests with `python -m pytest -q <test_file>.py`; run the full suite with `python -m pytest`.
- Check `git diff --check` before committing.

## Known environment notes

See the `Tool Quirks` section in [`.agents/AGENTS.md`](../.agents/AGENTS.md) for the worktree-path/branch-name distinction and missing historical-origin context.

For GitHub Releases, WinGet, Scoop, and Chocolatey, use the [Windows package-manager release runbook](releases/windows-package-manager-runbook.md). Microsoft Store distribution is out of scope in that guide.
