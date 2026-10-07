# EleViewer Agent Guide

## Purpose
This repository is a Python + PySide6 desktop app for browsing and studying local documents. Keep changes small, local, and consistent with the current implementation.

## Working assumptions
- The app entry point is [main.py](../main.py).
- The main UI shell is [ui.py](../ui.py).
- File routing happens in [file_handler.py](../file_handler.py).
- Viewer-specific logic lives in [markdown_renderer.py](../markdown_renderer.py), [docx_viewer.py](../docx_viewer.py), [pptx_viewer.py](../pptx_viewer.py), [pdf_viewer.py](../pdf_viewer.py), [xlsx_viewer.py](../xlsx_viewer.py), and [csv_viewer.py](../csv_viewer.py).
- Interactive tutorials and onboarding live in [tutorials.py](../tutorials.py) and [onboarding.py](../onboarding.py).
- Web browsing panel lives in [web_panel.py](../web_panel.py).
- Versioning single source of truth is [version.py](../version.py).
- The app is intentionally lightweight. Prefer native Python/Qt rendering and small caching or debouncing changes over introducing new runtime dependencies.
- There is no Rust-based viewer implementation in the current repository; do not add Rust or PyO3 work unless the user explicitly asks for it.

## Before editing
- Read this guide before acting. It is the canonical agent guide for this repository; do not create competing copies at the root or under `docs/`.
- Before major architecture changes, UI redesigns, or feature-scope decisions, read `docs/origin.md` if it exists. If the project vision is not documented there, use the README and developer onboarding guide and avoid making unapproved product-direction changes.
- Read `README.md` and `DEVELOPER_ONBOARDING.md` before making architecture or implementation changes.
- Read the relevant module and nearby callers before changing behavior.
- Check whether the change should be covered by an existing test in the repository root (for example [test_markdown_renderer.py](../test_markdown_renderer.py)). Use `pytest -s <test_file>.py` to validate changes.
- If a change affects public module APIs, search for imports before editing.
- Website-specific UI/CSS changes belong in the `eleviewer-site` repository unless the user explicitly asks for desktop app changes.

## Git identity and commits
- When creating commits, use the repository's configured Karefined Git identity (`git config user.name` and `git config user.email`); do not substitute another account.
- Never store, request, expose, or commit passwords, access tokens, private keys, or other credentials. Authentication must come from the user's configured Git/GitHub credential helper.
- Never commit or push unless the user explicitly requests it. Never add a `Co-authored-by` trailer in this repository.

## Documentation, product intent, and handoffs
- Keep this guide as the repository's operational manual for architecture, contribution rules, validation, and known environment traps.
- Before a substantial feature or phase is complete, add a concise permanent walkthrough under `docs/handoff/` covering the implementation, important decisions, and validation. Do not create handoff notes for trivial edits.
- For UI or core-workflow design, record relevant user needs and evidence-based UX reasoning under `docs/research/`; avoid generic aesthetic rationales.
- When evaluating a major product or technical direction, offer candid tradeoffs and practical alternatives. Do not present an unmeasured hypothesis as a proven benefit or silently expand the approved scope.
- For scraping or data-collection requests, assess the target, data sensitivity, and applicable access rules first. Explain privacy and terms-of-service risks when relevant; do not help collect private data or bypass access restrictions. Offer a safer, authorized alternative when needed.

## Implementation rules
- Keep UI responsiveness in mind for preview-heavy paths. Debouncing, caching, and skipping redundant renders are preferred when the user is typing or revisiting the same content.
- Preserve existing keyboard shortcuts and document navigation behavior unless the task explicitly changes them.
- **Tutorial & Dialog Geometry Invariants:** Spotlight overlays in `tutorials.py` must clamp card coordinates strictly within visible window bounds (`max(margin, min(win_w - card_w - margin, card_x))`) to prevent dialogs from rendering off-screen.
- **Version Alignment:** When bumping versions, update [version.py](../version.py), [setup.iss](../setup.iss), [version_sync.py](../version_sync.py), and the Winget manifests in `winget/`.

## Copywriting & Documentation
- **No Developer Jargon in User Copy:** User-facing files (Welcome guide, marketing sites, README intros, release notes) MUST strictly avoid developer jargon (e.g., SQLite, QThread, bleach, chardet, pyttsx3). Translate these into plain English (e.g., "background search engine", "security sanitization"). Keep readability at a 6th-to-8th grade level (Flesch-Kincaid). Developer docs (`DEVELOPER_ONBOARDING.md`, code comments) should remain technical.
- **Lead with Killer Features:** Do not bury the lede. Always highlight EleViewer's unique unified workspace features first: Split-Screen Web Panel, Vaults & Live Search, Session Restore, Persistent Bookmarks, and the Global Quick Note (Alt+E). Generic features (like "opens DOCX") should be listed last.
- Avoid adding new packages unless the task truly requires them.
- **Release Notes vs. Changelog:** Always maintain a dual-format structure for releases. 
  - `CHANGELOG.md` must be written for developers using the strict **"Keep a Changelog"** standard, utilizing semantic headings (`Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`) in reverse chronological order.
  - `release_notes.md` (and public announcements) must be written for users. It must strictly follow the "No Developer Jargon" and "Lead with Killer Features" rules, grouping changes logically by functional area (e.g., Workspace, Web Panel) and utilizing visuals where applicable.

## Release & Distribution
- The production CI/CD pipeline is defined in `.github/workflows/build.yml`. It triggers on tags matching `v[0-9]+.[0-9]+.[0-9]+`.
- The pipeline compiles with Nuitka C++ (LTO enabled), builds the Inno Setup installer, packages the portable zip, generates the Winget installer manifest with dynamic SHA256 hashes, creates the GitHub Release, and submits to the Windows Package Manager.
- Windows Package Manager manifests reside in `winget/karefined-eng.EleViewer*.yaml`.

## Validation
- Run the full root-level test suite with `python -m pytest`.
- If the change touches a viewer, do a quick manual smoke check by launching the app with `python main.py`.

## Tool Quirks and Environment Traps
- The worktree directory name may not change when the session branch is renamed. Searching under `C:\Users\asamoah\copilot-worktrees\eleviewer\elevonprospera-eng-commit-onboarding-update` failed with `Search paths do not exist` even though that was the branch name. Use the actual workspace path (`C:\Users\asamoah\copilot-worktrees\eleviewer\elevonprospera-eng-fantastic-garbanzo`) or omit the path to search from the current repository root.
- `docs/AGENTS.md` points to this file for operational guidance. `docs/origin.md` records only documented product purpose, not an inferred historical origin story.
- **Pytest unavailable / dependency installation blocked:** `python -m pytest` failed with `No module named pytest`. Installing project requirements and pytest failed because the environment could not resolve `files.pythonhosted.org` (`getaddrinfo failed`). Do not treat the suite as passing; report the blocker and use available syntax/static checks until dependencies can be installed.
- **Windows PowerShell command chaining:** This environment's PowerShell does not support `&&` or `||`. Chain commands with `;` and check `$LASTEXITCODE` or `$?` explicitly before dependent steps.
- **Mixed staged and unstaged documentation edits:** Interactive `git add -p` piped through PowerShell can stage unexpected hunks or leave prompts ambiguous. Inspect the index and working-tree diffs separately; use a narrowly scoped patch or index-only update, then verify `git diff --cached` before committing.
- `git merge origin/main` can fail with `Your local changes to the following files would be overwritten by merge` when an uncommitted edit overlaps an incoming change. After approval, `git merge --autostash origin/main` may create the merge commit but fail to reapply the autostash with `Applying autostash resulted in conflicts.` Git keeps the backup in `git stash list`. Resolve overlapping edits by combining both sides, verify each stashed change is represented in the merged tree or worktree, and only then drop the autostash.
- **Offscreen Qt capture caveat:** Capturing this PySide6 UI with `QT_QPA_PLATFORM=offscreen` rendered text as square missing-glyph boxes. The requested `QMainWindow.resize(800, 600)` also yielded a captured size of `804x844` because the non-scrollable welcome content imposed a taller minimum. Treat offscreen text pixels as unreliable; use Qt widget dimensions/accessibility or a real Windows display capture for visual-copy verification, and check the captured image dimensions rather than assuming a resize request took effect.
- **Qt debounce test timing:** A test that waited just longer than a `QTimer` interval intermittently asserted against stale UI state under the full suite. Stop the timer and emit its `timeout` signal directly when testing the debounced callback's resulting state; reserve real-time delay tests for the timer behavior itself.
