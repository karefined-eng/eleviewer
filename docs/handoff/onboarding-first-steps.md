# Handoff: welcome-screen first steps

## Summary

First-run onboarding no longer opens `getting_started/Welcome to EleViewer.md` automatically after the onboarding manager runs. The welcome screen now has one “Start here” section with plain-language descriptions and working actions for:

- Open a file (`Ctrl+O`)
- Create a blank note (`Ctrl+N`)
- Open the web panel (`Ctrl+T`)
- Open Quick Note from anywhere (`Alt+E`)

The full guide remains available to users who choose to open it.
Vault search guidance also explains its scope, offers a direct course-folder setup action when none is linked, and shows a no-matches recovery hint. The four quick-start actions appear only once; settings remain available from the toolbar and menus.
The welcome screen also scrolls vertically in compact windows, keeping recent files and bookmarks reachable without forcing the window to exceed the requested size.

## Files

- `main.py`: removed the automatic first-run guide launch.
- `ui.py`: provides one actionable welcome quick-start section, clear Vault search states, and vertical scrolling for compact windows.
- `test_all_ui_actions.py`: covers the Vault setup/no-results states, verifies there is only one quick-start action list, and checks scrolling at 800×600.
- `docs/research/onboarding-first-steps.md`: records the UX rationale.

## Validation and delivery

- `python -m pytest -q` — 49 passed, 1 warning after the search states, quick-start consolidation, and compact-window updates.
- `git diff --check` — passed for the implementation change.
- Original implementation commit: `a51a0560b6b257e675e2e7e7b5d361ebaaee99f4`, pushed on `elevonprospera-eng-commit-onboarding-update`.

If this change ships in a release, update both `CHANGELOG.md` and `release_notes.md`; update the website `/updates` page too if it publishes the same release notes.
