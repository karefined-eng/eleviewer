# Developer Onboarding: Welcome to the Free Windows Document Reader

If you are reading this, you are contributing to **EleViewer**â€”a minimalist, multi-tabbed study workstation built on PySide6. 

Before you write a single line of code, you must understand our philosophy.

## The Prime Directives
1. **Zero Telemetry**: No analytics, no tracking, no hidden pings home. User data is sacred and lives locally. (Note: Unhandled crashes are caught by a secure `sys.excepthook` which allows the user to *opt-in* to reporting the stack trace directly to our Vercel feedback API.)
2. **Speed over Features**: If a feature requires a 5-second loading screen or a 200MB dependency, we don't build it. The app must run on old student laptops without lag.
3. **Offline First**: The app must function 100% offline. The Web Panel is an *augmentative* feature, not a core dependency.

---

## Copywriting & Communication Standards (The Paul Graham / Ogilvy Framework)
To maintain our distraction-free student workflow, all user-facing copy (in desktop UI widgets, modals, feedback dialogs, and website components) must adhere to globally praised copywriting principles:
1. **Middle-Grader Readability (Flesch-Kincaid Grade 6â€“8 Rule)**: Keep vocabulary accessible to a 6th-to-8th grade reading level (ages 11â€“13). Avoid bloated corporate jargon, obscure acronyms, and convoluted sentence structures.
2. **Write Like You Talk**: Follow the Paul Graham and David Ogilvy principle of direct, conversational English. Speak to the user as a respected peer and fellow builder.
3. **Outcome-Driven Intake**: When soliciting feedback or reporting errors, focus on user empowerment rather than system failure. Use inviting, direct prompts (e.g., *"Is there something you wish EleViewer could do? Share your idea directly with the developer â€” every submission is reviewed for our upcoming builds."*).

---

## Architecture Overview

EleViewer relies heavily on standard PySide6 widgets and custom components to keep the footprint small.

### The Entry Point
- `main.py`: Bootstraps the application, enforces single-instance locking (so clicking a file opens it in the *existing* window), and binds `sys.excepthook` to route global unhandled exceptions securely to the feedback dialog.

### UI & Shell
- `ui.py`: The `MainWindow` class. Manages the tab widget, toolbars, and the side panels.
- `theme.py`: **CRITICAL**. Do not hardcode hex colors in any UI file. Use the centralized constants (`BRAND_PRIMARY`, `BRAND_PANEL`, etc.) here to ensure the desktop app visually matches the website. Additionally, this module powers the **Dynamic UI Accents** (via `get_active_accent()`) which dynamically injects the user's chosen accent color into active states like `:pressed` and `:checked` buttons.

### Core File Factory
- `file_handler.py`: The heart of the viewer. It reads a file extension and dynamically instantiates the correct viewer (e.g., `MarkdownViewer`, `XlsxViewer`, `PdfViewer`).

### The Viewers
- `pdf_viewer.py`: Uses `QPdfView` (native Qt module, not PyMuPDF) and caches loaded documents to reduce repeated render cost when the same file is reopened.
- `editor.py`: The text/Markdown editor. Uses a PySide6-based preview path with debounced refreshes and cached render output to keep typing responsive.
- `xlsx_viewer.py` & `csv_viewer.py`: Use `openpyxl` and standard library `csv` to render spreadsheets natively into `QTableWidget` with cell/row/column insertion and F9 TTS table summaries.
- `docx_viewer.py` & `pptx_viewer.py`: Render Word and PowerPoint content into lightweight HTML previews using the available parser libraries or XML fallbacks, with caching for repeated loads.
- `html_viewer.py` & `web_panel.py`: Dedicated HTML/XML workstation with a lazy-loaded web dock when the feature is available, plus reload/bookmark controls and global hyperlink interception.

### Sub-systems & Concurrency
- `file_icons.py` & `icons.py`: Minimalist Lucide line-art SVG icon engine supporting two-tone state rendering (`#6cb6ff` active focus vs `#888888` inactive).
- `instance_lock.py`: Local socket IPC server (`QLocalSocket`) enforcing single-instance execution, `--new`/`-n` CLI flag routing, and system-wide hotkey interception (`Alt+E` for Quick Note scratchpad).
- `vault_explorer.py` & `vault_indexer.py`: The left sidebar for file navigation (filtering out system junk files like `desktop.ini`). The current indexer is a Python/SQLite-based background search flow rather than a Rust extension.
- `quick_switcher.py`: The `Ctrl+Q` fuzzy finder for fast file switching.
- `draft_recovery.py`: Saves auto-snapshots of text using a background `DraftWorker(QThread)` to prevent UI stutter and data loss.
- `save_utils.py`, `session_manager.py`, `settings.py`: Enforces atomic disk writes (`tempfile.mkstemp` + `os.fsync` + `os.replace`) to strictly guarantee physical disk writes and eliminate 0-byte corruption on crash, while persisting scroll position, zoom, and PDF page numbers across sessions.
- `release_hash.py`: Standalone script for computing SHA-256 hashes for the packaged installer or bundled executable used in GitHub Releases, Winget, and other package-manager distribution flows.

### Release Distribution
- The release pipeline is a Windows-only GitHub Actions flow that builds EleViewer with Nuitka, packages it with Inno Setup, and publishes an installer to GitHub Releases.
- The Winget manifest targets the release installer artifact rather than a stale `latest/download/EleViewer.exe` path.
- The installer script and release helper are intentionally aligned with the same artifact naming so the packaged output is easier to verify.

---

## Contributing Workflow

1. **Read the code first**: Start with the relevant viewer or UI module, then update the docs if behavior changes.
2. **Keep the app lightweight**: Prefer smaller rendering changes, response-time improvements, and cache reuse over new dependencies.
3. **Testing**: Run `python main.py` for manual smoke checks, or execute the repository's root `test_*.py` suites with `pytest` (for example `pytest -s test_all_ui_actions.py`).
4. **Pull Requests**: Explain *why* a feature is needed, not just *what* it does. Ensure it doesn't break the "Offline First" or "Zero Telemetry" rules.

Welcome aboard!

