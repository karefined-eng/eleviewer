# UX rationale: welcome-screen distillation

## Intent

The welcome screen should feel like a calm landing pad, not a dashboard of competing prompts. The distillation pass reduces visual noise, keeps the single task flow obvious, and preserves the existing search and folder-linking behavior.

## Principles applied

- **Reduce cognitive load:** The hero, quick actions, and search surface now share a tighter rhythm with less empty space and fewer competing blocks. The user sees the next step before deciding what to do.
- **Give the primary action room to breathe:** Search is still the main discovery tool, but it is now visually paired with clearer guidance instead of being crowded by contradictory surfaces.
- **Keep the copy grounded in user tasks:** The app still names the real actions—open a file, create a note, use the web panel, or start a quick note—and keeps the quick shortcuts visible.
- **Maintain actionability in empty states:** When no course folder is linked, the welcome view still points directly to the folder-link flow. When no search result exists, guidance is still brief and specific.
- **Preserve pattern familiarity:** The screen still uses the same action objects and labels, so the distillation is a refinement of the existing workflow rather than a new navigation model.

## Implementation boundary

This pass modifies only the welcome screen presentation in `ui.py`. It does not change search logic, folder detection, or shortcut behavior. The underlying actions and screen semantics remain stable so existing tests and workflow expectations continue to hold.

## Validation

The focused welcome-screen tests passed: `python -m pytest -q test_all_ui_actions.py` (7 passed).
