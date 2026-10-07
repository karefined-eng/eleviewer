# Handoff: welcome-screen first steps

## Summary

First-run onboarding no longer opens `getting_started/Welcome to EleViewer.md` automatically after the onboarding manager runs. The welcome screen now has a “Start here” card with plain-language descriptions and working actions for:

- Open a file (`Ctrl+O`)
- Create a blank note (`Ctrl+N`)
- Open the web panel (`Ctrl+T`)
- Open Quick Note from anywhere (`Alt+E`)

The full guide remains available to users who choose to open it.

## Files

- `main.py`: removed the automatic first-run guide launch.
- `ui.py`: added the welcome-screen first-steps card using existing action handlers and theme colors.
- `docs/research/onboarding-first-steps.md`: records the UX rationale.

## Validation and delivery

- `python -m pytest -q test_onboarding_flow.py test_user_journey.py` — 4 passed.
- `git diff --check` — passed for the implementation change.
- Original implementation commit: `a51a0560b6b257e675e2e7e7b5d361ebaaee99f4`, pushed on `elevonprospera-eng-commit-onboarding-update`.

If this change ships in a release, update both `CHANGELOG.md` and `release_notes.md`; update the website `/updates` page too if it publishes the same release notes.
