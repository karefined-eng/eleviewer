---
name: eleviewer-ui-tester
description: Systematically tests and audits UI components, menu items, toolbars, file viewers, and web pages across both the EleViewer PySide6 desktop app (`eleviewer`) and Next.js marketing site (`eleviewer-site`). Use whenever verifying app stability, triaging auto-telemetry issues, testing viewer rendering, or checking website links and build health.
---

# EleViewer Systematic UI & Site Testing Skill (`eleviewer-ui-tester`)

Use this skill to execute end-to-end systematic testing, bug hunting, and telemetry triage across both the `eleviewer` desktop application and the `eleviewer-site` web repository.

---

## 1. Desktop Application Systematic Audit (`eleviewer`)

### A. Automated PySide6 GUI Verification Script Pattern
When testing `MainWindow`, menus, popups, and viewers, DO NOT rely on `qtbot` or GUI window interaction. Write or run a standalone `pytest` script (`test_all_ui_actions.py`) using `QApplication.instance() or QApplication([])`:

```python
import pytest
from PySide6.QtWidgets import QApplication
from ui import MainWindow
from file_handler import create_viewer_widget

def get_app():
    return QApplication.instance() or QApplication([])

@pytest.fixture
def main_window():
    app = get_app()
    win = MainWindow()
    yield win
    win.close()
```

### B. Exhaustive Execution Coverage Checklist
Every systematic audit of the desktop app MUST rigorously test every single interactive element. Do not skip any button, tab, or menu item:
1. **Toolbars & Buttons:** Systematically click and test EVERY button on the main toolbar, viewer toolbars, and floating panels. Ensure hover states and tactile feedback (Rule 9) work properly.
2. **Menu Items & Tabs:** Trigger every dropdown menu action, context menu, and tab state (switching, closing, reopening).
3. **Reflex Keys & Shortcuts:** Verify `Ctrl+Q` (Quick Switcher), `Alt+V` (Vault Panel), `Ctrl+T` (Web Panel), `Ctrl+Shift+T` (Reopen Closed Tab), `F9` (Read Aloud TTS).
4. **Side Panels:** Toggle and interact with Vault Explorer (`toggle_vault_panel()`), Bookmark Panel (`toggle_bookmarks_panel()`), and Web Panel (`toggle_web_panel()`).
5. **Document Viewers (8 Formats):** Create sample files and pass them to `create_viewer_widget()`:
   - Text (`.txt`), Markdown (`.md`), CSV (`.csv`), HTML (`.html`), PDF (`.pdf`), DOCX (`.docx`), XLSX (`.xlsx`), PPTX (`.pptx`).
6. **Modal Dialog Triggers:** Test `open_settings()`, `open_feedback_dialog()`, `open_getting_started()`, and `open_whats_new()` with `QDialog.exec` mocked to return immediately. Verify click-outside dismissal (Rule 30).
7. **Session Management:** Verify `_new_session()`, `bookmark_current_tab()`, `save_file()`, and `save_file_as()`.

### C. Performance & Responsiveness Verification (Ponytail Principles)
As a core tenet of the "Sovereignty Workstation", the UI must remain fast and consume minimal resources. During the audit:
- **Zero UI Freezes:** Test for UI stutter or blocking when opening large files, searching the Vault, or invoking TTS. If a freeze is detected, the operation MUST be offloaded to a background `QThread` worker.
- **Resource Constraints (The Ponytail Check):** Scrutinize memory and dependency usage. Are we loading heavy packages where native stdlib (like `zipfile` for DOCX/PPTX) suffices? If a feature takes >100ms or uses excessive memory, log it as a bug and mandate a "ponytail" refactor.
- **Thread Interruption:** Verify that background processes (TTS, search) can be immediately aborted without waiting for queues to drain (Rule 6).

### D. Critical Gotchas to Check
- **Lazy-Scope Import Contamination (Rule 25):** Any lazy-loaded function (like `open_web_tab()`) containing local imports AND `global` statements MUST place all local imports at the VERY TOP of the function scope. Mid-function imports cause Python to treat the symbol as an unbound local throughout the entire method, raising `UnboundLocalError` when accessed above the import line.
- **Dynamic Theme Palette Access (Rule 2):** PySide6 UI modules (`csv_viewer.py`, `xlsx_viewer.py`) MUST access colors dynamically via `p = get_active_palette()` (e.g., `p['BRAND_PANEL']`) inside initialization methods. Never use module-level static imports or unimported static constants.

### E. Auto-Telemetry Crash Triage (`gh issue list`)
Because EleViewer suppresses terminal stack traces and posts crashes to GitHub via telemetry:
1. Run `gh issue list --limit 10` to view recent `[Bug] Feedback from App` entries.
2. View detailed crash tracebacks using `gh issue view <ISSUE_ID>`.
3. Fix the underlying root cause in source code.
4. Close resolved issues sequentially using PowerShell chaining:
   ```powershell
   gh issue close 45; gh issue close 46; gh issue close 47
   ```

---

## 2. Marketing Website Audit (`eleviewer-site`)

### A. Location & Scope
The website repository is located at `c:\Users\kwadw\Documents\eleviewer-site` (or `site/`).

### B. Comprehensive Audit Checklist
1. **Asset & Download Link Integrity (`lib/links.ts`):** Verify that direct download links point to valid GitHub Release assets (e.g. `https://github.com/karefined-eng/eleviewer/releases/latest/download/EleViewer.exe`).
2. **SEO & Metadata Verification (`app/layout.tsx`):** Ensure title tags, meta descriptions, OpenGraph images (`og-image.png`), and JSON-LD structured data schemas follow global marketing guidelines.
3. **Build & Type Health Check:** Run Next.js build validation off-thread:
   ```powershell
   cd site; npm run build
   ```
4. **Monochrome Design Consistency:** Confirm that website Tailwind styles mirror the desktop application's CSS variables (`BRAND_PRIMARY`, `BRAND_BACKGROUND`, `BRAND_PANEL`, `BRAND_BORDER`).
5. **Responsiveness & Resource Load:** Run Lighthouse or Next.js analyzer to confirm the site meets fast load times. Audit for unnecessary dependencies and ensure mobile responsiveness holds on all breakpoints.

---

## 3. Session Closing Workflow
After running systematic tests and applying fixes:
1. Run full `pytest` suite in `eleviewer` root directory (ensure 100% pass rate).
2. Check `gh issue list` to verify zero unhandled telemetry bugs remain open.
3. Update `PROJECT_LOG.md` historical ledger.
4. Commit changes with structured git message:
   ```powershell
   git add file1.py file2.py; git commit -m "type(scope): short summary`n`n- Bullet points"
   ```
