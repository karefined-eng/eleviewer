# UX rationale: welcome-screen first steps

## Intent

The welcome screen should help a first-time user take a useful next action without requiring them to read a full guide first. The onboarding update removes the automatic guide launch and presents four direct actions exactly once: open a file, create a blank note, open the web panel, and start a Quick Note from anywhere.

## Principles applied

- **Recognition over recall:** Showing familiar action labels and shortcuts lets users identify an available task instead of having to remember a command or search the guide.
- **Progressive disclosure:** The welcome screen surfaces a small set of common actions and short explanations. Longer tutorial material remains available when the user wants it rather than interrupting startup.
- **Lower choice friction:** Each action appears once, with a visible shortcut and plain-language outcome, so students can scan or launch the next step without comparing duplicate lists.
- **Preserve user control:** Startup no longer opens a separate guide automatically; users can choose an action or consult the guide at their own pace.
- **Make empty states actionable:** Welcome search explains that it checks file names in the active course folder. When no folder is linked, the screen offers a direct way to add one; when a search has no matches, it says so and suggests a shorter search.
- **Keep all actions reachable:** The welcome content scrolls vertically in shorter desktop windows instead of forcing the window to grow beyond its available height.

## Implementation boundary

The quick-start rows call existing application actions and retain their existing shortcuts. Search guidance uses the existing folder-linking flow and does not add new task flows or dependencies. The welcome screen uses a native Qt scroll area to keep lower sections reachable at compact window heights. Settings remain available from the existing toolbar and menus rather than appearing as an extra welcome-screen action.

## Validation

The targeted onboarding tests passed: `python -m pytest -q test_onboarding_flow.py test_user_journey.py` (4 passed).
