---
name: eleviewer-workstation-dev
description: Develops, debugs, and refactors Python PySide6 modules for the EleViewer desktop application (`eleviewer`). Use this skill whenever working on desktop UI widgets, QThread concurrency, atomic file saves, zero-telemetry PII stripping, or universal TTS reading tools.
---

# EleViewer Sovereignty Workstation Development Skill (`eleviewer`)

When invoked to work on the Python PySide6 desktop application, adhere to these architectural and concurrency rules to maintain lightweight execution speed (~220MB standalone `.exe`), privacy sovereignty, and distraction-free study workflows.

## 1. Zero Telemetry & Data Sovereignty
- **Absolute Privacy:** Never add analytics, tracking scripts, or external telemetry pings.
- **PII Stripping:** When logging crash reports or handling feedback submissions in `feedback_dialog.py` / `main.py`, actively sanitize out user Personally Identifiable Information (PII). Specifically, replace Windows home directory paths (`os.path.expanduser("~")` or `C:\Users\<username>`) with `~` before copying to clipboard or network transmission.
- **Global Sovereignty Workstation Pivot:** Design all onboarding workflows, demo vaults, and tutorial notes for a universal global audience of developers, students, and researchers. Deprecate and ignore campus-specific onboarding constraints (e.g., University of Ghana "Starter Vaults" or campus bundle partnerships).
- **Sovereignty Workstation Philosophy:** Preserve a distraction-free, privacy-first local workspace. Avoid bloated toolbars, intrusive configuration wizards, or unnecessary cloud dependencies.

## 2. UI Theming & Token Consistency (`theme.py`)
- Do not hardcode hex colors (e.g., `#1c1c1c`, `#6cb6ff`) in PySide6 UI modules (`ui.py`, `pdf_viewer.py`, `xlsx_viewer.py`, `vault_explorer.py`).
- Always import and reuse centralized theme constants defined in `theme.py`, which mirror the website's CSS variables:
  ```python
  from theme import BRAND_PRIMARY, BRAND_PANEL, BRAND_PANEL_2, BRAND_ACCENT, BRAND_BORDER, BRAND_BACKGROUND
  ```
- **QComboBox Popup Styling (`QAbstractItemView`):** On Windows, when styling a `QComboBox`, you MUST also explicitly style its popup list view (`QComboBox QAbstractItemView { background: ...; color: ...; }`), otherwise the dropdown items will default to dark Windows system font colors on a dark background, making them illegible.

## 3. Off-Thread Concurrency (`QThread`)
- To guarantee zero GUI freezing during heavy operations, all network requests, file indexing, and auto-save tasks MUST be executed on background `QThread` workers:
  - `FeedbackSubmitThread` / `FeedbackSubmitWorker` for GitHub issue submission.
  - `DraftWorker` for background autosaving.
  - `VaultSearchWorker` for local file indexing and vault searching.
- **Instant Thread Interruption & Queue Purging:** When a background worker executes a blocking third-party call (such as Windows SAPI COM via `pyttsx3`'s `runAndWait()`), putting a message in a thread queue will not be processed until the blocking call finishes. To achieve instant responsiveness when stopping or cancelling:
  1. Immediately clear/drain all pending items from the queue (`get_nowait()`).
  2. Invoke thread-safe native interruption methods (e.g., calling `engine.stop()` on the stored SAPI engine instance) directly from the calling thread to abort the blocking operation.

## 4. The 4 Reflex Keys & Universal TTS (`F9`)
- Preserve seamless global shortcut operation for the 4 Reflex keys:
  - `Ctrl+Q`: Quit application / Lock workspace.
  - `Alt+V`: Toggle Vault sidebar drawer.
  - `Ctrl+T`: Open new workspace tab / web viewer.
  - `Ctrl+Shift+T`: Restore recently closed tab.
- Maintain Universal Text-to-Speech (`F9`), ensuring it can read aloud highlighted or full-page text across all document readers (`pdf_viewer.py`, `docx_viewer.py`, `pptx_viewer.py`, `xlsx_viewer.py`, `editor.py`, and `txt_viewer.py`).
- **Reader Bar Controls & Tactile UX:** Ensure floating reader bars (`TtsReaderBar`) provide unmistakable visual feedback. Use distinct object names (`#TtsStopBtn`) and explicit `:hover` and `:pressed` stylesheet background highlights so users instantly perceive control activation.

## 5. Atomic File Operations (`atomic_write`)
- All user settings (`settings.json`), session state, and document drafts MUST be saved using atomic write patterns (`atomic_write` temp file renaming) to prevent 0-byte file corruption during unexpected Windows power cuts or system shutdowns.

## 6. Installer Creation & Copywriting Standards (`setup.iss`)
- **Flesch-Kincaid & Paul Graham Copywriting:** When creating or modifying installer scripts (`setup.iss`), PyInstaller specs (`EleViewer.spec`), or Winget manifests, never use dry corporate/technical boilerplate. All wizard messages, task descriptions, and option labels must speak in conversational, middle-grader accessible English (e.g., *"Open my study files with EleViewer by default"* instead of *"Register default file associations"*).
- **Distraction-Free Wizard Design:** Ensure custom installer messages (`WelcomeLabel2`, `FinishedLabelNoIcons`) emphasize our core student promise: offline privacy, zero telemetry, local storage, and lightweight speed.

## 7. Qt WebEngine Interception (`createWindow`)
- When embedding `QWebEngineView` (e.g., `WebViewWrapper` in `web_panel.py`), always intercept new window/tab requests (`target="_blank"`, `window.open`) by overriding `createWindow(self, type)`.
- Any parent method invoked by `createWindow` (such as `add_tab` or `open_url_in_new_tab`) MUST:
  1. Accept optional keyword arguments (`url=None`, `title="New Tab"`).
  2. Return the newly instantiated `QWebEngineView` widget pointer.
- Failing to return a valid view pointer back to Qt WebEngine C++ will cause Chromium to hit a fatal `NOTREACHED` exception and fail to open popup links.
- **Fallback Safety Guard:** If the parent tab creation method returns `None` (e.g., if web viewing is disabled or tab creation fails), `createWindow(self, type)` MUST fall back to returning `self` (the original calling view) instead of returning `None`, preventing Chromium from crashing.

## 8. PySide6 Unit Testing & Shiboken C++ Binding Gotchas
- **Shiboken `__init__` Bypassing Restriction:** In PySide6, patching out or bypassing `__init__` on a `QObject` / `QWidget` / `QWebEngineView` subclass will cause shiboken C++ binding errors (`RuntimeError: libshiboken: '__init__' method of object's base class not called`) when any instance method is invoked.
- **Direct-to-Class Method Testing:** To unit test custom widget methods (such as `createWindow` or helper utilities) without instantiating heavy Qt GUI or Chromium WebEngine subprocesses, invoke the function directly on the class while passing a Python mock object as `self`:
  ```python
  mock_view = MagicMock()
  mock_parent = MagicMock()
  mock_view.parent.return_value = mock_parent
  res = WebViewWrapper.createWindow(mock_view, 1)
  assert res is mock_view  # Verifies fallback safety without starting Qt
  ```
- **Qt Application Fixture (`qapp`):** When instantiating real GUI widgets in pytest, always inject the `@pytest.fixture(scope="session") def qapp()` fixture into the test signature so that `QApplication.instance()` is initialized before widget creation.
- **Regression Suite Archiving:** When resolving crash reports from `app.log`, always append automated unit regression tests to `OneDrive\Documents\EleViewer\tests\test_eleviewer_fixes.py` to ensure zero regression recurrence.

## 9. Crash-Safe Atomic Persistence on Windows (`os.replace` & `tempfile`)
- **Zero-Byte Corruption Prevention:** Direct `open(filepath, "w")` calls truncate files to 0 bytes immediately and risk permanent data loss during sudden power dips or system crashes.
- **Mandatory Windows Atomic Pattern:** All JSON/text configuration and session saving MUST write to a temporary file created in the *same directory* as the target file (`tempfile.NamedTemporaryFile(dir=target_dir, delete=False)`).
- **Physical Disk Sync & Handle Closure:** Before calling `os.replace()`, you MUST explicitly invoke `tf.flush()` and `os.fsync(tf.fileno())` to guarantee physical disk persistence. On Windows, ensure the temporary file handle is closed *before* invoking `os.replace(temp_name, target_path)` to prevent Win32 `PermissionDenied` errors.

## 10. Zero-Leak Tab & Chromium Memory Cleanup (`QTabWidget` & `QWebEngineView`)
- **Orphaned C++ Allocation Trap:** In PySide6, calling `self.tabs.removeTab(index)` only detaches the widget from the GUI container; the underlying C++ object (especially heavy `QWebEngineView` Chromium child processes and PDF viewers) remains orphaned in RAM. Python's `del` keyword only decrements reference counts and does not destroy Qt C++ allocations.
- **Mandatory Cleanup Pattern:** When removing a tab, always capture the widget reference before removal and explicitly invoke `widget.deleteLater()` after `removeTab()`:
  ```python
  widget = self.tabs.widget(index)
  self.tabs.removeTab(index)
  if widget:
      widget.deleteLater()  # Safely reclaims C++ RAM on the next event loop cycle
  ```
- **Collection Purging:** Immediately purge any references to the deleted widget from internal Python tracking dictionaries or lists.

## 11. Low-I/O Background Ingestion (`os.scandir` & `QThread` / `QRunnable`)
- **Disk Seek Contention Avoidance:** File searching is strictly I/O-bound. Never spawn excessive concurrent threads (e.g., 50+ threads on standard HDDs/SSDs) as this degrades performance due to disk seek contention.
- **Mandatory `os.scandir` Usage:** Never run synchronous filesystem scanning on the GUI thread or use `os.walk()` / `os.listdir()` for large directories. Always use **`os.scandir()`**, which retrieves file metadata (stat/type) directly from OS directory entries during iteration without extra system calls.
- **Worker Communication:** Execute background vault indexing and recovery scanning inside a dedicated worker (`QThread` for persistent monitoring, `QRunnable`/`QThreadPool` with limited max thread count for bulk scanning) with a periodic GUI update signal (`found_files.emit(list)`) and a cancellation flag (`self.is_running`) to maintain 60 FPS without UI freezing.

## 12. Lightweight Performance Auditing & Benchmarking Standards
- **Lazy Module Ingestion (<100ms Cold Start):** Never import heavy third-party libraries (`openpyxl`, `python-docx`, `python-pptx`, `bleach`, `pygments`, `PySide6.QtPdf`) at top-level module load time in factory routers (such as `file_handler.py`). Always import them lazily inside component instantiation functions (e.g. `create_viewer_widget()`) so that text viewing and empty window initialization boot in under 100ms.
- **Avoid Recursive Win32 Path Resolution Overhead:** Inside recursive directory scanning loops (`scandir_walk`), never invoke `Path(root).resolve()`. `Path.resolve()` issues expensive Win32 `GetFinalPathNameByHandleW` kernel calls for every directory step. Pre-resolve the root directory *once* before the loop, and use `os.path.abspath(root).startswith(vault_str)` for boundary validation.
- **Empirical Benchmark Validation:** When performing speed or performance optimizations, validate results using a micro-benchmark measuring:
  1. Cold-start module import latency (`time.perf_counter()`).
  2. Directory traversal throughput (files & directories per millisecond).
  3. Atomic file write speed (`atomic_write` + `os.fsync()`).
  4. 100% pass rate on `test_eleviewer_fixes.py` regression suite.
- **Mandatory Audit Gate Before Any Performance Fix:** Before implementing any claimed performance bug fix or optimization, you MUST first read the relevant source file and verify the bug actually exists in the current code. A significant portion of "suspected" issues are already correctly implemented in the codebase. Record confirmed-real vs. phantom findings explicitly in your response before writing any code. This prevents wasted effort, avoids introducing regressions from "fixing" working code, and keeps the commit history clean.

## 13. PySide6 + Nuitka Gold Standard Performance Architecture
- **Lazy Chromium Ingestion (<50MB Cold RAM):** Never import `PySide6.QtWebEngineWidgets` or `QtWebEngineCore` at top-level module load time. Defer imports until the user explicitly opens a web tab or HTML preview to avoid triggering `QtWebEngineProcess.exe` on startup.
- **Model/View Virtualization (`QTableView` + `QAbstractTableModel`):** Never use `QTableWidget` for CSV, TSV, or XLSX data viewers. Always implement a custom `QAbstractTableModel` with `QTableView`. Qt will only query cells currently visible in the viewport via `data(index, Qt.DisplayRole)`, guaranteeing flat RAM usage and 60 FPS scrolling even on 100,000+ row files.
- **Async PDF Pre-Buffering:** Offload PDF text parsing and raster pre-buffering to background `QThread` workers to maintain smooth scrolling without blocking the main GUI thread.
- **Nuitka Compilation Trimming:** When building with Nuitka, always specify Link Time Optimization (`--lto=yes`) and selective plugin inclusion (`--include-qt-plugins=sensible,styles`) to strip unused Qt 3D/multimedia DLLs, keeping executable size <250MB.
- **High-Speed Ingestion (`os.scandir`):** Always use `os.scandir()` instead of `os.walk()` for vault indexing and file system traversal to retrieve OS stat metadata without redundant kernel syscalls.

## 14. Session Closing Ritual (Mandatory)
After completing any task session in `eleviewer`, you MUST execute these three steps in order:

1. **Run the regression suite first.** Execute `test_csv_viewer.py`, `test_html_viewer.py`, and `test_link_interception.py` and confirm all tests pass before committing anything. Do not commit broken code.

2. **Commit with a structured message.** Use `type(scope): short summary` on the first line (e.g., `perf(vault): replace Path.resolve() with os.path.abspath()`), followed by a blank line and a bulleted body enumerating every file changed and the precise reason. Use semicolons to chain git commands per PowerShell Rule 11:
   ```powershell
   git add file1.py file2.py; git commit -m "type(scope): summary`n`nbody"
   ```

3. **Update `PROJECT_LOG.md` Historical Ledger.** Prepend a new `### [DATE] Task Title` entry to the ledger with:
   - What changed and why, including the audit result (real bugs found vs. phantom assumptions).
   - An **Agent Notes for Future Sessions** sub-section listing specific non-obvious gotchas discovered during the session (e.g., Win32 API subtleties, Inno Setup registry traps, Nuitka flag requirements). This ledger is written *for future AI agents*, not for the human user — future agents will read it to inherit session context.

---

## 15. Learnings from Recent Issue Triage & Implementation Plan

**Issue Triage Summary (v1.3.0)**
- Identified three P0 crashes affecting launch and feedback submission:
  1. Missing `sys` import in `ui.py` preventing app start.
  2. Undefined `APP_VERSION` in `feedback_dialog.py` causing feedback crashes.
  3. `WebPanel.add_tab()` signature mismatch rejecting `url=`/`title=` kwargs, breaking popup links.
- Additional user requests for a light theme, PPTX image handling, and a positive testimonial.

**Actions Taken**
- Added the missing imports (`import sys` in `ui.py` and `from eleviewer import APP_VERSION` in `feedback_dialog.py`).
- Updated `WebPanel.add_tab()` to accept `url=None, title="New Tab"` kwargs and return a valid `QWebEngineView` pointer per **Rule 7**.
- Included these fixes in the hot‑fix release notes and updated `PROJECT_LOG.md` accordingly.

**Implementation Plan v1.4.0 – "Closing the Gap"**
- Extend the CSV viewer with automatic charset detection and delimiter inference.
- Improve DOCX/PPTX rendering for high‑resolution images and ensure graceful fallback on missing assets.
- Optimize PDF handling: lazy page rasterization and background text extraction to avoid UI freezes.
- Add a unified light theme leveraging the centralized `theme.py` constants for consistent styling.
- Document the `gh issue list` / `gh issue view` workflow as the standard triage pattern for future releases.

**Guideline Updates**
- **Rule 7 (WebEngine Popup Safety):** Enforced keyword‑argument acceptance and fallback return values for all tab creation functions.
- **Rule 11 (PowerShell Command Chaining):** Added examples in `PROJECT_LOG.md` using `;` separators for git commands.
- **New Rule 15 (Issue‑Triage Integration):** Before any release, run `gh issue list --state open` and incorporate findings into the release checklist.

These updates ensure that the most critical crashes are resolved, the development workflow is tighter, and the upcoming v1.4.0 targets the remaining performance and usability gaps identified by the AI Mode research.
