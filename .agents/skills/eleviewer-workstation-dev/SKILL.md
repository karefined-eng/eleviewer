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


