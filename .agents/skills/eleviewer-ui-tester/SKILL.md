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
- **The <100ms Cold Start (Chromium Tax):** Verify that `QtWebEngine` and the Web Panel are strictly lazy-loaded and never imported at the top level. The app must launch instantly.
- **Zero UI Freezes (Off-Thread Concurrency):** Test for UI stutter. Any heavy task (Vault Indexing, Draft Auto-saving, Feedback Submission) MUST run on background `QThread` workers.
- **Zero-Dependency Parsing:** Verify that DOCX/PPTX files are parsed using the native Python `zipfile` library to inject Base64 images directly, avoiding disk I/O and bloated dependencies.
- **Native Audio Playback:** Verify that TTS uses the native Windows Multimedia API (MCI) off-thread, avoiding heavy third-party audio packages.
- **Offline-First Resilience:** Ensure no network calls or telemetry block the UI. The app must function instantly without an internet connection.

### D. Critical Gotchas to Check
- **Lazy-Scope Import Contamination (Rule 25 & 36):** Any lazy-loaded function (like `open_web_tab()` or `toggle_web_focus()`) containing local imports MUST place ALL needed names at the VERY TOP of the function body. Module-level imports become invisible inside functions that contain any local `from x import y` statement. Missing imports raise a fatal `NameError` only at runtime when the lazy path executes — not during module load. Always grep for every name used in the function and confirm it's imported locally.
- **Dynamic Theme Palette Access (Rule 2):** PySide6 UI modules (`csv_viewer.py`, `xlsx_viewer.py`) MUST access colors dynamically via `p = get_active_palette()` (e.g., `p['BRAND_PANEL']`) inside initialization methods. Never use module-level static imports or unimported static constants.
- **QSyntaxHighlighter Override Bug (Rule 40):** If syntax highlighting (bold headings, colored inline code, italics) is invisible in `MarkdownViewer` or `HtmlViewer`, the root cause is almost always `color`, `font-size`, or `font-family` inside the `QPlainTextEdit.setStyleSheet()` block. Qt's stylesheet engine silently overrides all `QTextCharFormat` properties applied by the highlighter. Fix: remove those CSS properties from the stylesheet; inject them natively via `widget.setFont(QFont("Consolas", 14))` and `palette.setColor(QPalette.Text, QColor(...)); widget.setPalette(palette)`. Then call `highlighter._setup_formats(); highlighter.rehighlight()`.

### E. Auto-Telemetry Crash Triage (`gh issue list`)
Because EleViewer suppresses terminal stack traces and posts crashes to GitHub via telemetry:
1. Run `gh issue list --limit 10` to view recent `[Bug] Feedback from App` entries.
2. View detailed crash tracebacks using `gh issue view <ISSUE_ID>`.
3. Fix the underlying root cause in source code.
4. Close resolved issues sequentially using PowerShell chaining:
   ```powershell
   gh issue close 45; gh issue close 46; gh issue close 47
   ```

### F. Distribution & Bundling Integrity Check
When auditing a release cycle, verify the following are consistent across all channels:
1. **setup.iss FileExtensions:** Confirm ProgIDs for `.txt`, `.csv`, `.tsv`, `.html`, `.htm`, `.md`, `.pdf`, `.docx`, `.xlsx`, `.pptx` are all registered under `HKCU\Software\Classes\` (not `HKCR`). The `[Tasks]` section should list all formats explicitly.
2. **winget `installer.yaml` FileExtensions:** The `FileExtensions:` block MUST list all 10 supported extensions (`pdf`, `docx`, `xlsx`, `pptx`, `md`, `csv`, `tsv`, `txt`, `html`, `htm`). Missing this field prevents Windows Open With integration for users who install via `winget install`.
3. **CI Rust Build Order (`build.yml`):** The workflow must run `cd eleviewer-native; maturin develop --release` BEFORE the Nuitka compile step. Never use `pip install ./eleviewer-native` — this requires a pre-built `.whl` that won't exist on a fresh runner.
4. **Nuitka Module Inclusion:** Verify `--include-module=eleviewer_native` is present in the Nuitka compile step so the Rust `.pyd` is explicitly bundled into `main.dist/`.
5. **Stale Dependencies:** Run `grep -r "import <package>" --include="*.py" .` for every entry in `requirements.txt`. Remove any package with zero import references (e.g., `pygame` violates Rule 20 — native WinMM audio via `ctypes` replaces it).

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
