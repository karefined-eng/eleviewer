# UX rationale: welcome-screen first steps

## Intent

The welcome screen should help a first-time user take a useful next action without requiring them to read a full guide first. The onboarding update removes the automatic guide launch and presents four direct actions: open a file, create a blank note, open the web panel, and start a Quick Note from anywhere.

## Principles applied

- **Recognition over recall:** Showing familiar action labels and shortcuts lets users identify an available task instead of having to remember a command or search the guide.
- **Progressive disclosure:** The welcome screen surfaces a small set of common actions and short explanations. Longer tutorial material remains available when the user wants it rather than interrupting startup.
- **Lower choice friction:** Each row pairs one action with a plain-language outcome, helping users distinguish similar starting points quickly.
- **Preserve user control:** Startup no longer opens a separate guide automatically; users can choose an action or consult the guide at their own pace.

## Implementation boundary

The rows call existing application actions and retain their existing shortcuts. They add orientation, not new task flows or dependencies.

## Validation

The targeted onboarding tests passed: `python -m pytest -q test_onboarding_flow.py test_user_journey.py` (4 passed).
