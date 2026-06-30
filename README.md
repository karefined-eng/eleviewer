# EleViewer

A lightweight Windows text editor supporting **DOCX**, **XLSX**, **MD**, and **TXT** file formats. Built with Python and PySide6.

## Features

✅ **Multi-format support**
- Word documents (.docx) — view and edit
- Excel spreadsheets (.xlsx) — view, edit cells, multiple sheets
- Markdown files (.md) — full editing
- Plain text (.txt) — full editing

✅ **Advanced editing features**
- **Multi-tab interface** — work with multiple files simultaneously
- **Session restore** — automatically reopens tabs from your last session
- **Quick switcher (Ctrl+P)** — fuzzy search and jump to recent/pinned files (VSCode-style)
- **Pinned files** — keep frequently used files at the top for quick access
- **Recent files menu** — fast access to last 10 files with automatic validation
- **Autosave** — automatic background saving (optional)
- **File validation** — removes deleted files from recent list

✅ **Clean, Dark UI**
- Professional dark luxury editorial aesthetic
- Responsive interface built with PySide6
- Fast and lightweight

## System Requirements

- **Windows 10/11**
- **Python 3.9+** (if running from source)
- 16MB disk space (minimal)

## Installation

### Option 1: Use the .exe (Recommended for End Users)

1. Download `EleViewer.exe` from the [releases](https://github.com/karefined-eng/eleviewer/releases) page
2. Run it — no installation needed
3. Start editing!

### Option 2: Run from Source

1. Clone the repository:
   ```bash
   git clone https://github.com/karefined-eng/eleviewer.git
   cd eleviewer
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the app:
   ```bash
   python main.py
   ```

## Building the .exe

If you want to rebuild the executable:

```bash
pip install pyinstaller
pyinstaller --noconsole --onefile main.py
```

The executable will be generated at `dist/main.exe`.

## Usage

### Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| **Ctrl+N** | New tab |
| **Ctrl+O** | Open file |
| **Ctrl+S** | Save file |
| **Ctrl+Shift+S** | Save as |
| **Ctrl+W** | Close tab |
| **Ctrl+Shift+T** | Reopen closed tab |
| **Ctrl+P** | Quick switcher (search files) |

### Features in Action

**Session Restore**
- Open multiple files
- Close EleViewer
- Reopen it → all your tabs come back

**Quick Switcher (Ctrl+P)**
- Press Ctrl+P
- Type filename to search
- Use ↑↓ to navigate, Enter to select
- Searches both recent and pinned files

**Pinned Files**
- Access via **File > Pinned Files** menu
- Pin frequently used files for quick access

## Project Structure

```
eleviewer/
├── main.py                 # Entry point
├── ui.py                   # Main window & tab management
├── editor.py               # Text editor widget
├── file_handler.py         # File type router (factory pattern)
├── docx_viewer.py          # DOCX support
├── xlsx_viewer.py          # XLSX support
├── autosave.py             # Automatic saving
├── recent_files.py         # Recent files with validation
├── pinned_files.py         # Pinned files management
├── session_manager.py      # Session restore
├── quick_switcher.py       # Ctrl+P quick switcher
├── settings.py             # App settings
├── markdown_renderer.py    # Markdown rendering helpers
├── requirements.txt        # Python dependencies
└── assets/                 # App assets (if any)
```

## Dependencies

- **PySide6** — UI framework
- **python-docx** — DOCX file handling
- **openpyxl** — XLSX file handling

See `requirements.txt` for exact versions.

## Architecture

EleViewer uses a **factory pattern** for file type handling:

1. **file_handler.py** — Routes files to the correct viewer
   - `.docx` → DocxViewer
   - `.xlsx` → XlsxViewer
   - `.txt`/`.md` → EditorTab (plain text)

2. **viewer modules** — Each format has its own widget
   - Save/load specific to the format
   - Compatible interface for the tab system

3. **session_manager.py** — Preserves open tabs between sessions

4. **quick_switcher.py** — Fuzzy search over files (VSCode-inspired)

## Data Storage

User data is stored in the Windows standard location:
```
C:\Users\<YourName>\AppData\Roaming\EleViewer\
```

This directory contains:
- `recent_files.json` — Recent files list
- `pinned_files.json` — Pinned files list
- `session.json` — Last session tabs
- `settings.json` — App settings

## Limitations

- **DOCX editing** — Plain text extraction and restructuring (preserves content, not all formatting)
- **XLSX editing** — Cell editing and multiple sheets (basic; no formulas or advanced formatting)
- **Merged cells** — Read-only in Excel files

## Contributing

This is an archived project. Feel free to fork it and build on it!

## License

MIT License — see LICENSE file for details.

## Author

Built by **Elevon (ka.refined)** — Digital entrepreneur & developer based in Accra, Ghana.

---

**Questions or want to report a bug?** Open an issue on GitHub!
