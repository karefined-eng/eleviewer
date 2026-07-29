# EleViewer

![Version](https://img.shields.io/github/v/release/karefined-eng/eleviewer?label=version)
![License](https://img.shields.io/github/license/karefined-eng/eleviewer)
![Downloads](https://img.shields.io/github/downloads/karefined-eng/eleviewer/total)

A lightweight Windows document editor supporting **DOCX**, **XLSX**, **PPTX**, **MD**, **TXT**, **CSV**, **HTML/HTM**, and **PDF**. Built with Python and PySide6.

## 📚 Features

### 📁 File Support
Opens & edits **DOCX, XLSX, PPTX, PDF, MD, TXT, CSV and HTML** — all in one workspace.
- **XLSX View-Only Mode** — displays computed formula values (not raw formulas) in a read-only grid, protecting spreadsheet integrity while letting you study the data.
- **Image Placeholders** — DOCX and PPTX files with embedded images display `📷 [Image]` markers so you know where visuals exist, even in text-only rendering.
- **CSV Smart Encoding** — automatically detects file encoding via `chardet` so Excel-exported CSVs in Windows-1252, Latin-1, or UTF-8 render without garbled characters.
- **CSV Table Workstation** — dual Table Grid View ⇄ Raw Text View with interactive cell editing, row/column insertion, delimiter overrides, and non-destructive text preservation.
- **HTML Live Workstation** — split-screen syntax editor with debounced live preview, compact monochromatic styling, and 1-click migration into the right-hand Web Panel.
- **Global Hyperlink Interception** — clicks on web or file links in documents automatically open inside EleViewer's Web Panel or editor tabs without launching external system browsers.

### 🔊 Reading & Study Tools
- **Universal Text-to-Speech** — reads lectures, notes, Word docs, Markdown, CSV tables, HTML text, and PDFs aloud for hands-free studying (Toggle with `F9` or the toolbar button). Reads highlighted text selection or the full document.
- **Hybrid Neural TTS** — automatically uses high-quality Microsoft Neural voices (`edge-tts`) when online, and seamlessly falls back to native Windows SAPI5 voices (`pyttsx3`) when offline. No setup required.
- **Persistent Bookmarks** — drop a bookmark anywhere in your documents (`Ctrl+D`), even in 400-page textbooks or lengthy notes, and jump back instantly.

### 🗂️ Organization & System Tray
- **Vault sidebar** — one-click access to course folders (`Alt+V`).
- **SQLite FTS5 full-text indexer** — instant background search across all vault study files.
- **Quick switcher** — fuzzy file search like VSCode (`Ctrl+Q`).
- **Obsidian-inspired Web Panel** — persists URLs, with dedicated Refresh and Bookmark toolbar controls.
- **Session restore** — reopens all tabs right where you left off, preserving scroll position, zoom, and PDF page numbers.
- **System Tray Minimization** — minimize to tray on close with background notification and double-click restore.
- **Reopen closed tab** (`Ctrl+Shift+T`).

### ✨ Security & Reliability
- **Atomic Writes** — zero-byte file corruption prevention on sudden crash or power loss.
- **HTML XSS Sanitization** — `bleach` sanitization before rendering Markdown previews.
- **Symlink Path Traversal Guards** — strict canonical root validation to isolate local file access.
- **Off-Thread Concurrency** — draft recovery autosave, live vault search, and feedback submissions run on background `QThread` workers.
- **Dynamic UI Accents** — Status bar and active icons pop with your chosen theme color.
- **Lucide Icon Set** — clean, consistent, professional SVG icons throughout the UI, replacing legacy bulky glyphs.

### 💻 Specs
- **< 45 MB** compiled Native C++ executable — no heavy installer needed.
- **< 100 ms** cold-start latency.
- Windows 10/11 native integration (Jump Lists, AppUserModelID, ProgIDs).
- No account, **zero telemetry** — your files stay local. Includes an opt-in, **PII-stripped secure crash reporter** that automatically copies technical logs to your clipboard without exposing your personal username or file paths.
- **Flesch-Kincaid Compliant Copy** — all user-facing text follows the Paul Graham / Ogilvy "write like you talk" framework at a 6th-to-8th grade reading level for effortless scanning.
- **GNU GPLv3 licensed**, open source (Python + PySide6).
- Free forever, no ads.

## 🚀 Quick Start

### For End Users
1. Download `EleViewer.exe` from the [releases](https://github.com/karefined-eng/eleviewer/releases) page.
2. Run it — no installation needed!

### For Developers

**Prerequisites:** Windows 10/11, Python 3.9+, Git.

1. **Clone the repository:**
   ```bash
   git clone https://github.com/karefined-eng/eleviewer.git
   cd eleviewer
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   *(Optional)* For the web panel: `pip install PySide6-WebEngine`

4. **Run the application:**
   ```bash
   python main.py
   ```

## ⌨️ Keyboard Shortcuts & Usage

| Shortcut | Action |
|---|---|
| **Alt+E** | **System-Wide Quick Note / Summon** (Brings EleViewer to front & opens new note from anywhere in Windows) |
| **Ctrl+N** | New File picker |
| **Ctrl+O** / **Ctrl+S** | Open file / Save file |
| **Ctrl+Shift+S** | Save As |
| **Ctrl+W** | Close tab |
| **Ctrl+Shift+T** | Reopen closed tab |
| **Ctrl+F** | Find in document |
| **Ctrl+H** | Find and Replace |
| **Ctrl+Q** | Quick switcher (search files) |
| **Alt+V** | Toggle Vault (Folder Explorer) |
| **Ctrl+Alt+B**| Toggle Bookmarks Panel |
| **Ctrl+D** | Bookmark current file position / page |
| **F9** | Read Aloud / Toggle TTS Bar |
| **F1** | Open Getting Started Guide |
| **Ctrl+T** | Open Web Browser Panel / New Web Tab |
| **Alt+S** | Open Settings |

### Feature Details
- **Markdown**: Double-click the preview for a simple plain-text edit (hides markdown symbols). Triple-click for a full syntax edit. HTML previews are sanitized against XSS attacks.
- **PDFs**: Use the toolbar to fit-to-page/width, use arrow keys to navigate, and click the speaker icon to read aloud.
- **Vaults**: Add multiple project folders. Switch between them via the sidebar dropdown. Set up vaults via the **+** icon.
- **Web Panel**: Persists URLs between sessions. Configure the default new tab URL in the Settings menu.

## 🛠️ Building the Executable & SHA-256 Release Hashing

EleViewer v1.3.0 utilizes **Nuitka LTO** to compile Python directly to C++ machine code, paired with a **Rust/PyO3** extension for native asynchronous I/O (Vault Indexing).

```bash
# 1. Compile the Rust extensions
maturin develop --release

# 2. Compile the core application to C++ via Nuitka
nuitka --standalone --lto=yes --plugin-enable=pyside6 main.py

# 3. Generate SHA-256 hashes
python release_hash.py
```
The executable will be generated in the `dist/` directory alongside `EleViewer_SHA256.txt`.

## 📁 Architecture & Structure

EleViewer uses a **factory pattern** for file handling. `file_handler.py` routes files to the correct viewer module (e.g., `docx_viewer.py`, `xlsx_viewer.py`, `pdf_viewer.py`).

Key directories and modules:
- `main.py` & `ui.py` — Entry point, system tray, and main window tab management.
- `editor.py` & `markdown_renderer.py` — Text and markdown editors (with XSS sanitization).
- `pdf_viewer.py`, `docx_viewer.py`, `xlsx_viewer.py` — Format-specific viewers.
- `vault_explorer.py`, `vault_search.py`, `vault_indexer.py` — Vault browser, live search, and SQLite FTS5 indexer.
- `draft_recovery.py`, `feedback_dialog.py` — Background `QThread` workers for auto-backup and feedback.
- `session_manager.py`, `save_utils.py`, `settings.py` — Atomic writes, settings, and session scroll/zoom/page restore.
- `release_hash.py` — Automated SHA-256 release manifest generator.
- Test suites are archived in `OneDrive\Documents\EleViewer\tests\`.
- Data is stored in `%APPDATA%\EleViewer\` (`recent_files.json`, `settings.json`, `session.json`, `vault_index.db`, etc.)

- **ModuleNotFoundError (e.g., 'PySide6', 'docx')**: Ensure you've run `pip install -r requirements.txt`.
- **Web panel not available**: Run `pip install PySide6-WebEngine`.
- **PDF read-aloud not working**: Ensure `pyttsx3` is installed and Windows speech voices are enabled in OS settings. For higher quality neural voices, install `edge-tts` and `pygame` (requires internet connection).

## 🛡️ The Offline-First Philosophy
Independent utility apps often suffer from bloated file-rendering engines, heavy cloud dependencies, or unpolished UIs. EleViewer explicitly rejects this trend:
- **No Heavy Wrappers:** Instead of bundling a 200MB LibreOffice clone, we use pure-Python data extraction (like `mammoth` and `python-pptx`) to parse binary data and base64-encode it directly into PySide6 native UIs.
- **Zero Cloud Rendering:** No documents are ever uploaded to a server to be rendered.
- **Graceful Degradation:** Cloud-assisted features (like Microsoft Neural TTS) seamlessly fall back to local Windows COM APIs when offline, ensuring your study session never crashes in a dead zone.

## 🤝 Contributing

This project is open-source. Feel free to fork it, create a branch, and submit a pull request!

## 📄 License

GNU GPLv3 License — see the LICENSE file for details.

## ✍️ Author
Built by **[karefined-eng](https://github.com/karefined-eng)**