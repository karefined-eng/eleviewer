# Three high-impact improvements

## What changed

- Added `vault_index.py`, a local SQLite filename index that refreshes connected
  folders in the background search worker and removes stale entries.
- Added `async_loader.py` and moved DOCX, PPTX, and XLSX parsing behind Qt
  workers so opening large documents does not block the main window.
- Added `WorkspaceServices` as an application boundary for viewer construction
  and session persistence, and added `.github/workflows/test.yml` for pull
  request and `main` branch validation.

## Important decisions

- The index stores only local file metadata: vault path, file path, filename,
  relative directory, modified time, and size. Document contents are not
  indexed or uploaded.
- Existing viewer APIs remain available; asynchronous loading is used by the
  normal file factory path while synchronous loading remains available for
  direct callers and tests.
- The release workflow remains tag-only. Pull requests use the lighter test
  workflow instead of attempting to build and publish installers.

## Validation

- Changed production modules compile successfully.
- `test_vault_search.py`, `test_security_hardening.py`, `test_pptx_viewer.py`,
  `test_all_ui_actions.py`, CSV/TSV/HTML viewer tests, settings, and shortcut
  tests pass.
- Repository-wide compile remains blocked by the pre-existing null-byte
  scratch file `src/scratch/test_script.py`; this is documented in
  `.agents/AGENTS.md`.
