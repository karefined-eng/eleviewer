# Welcome screen distill pass

## Scope

This update refines the initial welcome tab in `ui.py` to feel cleaner and more focused without changing the actual study workflow. The intent is to reduce noise, keep the action list readable, and let the file search remain the visual center of the page.

## What changed

- Tightened the welcome view spacing and card rhythm so the hero, quick actions, and search panel feel like one calm composition instead of separate competing blocks.
- Kept the existing quick actions and shortcut labels intact for usability and compatibility with keyboard-first workflows.
- Simplified the visual styling of the search surface and quick-action rows while preserving the current folder-link guidance and empty-state copy.

## Why this helps

Students can now scan the page more quickly and identify the next step without visual clutter. The result is a lighter, calmer onboarding surface that still supports the product's established action model.

## Verification

Ran the targeted UI checks successfully:

- `python -m pytest -q test_all_ui_actions.py`
- Result: 7 passed
