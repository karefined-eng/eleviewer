# EleViewer UI/UX Review → Remediation Plan

The full expert review is in my previous message. This plan (1) captures it permanently in the repo, and (2) implements the **P0 trust/data-loss fixes** — the smallest changeset that stops the app from destroying user work. No P1/P2 changes in this pass.

## Deliverable 1: `UX_REVIEW.md` (new file)

Write the complete review into the repo: overall verdict, what's working well, P0–P3 findings each with file:line references, and a prioritized remediation roadmap (P1–P3 items become the backlog). Written so a contributor can pick up any item without re-doing the investigation.

## Deliverable 2: P0 code fixes

**1. Single source of truth for version (drift: main=1.5.0 vs ui/feedback=1.4.0)**
- New `version.py` with `APP_VERSION = "1.5.0"`.
- `main.py:15`, `ui.py:11`, `updater.py:17`, `feedback_dialog.py:15`, `whats_new.py:9` all import from it. Fixes update checks comparing against the wrong version.

**2. Markdown toolbar-pin wipes all settings**
- `markdown_renderer.py:377` passes a one-key dict to `save_settings()`, which replaces the whole settings JSON (`settings.py:89`) — vaults, web tabs, theme all destroyed. Change to read-modify-write, same as `editor.py:257-260` already does.

**3. Failed file read can be saved over the real file**
- `file_handler.py:_read_file_safely` currently returns `"[EleViewer] Could not read file: …"` as document text. Raise instead, so the existing exception handlers in `ui.py` show the standard "Failed to open file" dialog and no tab is created.
- Add a size guard (refuse text files > ~25 MB with a clear message) so opening a huge file can't freeze the UI thread.

**4. DOCX "save" destroys documents**
- `DocxViewer` is a read-only `QTextBrowser`, but edits-in-name-only mark it modified and Ctrl+S rebuilds the .docx from plain text via `to_docx_bytes()` — formatting/images silently lost.
- Fix honestly, following the existing XLSX precedent: stop wiring `textChanged` → `is_modified`, add the same style "View-only" banner, and guard `save_file`/`get_file_content` so a DocxViewer can never overwrite its file (status/info message instead). Save As exports plain text only with a one-time clear warning.

**5. Settings dialog silently discards all changes on outside click**
- Remove the `WindowDeactivate → reject()` auto-reject in `settings_dialog.py:420-424` (keep Cancel/Save). The same pattern in quick switcher/vault search only loses a query — left as-is for now.

**6. Draft recovery is dead code**
- Instantiate `DraftManager` in `MainWindow` (so the existing `hasattr(self, "draft_manager")` guards in `ui.py` come alive), call `check_and_recover()` after startup, and verify snapshots include untitled notes (they're the ones live autosave skips).
- Fix behavior: when the user answers "No" to recovery, keep the drafts (currently `check_and_recover` deletes them unconditionally).

**7. PPTX Chromium rendering path is dead**
- `pptx_viewer.py:144/150` imports `_SecureWebView`, which doesn't exist in `web_panel` (silently swallowed → always degraded fallback). Use `WebViewWrapper` (the class `html_viewer.py` already uses successfully); verify the methods used (load/findText/signals) match.

**8. Failed web pages show a real error state**
- `web_panel.py:_on_load_finished` ignores `ok`. Render an inline themed error page (message + Retry button) when a load fails (excluding intentional stops / about:blank), and add a `renderProcessTerminated` handler with a reload affordance.

## Verification
- Run the full suite: `pytest -s` from repo root; update any tests asserting the old (buggy) behavior — note the working tree already has uncommitted edits in `onboarding.py`, `settings.py`, `ui.py`, `test_theme_and_adblock.py` which I will build on top of, not revert.
- Smoke-run the app (`python main.py`) and the existing capture script (`capture_ui_check.py`) to confirm: startup clean, no settings loss after pin toggle, DOCX opens read-only with banner, failed page shows error state.

Out of scope (documented in UX_REVIEW.md as the roadmap): light-theme hardcoded-color sweep, Ctrl+F unification, moving blocking work off the UI thread, modal/interruption reduction, empty states, terminology unification, copy/doc corrections.