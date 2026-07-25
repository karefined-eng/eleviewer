# Developer Onboarding: Welcome to the Sovereignty Workstation

If you are reading this, you are contributing to **EleViewer**—a minimalist, multi-tabbed study workstation built on PySide6. 

Before you write a single line of code, you must understand our philosophy.

## The Prime Directives
1. **Zero Telemetry**: No analytics, no tracking, no hidden pings home. User data is sacred and lives locally. (Note: Unhandled crashes are caught by a secure `sys.excepthook` which allows the user to *opt-in* to reporting the stack trace directly to our Vercel feedback API.)
2. **Speed over Features**: If a feature requires a 5-second loading screen or a 200MB dependency, we don't build it. The app must run on old student laptops without lag.
3. **Offline First**: The app must function 100% offline. The Web Panel is an *augmentative* feature, not a core dependency.

---

## Copywriting & Communication Standards (The Paul Graham / Ogilvy Framework)
To maintain our distraction-free student workflow, all user-facing copy (in desktop UI widgets, modals, feedback dialogs, and website components) must adhere to globally praised copywriting principles:
1. **Middle-Grader Readability (Flesch-Kincaid Grade 6–8 Rule)**: Keep vocabulary accessible to a 6th-to-8th grade reading level (ages 11–13). Avoid bloated corporate jargon, obscure acronyms, and convoluted sentence structures.
2. **Write Like You Talk**: Follow the Paul Graham and David Ogilvy principle of direct, conversational English. Speak to the user as a respected peer and fellow builder.
3. **Outcome-Driven Intake**: When soliciting feedback or reporting errors, focus on user empowerment rather than system failure. Use inviting, direct prompts (e.g., *"Is there something you wish EleViewer could do? Share your idea directly with the developer — every submission is reviewed for our upcoming builds."*).

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
- `pdf_viewer.py`: Uses `QPdfView` (native Qt module, not PyMuPDF). Features Text-to-Speech integration via `tts_engine.py`.
- `editor.py`: The text/Markdown editor. Includes live syntax highlighting and markdown preview generation.
- `xlsx_viewer.py` & `csv_viewer.py`: Uses `openpyxl` and standard library `csv` to render spreadsheets natively into `QTableWidget`.
- `docx_viewer.py`: Converts Word docs to HTML using `python-docx` for rich rendering.

### Sub-systems & Concurrency
- `vault_explorer.py` & `vault_indexer.py`: The left sidebar for file navigation, paired with `vault_search.py` and `vault_indexer.py` (SQLite FTS5 full-text background search).
- `quick_switcher.py`: The `Ctrl+Q` fuzzy finder for fast file switching.
- `draft_recovery.py`: Saves auto-snapshots of text using a background `DraftWorker(QThread)` to prevent UI stutter and data loss.
- `save_utils.py`, `session_manager.py`, `settings.py`: Enforces atomic disk writes (`tempfile.mkstemp` + `os.replace`) to eliminate 0-byte corruption on crash, while persisting scroll position, zoom, and PDF page numbers across sessions.
- `release_hash.py`: Standalone script for computing executable SHA-256 release hashes.

---

## Contributing Workflow

1. **Check the Ledger**: Read `PROJECT_LOG.md` before starting work. It contains historical context on why certain decisions were made (e.g., why we dropped `fitz` for PDF).
2. **Design System**: Ensure UI changes match `eleviewer-site/app/globals.css`. 
3. **Testing**: Run `main.py` directly for manual validation, or execute test suites archived in `OneDrive\Documents\EleViewer\tests\`.
4. **Pull Requests**: Explain *why* a feature is needed, not just *what* it does. Ensure it doesn't break the "Offline First" or "Zero Telemetry" rules.

Welcome aboard!
