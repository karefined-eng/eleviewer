# Windows package-manager release runbook

Added `docs/releases/windows-package-manager-runbook.md` as the operational
guide for future AI agents releasing EleViewer through GitHub Releases, WinGet,
Scoop, and Chocolatey. Microsoft Store is excluded at the user's direction.

The guide reflects the current `build.yml` flow: GitHub Releases and WinGet are
automated by a version tag; Scoop and Chocolatey require separate package
submission/update steps. It records the current WinGet PR for 1.3.5, checksum
handling for the separate installer and portable ZIP, unsigned-release policy,
credential boundaries, platform review steps, and required validation. It also
flags a concrete Chocolatey release gate: test elevated and per-user install,
upgrade, and uninstall behavior before submitting because the current Inno
Setup installer is configured for lowest privileges and per-user integration.

Validation: checked the guidance against `.github/workflows/build.yml`,
`winget/`, `setup.iss`, `release_hash.py`, `version.py`, and official platform
documentation. No package was submitted and no release was run.
