# Quick Start Guide

## For End Users

1. Download `main.exe` from the releases page
2. Run it
3. Start editing!

No installation needed.

## For Developers / Running from Source

### Prerequisites
- Windows 10/11
- Python 3.9 or higher
- Git

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/karefined-eng/eleviewer.git
   cd eleviewer
   ```

2. **Create a virtual environment (optional but recommended)**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the app**
   ```bash
   python main.py
   ```

### Building the .exe

If you want to create a standalone executable:

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
- Ensure Windows speech voices are installed in Settings → Time & Language → Speech

**The app doesn't start**

### Project Structure

```
eleviewer/
├── main.py                  # Entry point — run this to start
├── ui.py                    # Main window
├── editor.py                # Text editor widget
├── file_handler.py          # File type routing
├── docx_viewer.py           # DOCX support
├── xlsx_viewer.py           # XLSX support
├── session_manager.py       # Session persistence
├── quick_switcher.py        # Ctrl+P dialog
├── recent_files.py          # Recent files menu
├── pinned_files.py          # Pinned files
├── autosave.py              # Auto-save system (atomic writes, settings-aware)
├── paths.py                 # Centralized app data paths
├── theme.py                 # Centralized dark theme styles
├── settings.py              # User settings persistence
├── settings_dialog.py       # Settings UI
├── save_utils.py            # Atomic file writes
├── markdown_renderer.py     # Markdown view/edit toggle
├── pdf_viewer.py            # PDF viewing with zoom and TTS
├── pdf_tts.py                 # Windows native read-aloud
├── vault_explorer.py          # Multi-vault folder sidebar
├── web_panel.py               # Tabbed web browser panel
├── markdown_utils.py          # Plain-text markdown conversion
├── pdf_tts.py                 # Windows native read-aloud
├── icons.py                   # Lucide-style icon loader
├── icons/                     # SVG icon assets
├── requirements.txt         # Dependencies
└── data/                    # User data (created at runtime)
```

### Key Modules

- **file_handler.py** — Determines which viewer to use based on file extension
- **docx_viewer.py** — DOCX file viewing and editing
- **xlsx_viewer.py** — XLSX file viewing and editing
- **session_manager.py** — Saves/restores open tabs between sessions
- **quick_switcher.py** — Ctrl+P fuzzy file search dialog

### Development Tips

**Adding a new file format:**

1. Create a new viewer module (e.g., `pdf_viewer.py`)
2. Create a class that inherits from QWidget
3. Implement required methods: `toPlainText()`, `to_format_bytes()`, `textChanged` signal
4. Update `file_handler.py` to route to your new viewer
5. Update `ui.py` file dialogs to include the new extension

**Modifying the UI:**

- Main window logic is in `ui.py`
- File menu and shortcuts are configured in `create_menu()`
- Tab system uses `QTabWidget`

**Data storage:**

All user data is stored in:
```
C:\Users\<YourName>\AppData\Roaming\EleViewer\
```

This includes:
- `recent_files.json` — Recent files list
- `pinned_files.json` — Pinned files
- `session.json` — Last session tabs

### Running Tests

Manual checks for iteration 2:

- Add multiple vaults; expand subfolders with chevron; restart app — vaults should persist
- Markdown: double-click preview for simple edit; triple-click for syntax
- PDF: should open at readable size; TTS speak button on text pages
- Web panel: add multiple tabs (Gemini, Google); restart — tabs should restore
- File menu: Session → Reopen Tab (no label overflow)

---

**Need help?** Open an issue on GitHub!
