# EleViewer

![Version](https://img.shields.io/github/v/release/karefined-eng/eleviewer?label=version)
![License](https://img.shields.io/github/license/karefined-eng/eleviewer)
![Downloads](https://img.shields.io/github/downloads/karefined-eng/eleviewer/total)

A lightweight Windows document editor supporting **DOCX**, **XLSX**, **MD**, **TXT**, **CSV**, **HTML/HTM**, and **PDF**. Built with Python and PySide6.

## 📚 Features

### 📁 File Support
Opens & edits **DOCX, XLSX, PDF, MD, TXT and HTML** — all in one workspace.

### 🔊 Reading & Study Tools
- **PDF text-to-speech** — reads lectures/PDFs aloud for hands-free studying.
- **Persistent bookmarks** — never lose your place, even in 400-page textbooks.

### 🗂️ Organization
- **Vault sidebar** — one-click access to course folders (Alt+V).
- **Quick switcher** — fuzzy file search like VSCode (Ctrl+Q).
- **Session restore** — reopens all tabs right where you left off.
- **Reopen closed tab** (Ctrl+Shift+T).

### ✨ Extras
- **Built-in web browser panel**, side-by-side with notes (Ctrl+T).
- **Bookmarks panel toggle** (Ctrl+Alt+B).

### 💻 Specs
- 16 MB, single portable `.exe` — no install needed.
- Windows 10/11.
- No account, no telemetry — files stay local.
- MIT licensed, open source (Python + PySide6).
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
| **Ctrl+D** | Bookmark current PDF page |
| **Ctrl+T** | Open Web Browser Panel / New Web Tab |
| **Alt+S** | Open Settings |

### Feature Details
- **Markdown**: Double-click the preview for a simple plain-text edit (hides markdown symbols). Triple-click for a full syntax edit.
- **PDFs**: Use the toolbar to fit-to-page/width, use arrow keys to navigate, and click the speaker icon to read aloud.
- **Vaults**: Add multiple project folders. Switch between them via the sidebar dropdown. Set up vaults via the **+** icon.
- **Web Panel**: Persists URLs between sessions. Configure the default new tab URL in the Settings menu.

## 🛠️ Building the Executable

To create a standalone `.exe`:
```bash
pip install pyinstaller
pyinstaller EleViewer.spec
```
The executable will be generated in the `dist/` directory.

## 📁 Architecture & Structure

EleViewer uses a **factory pattern** for file handling. `file_handler.py` routes files to the correct viewer module (e.g., `docx_viewer.py`, `xlsx_viewer.py`, `pdf_viewer.py`).

Key directories and modules:
- `main.py` & `ui.py` — Entry point and main window tab management.
- `editor.py` & `markdown_renderer.py` — Text and markdown editors.
- `pdf_viewer.py`, `docx_viewer.py`, `xlsx_viewer.py` — Format-specific viewers.
- `vault_explorer.py`, `web_panel.py`, `bookmark_panel.py` — Sidebar panels.
- `find_replace.py`, `instance_lock.py` — Cross-editor find/replace and single-instance locking.
- `session_manager.py`, `autosave.py`, `settings.py` — State and persistence.
- Data is stored in `%APPDATA%\EleViewer\` (`recent_files.json`, `settings.json`, etc.)

## 🔧 Troubleshooting

- **ModuleNotFoundError (e.g., 'PySide6', 'docx')**: Ensure you've run `pip install -r requirements.txt`.
- **Web panel not available**: Run `pip install PySide6-WebEngine`.
- **PDF read-aloud not working**: Ensure `pyttsx3` is installed and Windows speech voices are enabled in OS settings.

## 🤝 Contributing

This project is open-source. Feel free to fork it, create a branch, and submit a pull request!

## 📄 License

MIT License — see the LICENSE file for details.

## ✍️ Author
Built by **Elevon (ka.refined)** — Digital entrepreneur & developer based in Accra, Ghana.
