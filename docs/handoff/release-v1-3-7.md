# Release readiness for v1.3.7

## Scope

This release packages the fixes for the public Web Panel crash and Read Aloud
silence reports, plus the high-impact workspace improvements:

- QtWebEngine startup failures caused by locked or unavailable files now degrade
  to a user-facing warning instead of terminating the app.
- Read Aloud falls back to Windows Speech when the local speech engine cannot
  initialize or restart.
- Vault search uses a persistent local filename index.
- DOCX, PPTX, and XLSX files load asynchronously through the normal file-opening
  path.
- Workspace service boundaries and pull-request/main CI validation are included.
- Regression tests cover both local-engine failure paths.

## Release metadata

- `version.py` -> `APP_VERSION = "1.3.7"`
- `setup.iss` -> local installer fallback `1.3.7`
- `version_sync.py` -> local default `1.3.7`
- `CHANGELOG.md` and `release_notes.md` -> v1.3.7 patch notes

## Validation

- `python -m pytest -q test_web_dock_layout.py test_tts_engine.py`
- `python -m py_compile web_panel.py ui.py tts_engine.py test_tts_engine.py`
- `git diff --check`

## Published release

- GitHub Release: <https://github.com/karefined-eng/eleviewer/releases/tag/v1.3.7>
- Installer: `EleViewer_Setup_v1.3.7.exe`
- Installer SHA-256:
  `b18c5bb148b454ff3b1c0b79f40f24695f9bbc8b47e32b1cc08beb853086ad95`
- The v1.3.7 release workflow completed successfully. WinGet submission was
  intentionally skipped because the package ID has not yet been accepted into
  `microsoft/winget-pkgs`.
- The website is deployed with v1.3.7 metadata and redirects downloads to the
  v1.3.7 installer.
