# Release readiness for v1.3.6

This pass prepared the repository for the 1.3.6 release by aligning the version metadata used across the app, installer, and Windows Package Manager manifests.

## Updated files
- `version.py` -> `APP_VERSION = "1.3.6"`
- `setup.iss` -> installer fallback and package version
- `version_sync.py` -> default version in the local sync script
- `winget/karefined-eng.EleViewer*.yaml` -> package versions and installer URL
- `CHANGELOG.md` and `release_notes.md` -> release notes for the new version

## Validation
- Confirmed the release metadata is internally consistent across the checked-in files.
- No product code behavior changes were introduced in this pass; it is a packaging/version alignment release.
