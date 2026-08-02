# Copilot instructions for `eleviewer`

## Scope
- Primary app code is in the repository root (`main.py`, `ui.py`, viewers, tests named `test_*.py`).
- The `agentic-awesome-skills/` and `.agents/skills/` trees contain separate tooling/content and many unrelated tests/scripts. Do not treat them as the default target unless a task explicitly asks for them.

## Build, run, and test commands
- Install runtime dependencies:
  - `pip install -r requirements.txt`
- Run the desktop app:
  - `python main.py`
- Run EleViewer tests (root test files only):
  - `pytest -q test_*.py`
- Run a single test:
  - `pytest -q test_vault_search.py::test_vault_search_worker_cancellation`
- Release build flow (Windows, aligned to `.github/workflows/build.yml`):
  1. `pip install -r requirements.txt`
  2. `pip install maturin nuitka ordered-set zstandard`
  3. `cd eleviewer-native; maturin develop --release; cd ..`
  4. Build with Nuitka using workflow flags from `.github/workflows/build.yml`
  5. Compile installer with Inno Setup (`setup.iss`)

## High-level architecture
- `main.py` is the bootstrapper: initializes `QApplication`, enforces single-instance behavior via `instance_lock.py`, wires a global exception hook, strips PII in crash text (`paths.strip_pii`), and restores launch/session behavior.
- `ui.py` contains `MainWindow` and workspace composition:
  - Main splitter: vault explorer + editor area.
  - Editor area: tabbed viewers/editors plus bookmarks panel.
  - Web panel is lazy-loaded on demand (`open_web_tab`) to protect cold-start performance.
  - App-level shortcuts and tray/hotkey behavior are centralized here.
- `file_handler.py` is the file-viewer factory. It routes by extension to specialized viewers (`pdf_viewer.py`, `docx_viewer.py`, `xlsx_viewer.py`, `pptx_viewer.py`, `csv_viewer.py`, `html_viewer.py`, `markdown_renderer.py`) and falls back to `EditorTab` for plain text.
- Persistence is AppData-based (`paths.py`) and write-safe:
  - `settings.py`, `session_manager.py`, recent/pinned/bookmark data use `save_utils.atomic_write`.
  - Session restore persists per-tab state, including binary-viewer metadata.
- Vault indexing/search subsystem:
  - `vault_indexer.py` maintains SQLite FTS5 index (with optional `eleviewer_native` Rust acceleration and Python fallback).
  - `vault_search.py` runs search in background worker threads and merges FTS results with filename fallback search.
- Networked surfaces (feedback/update checks) are asynchronous and UI-safe (`QThread` based, e.g., `feedback_dialog.py`).

## Key repository conventions
- **Offline-first + graceful degradation:** network-enhanced features must keep a local fallback path and remain usable without internet.
- **No telemetry and PII scrubbing:** any crash/feedback payloads must sanitize user paths via `strip_pii` before transmission.
- **Dynamic theming at runtime:** use `theme.get_active_palette()` / `get_active_accent()` in widget setup; avoid hardcoded hex values in UI logic.
- **Avoid module-level WebEngine imports:** keep QtWebEngine paths lazy-loaded in action handlers (especially web panel entry points).
- **Threading policy:** expensive I/O, indexing, autosave, and network work should run off the UI thread using `QThread` workers with explicit cancellation/cleanup on dialog close.
- **Atomic writes are required for persisted state:** reuse `atomic_write` for settings/session/list-like data to avoid corruption on abrupt shutdown.
- **Keep core interaction model stable:** preserve reflex shortcuts and lightweight workspace behavior (`Ctrl+Q`, `Alt+V`, `Ctrl+T`, `Ctrl+Shift+T`, `F9`).
