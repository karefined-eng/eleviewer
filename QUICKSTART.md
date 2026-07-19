# Quick Start Guide

## For End Users

1. Download `main.exe` from the releases page.
2. Run it.
3. Start editing.

No installation is required for the packaged executable.

## For Developers / Running from Source

### Prerequisites
- Windows 10/11
- Python 3.9 or higher
- Git

### Setup

1. Clone the repository:
   ```bash
git clone https://github.com/karefined-eng/eleviewer.git
cd eleviewer
```

2. Create a virtual environment (optional but recommended):
   ```bash
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies:
   ```bash
pip install -r requirements.txt
```

4. Run the app:
   ```bash
python main.py
```

### Optional Web Panel

Install Qt WebEngine if you want the in-app browser panel:

```bash
pip install PySide6-WebEngine
```

### Building the .exe

If you want a standalone executable:

```bash
pip install pyinstaller
pyinstaller --noconsole --onefile main.py
```

The executable will be generated at `dist/main.exe`.

### Troubleshooting

**Error: "No module named 'PySide6'"**
- Run: `pip install -r requirements.txt`

**Error: "ModuleNotFoundError: No module named 'docx'"**
- Run: `pip install python-docx`

**Error: "ModuleNotFoundError: No module named 'openpyxl'"**
- Run: `pip install openpyxl`

**Error: "No module named 'fitz'" or PDF won't open**
- Run: `pip install PyMuPDF`

**Error: "No module named 'markdown'"**
- Run: `pip install markdown`

**Optional: Web panel not available**
- Run: `pip install PySide6-WebEngine`

**PDF read-aloud not working**
- Run: `pip install pyttsx3`
- Ensure Windows speech voices are installed in Settings → Time & Language → Speech.

### Project Structure

```
eleviewer/
├── main.py                  # Entry point
├── ui.py                    # Main window
├── editor.py                # Text editor widget
├── file_handler.py          # File type routing
├── docx_viewer.py           # DOCX support
├── xlsx_viewer.py           # XLSX support
├── session_manager.py       # Session persistence
├── quick_switcher.py        # Ctrl+Q dialog
├── recent_files.py          # Recent files menu
├── pinned_files.py          # Pinned files
├── autosave.py              # Auto-save system
├── paths.py                 # Centralized app data paths
├── theme.py                 # Centralized dark theme styles
├── settings.py              # User settings persistence
├── settings_dialog.py       # Settings UI
├── save_utils.py            # Atomic file writes
├── markdown_renderer.py     # Markdown view/edit toggle
├── pdf_viewer.py            # PDF viewing with QPdfView and TTS
├── pdf_tts.py               # Windows native read-aloud
├── vault_explorer.py        # Multi-vault folder sidebar
├── web_panel.py             # Tabbed web browser panel
├── markdown_utils.py        # Plain-text markdown conversion
├── bookmark_manager.py      # Bookmark storage and persistence
├── bookmark_panel.py        # Bookmarks GUI sidebar
├── icons.py                 # Lucide-style icon loader
├── icons/                   # SVG icon assets
├── requirements.txt         # Dependencies
└── data/                    # User data (created at runtime)
```

### Key Modules

- **file_handler.py** — determines which viewer to use by file extension
- **docx_viewer.py** — DOCX viewing and editing
- **xlsx_viewer.py** — XLSX viewing and editing
- **pdf_viewer.py** — PDF viewing with QPdfView and TTS
- **session_manager.py** — saves/restores open tabs between sessions
- **quick_switcher.py** — Ctrl+Q fuzzy file search dialog
