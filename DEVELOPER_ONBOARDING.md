# Developer Onboarding: Welcome to the Sovereignty Workstation

If you are reading this, you are contributing to **EleViewer**—a minimalist, multi-tabbed study workstation built on PySide6. 

Before you write a single line of code, you must understand our philosophy.

## The Prime Directives
1. **Zero Telemetry**: No analytics, no tracking, no hidden pings home. User data is sacred and lives locally. (Note: Unhandled crashes are caught by a secure `sys.excepthook` which allows the user to *opt-in* to reporting the stack trace directly to our Vercel feedback API.)
2. **Speed over Features**: If a feature requires a 5-second loading screen or a 200MB dependency, we don't build it. The app must run on old student laptops without lag.
3. **Offline First**: The app must function 100% offline. The Web Panel is an *augmentative* feature, not a core dependency.

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

### Sub-systems
- `vault_explorer.py`: The left sidebar for file navigation.
- `quick_switcher.py`: The `Ctrl+Q` fuzzy finder powered by an embedded SQLite FTS5 database.
- `draft_recovery.py`: Saves aggressive snapshots of text every 60 seconds to prevent data loss.

---

## Contributing Workflow

1. **Check the Ledger**: Read `PROJECT_LOG.md` before starting work. It contains historical context on why certain decisions were made (e.g., why we dropped `fitz` for PDF).
2. **Design System**: Ensure UI changes match `eleviewer-site/app/globals.css`. 
3. **Testing**: Run `main.py` directly. Do not build the `.exe` via PyInstaller for testing—it takes too long and obscures stack traces.
4. **Pull Requests**: Explain *why* a feature is needed, not just *what* it does. Ensure it doesn't break the "Offline First" or "Zero Telemetry" rules.

Welcome aboard!
