# EleViewer

![Version](https://img.shields.io/github/v/release/karefined-eng/eleviewer?label=version)
![License](https://img.shields.io/github/license/karefined-eng/eleviewer)
![Downloads](https://img.shields.io/github/downloads/karefined-eng/eleviewer/total)

A lightweight Windows document editor supporting **DOCX**, **XLSX**, **PPTX**, **MD**, **TXT**, **CSV**, **TSV**, **HTML/HTM**, and **PDF**. Built with Python and PySide6.

## 📚 Why EleViewer? (The Killer Features)

Instead of a generic text editor, EleViewer is an offline-first, interconnected study workstation. Here is what makes it unique:

### 🚀 The Unified Workspace
- **Split-Screen Web Panel (`Ctrl+T`)** — Browse the web directly alongside your local documents. Hyperlinks inside your PDFs or Markdown notes open in the Web Panel instead of kicking you out to Chrome, keeping your focus locked.
- **Vaults & Live Search (`Alt+V`)** — Connect your local study folders. The embedded **background search engine** silently scans everything, allowing you to instantly search across hundreds of course files simultaneously.
- **Session Restore** — Respects your time. If you close the app with 8 tabs open, a split-screen web page, and a specific PDF zoom, your entire workstation restores *exactly* as you left it on the next launch.
- **Persistent Bookmarks (`Ctrl+D`)** — Drop a bookmark on page 342 of a massive textbook or deep within a Markdown file. EleViewer remembers the exact scroll coordinate so you can jump back instantly later.
- **Global Quick Note (`Alt+E`)** — A system-wide Windows hotkey. Press `Alt+E` from anywhere in Windows to instantly bring EleViewer to the front and open a new blank scratchpad.

### 🔊 Advanced Reading & Data Tools
- **Hybrid Neural Text-to-Speech (`F9`)** — Reads documents aloud to you. It automatically uses high-quality Microsoft Neural voices when online, and seamlessly falls back to native Windows offline voices when disconnected.
- **Dual-Mode CSV Workstation** — Toggle instantly between a beautiful Table Grid View and a raw text editor, with automatic encoding detection so your data never looks garbled.
- **HTML Live Workstation** — Split-screen syntax editor with debounced live previews and 1-click migration into the Web Panel.

### 📁 Universal File Support (Zero Cloud Rendering)
Opens & edits **DOCX, XLSX, PPTX, PDF, MD, TXT, CSV, TSV and HTML/HTM** — all parsed natively using pure Python and PySide6.
- No heavy LibreOffice wrappers. No uploading files to a cloud renderer.
- **XLSX View-Only Mode** displays computed formula values to protect spreadsheet integrity.
- **Inline Image Extraction** natively renders embedded pictures inside DOCX and PPTX files.

### ✨ Security & Reliability
- **Atomic Writes** — zero-byte file corruption prevention on sudden crash or power loss.
- **Safe Previews** — strict security sanitization before rendering Markdown and HTML.
- **Smooth Performance** — draft recovery autosave and live vault searches run silently in the background to prevent your app from freezing.
- **Zero Telemetry** — no mandatory logins, no tracking. Includes an opt-in, privacy-focused secure crash reporter.

### 💻 Specs
- **~129 MB** compiled one-file portable Windows executable — no traditional installation required.
- **< 100 ms** cold-start latency.
- Windows 10/11 native integration (Jump Lists, AppUserModelID, ProgIDs).
- No account, **zero telemetry** — your files stay local. Includes an opt-in, **PII-stripped secure crash reporter** that automatically copies technical logs to your clipboard without exposing your personal username or file paths.
- **Flesch-Kincaid Compliant Copy** — all user-facing text follows the Paul Graham / Ogilvy "write like you talk" framework at a 6th-to-8th grade reading level for effortless scanning.
- **GNU GPLv3 licensed**, open source (Python + PySide6).
- Free forever, no ads.

## 🚀 Quick Start

### For End Users
1. Download the latest `EleViewer.exe` from the [releases](https://github.com/karefined-eng/eleviewer/releases) page.
2. Run `EleViewer.exe`. The current published release is portable and does not require a traditional installation.

### What’s new
- Faster preview refreshes for Markdown and HTML content while you type, with less wasted work and smoother updates.
- Reused rendered output for unchanged documents in the main preview paths, which helps reopen or revisit content more quickly.
- Cleaner guidance in this repo so the docs and agent instructions match the actual Python + PySide6 implementation.

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
   The requirements include PPTX parsing through `python-pptx`. For the embedded web panel, install the optional Qt WebEngine package as well: `pip install PySide6-WebEngine`. Without it, EleViewer remains usable for local documents but shows a clear warning when web-panel features are requested.

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

## 🛠️ Building Locally

The current desktop build path is a standard Python + PySide6 workflow.

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate

# 2. Install the app dependencies
pip install -r requirements.txt

# 3. Start the app
python main.py
```

If you want a packaged build, the release workflow uses Nuitka `--onefile` plus Inno Setup to produce a standalone portable `EleViewer.exe` and a Windows installer.

```bash
nuitka --onefile --plugin-enable=pyside6 --include-qt-plugins=sensible,styles --disable-console main.py
```

Release hashes can still be generated from the packaged artifact with:

```bash
python release_hash.py
```

## 📁 Architecture & Structure

EleViewer uses a **factory pattern** for file handling. `file_handler.py` routes files to the correct viewer module (e.g., `docx_viewer.py`, `xlsx_viewer.py`, `pdf_viewer.py`).

Key directories and modules:
- `main.py`, `ui.py`, `file_handler.py` — First stop for new contributors. `main.py` boots the app, `ui.py` manages the main window and toolbar, and `file_handler.py` routes supported file types to viewer modules.
- `editor.py` & `markdown_renderer.py` — Text and markdown editors with sanitized preview rendering.
- `pdf_viewer.py`, `docx_viewer.py`, `pptx_viewer.py`, `xlsx_viewer.py`, `csv_viewer.py` — Format-specific viewers.
- `vault_explorer.py`, `vault_search.py`, `vault_indexer.py` — Vault browser, live search, and a pure-Python SQLite FTS5 indexer.
- `draft_recovery.py`, `feedback_dialog.py` — Background `QThread` workers for auto-save and feedback submission.
- `session_manager.py`, `save_utils.py`, `settings.py` — Atomic writes, settings, and session scroll/zoom/page restore.
- `release_hash.py` — SHA-256 release hash generator used by the installer and GitHub release flow.
- Tests live in the repository root as `test_*.py` files. Use them to understand current behavior and validate your work.
- Data is stored in `%APPDATA%\EleViewer\` (`recent_files.json`, `settings.json`, `session.json`, `vault_index.db`, etc.)

## 🧪 Testing

All tests are run via `pytest` from the repository root.

To run the full suite with live output:
```bash
pytest -s
```

To run a specific test file:
```bash
pytest -s test_all_ui_actions.py
pytest -s test_markdown_renderer.py
```

If a test fails due to missing dependencies, ensure you have installed the requirements:
```bash
pip install -r requirements.txt
```

- **`ModuleNotFoundError` (e.g., 'PySide6', 'docx')**: Install missing packages from `requirements.txt`.
- **Web panel not available**: Install the optional web engine dependency:
  ```bash
  pip install PySide6-WebEngine
  ```
- **PDF read-aloud not working**: Ensure `pyttsx3` is installed and Windows speech voices are enabled in OS settings. For higher quality neural voices, install `edge-tts`.

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