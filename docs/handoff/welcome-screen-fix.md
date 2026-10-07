# Welcome screen fix

## Issue
The app crashed while creating the welcome tab because `ui.py` referenced a local variable named `brand_accent` before it was assigned. The first assignment occurred later in `_create_welcome_widget()`, so startup failed immediately when the welcome widget was instantiated.

## Fix
Initialize the accent from `get_brand_accent()` before styling the "Start here" label, then reuse the same variable for the later dropdown styling. This keeps the CSS consistent and avoids the unbound local error.

## Verification
Ran the repository test suite with `pytest -q` and confirmed it passes:

- 48 passed
- 1 warning
