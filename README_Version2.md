# EleViewer

A lightweight Windows text editor supporting **DOCX**, **XLSX**, **MD**, **TXT**, and **PDF** file formats. Built with Python and PySide6.

## Features

✅ **Multi-format support**
- Word documents (.docx) — view and edit (basic text editing)
- Excel spreadsheets (.xlsx) — view, edit cells, multiple sheets
- Markdown files (.md) — editing with live HTML preview (tables, code blocks)
- Plain text (.txt) — full editing
- PDF files (.pdf) — read-only viewing with page navigation

✅ **Advanced editing features**
- **Multi-tab interface** — work with multiple files simultaneously
- **Session restore** — reopens tabs from your last session (reloads saved files from disk)
- **Quick switcher (Ctrl+P)** — fuzzy search over recent/pinned files (VSCode-style)
- **Reopen closed tab (Ctrl+Shift+T)**
- **Pinned files** — keep frequently used files at the top
- **Recent files menu** — last 10 files with automatic validation
- **Autosave** — optional background saving with atomic writes (configurable in Settings)
- **Quit prompt** — warns when closing with unsaved changes
- **Status bar** — shows current file, path, and save/autosave feedback
- **Optional web panel** — embedded browser with configurable URL

✅ **Clean, Dark UI**
- Centralized dark theme across all viewers
- Responsive interface built with PySide6
- Fast and lightweight

## System Requirements

- **Windows 10/11**
- **Python 3.9+** (if running from source)
- ~50MB disk space with all dependencies

## Installation

### Option 1: Use the .exe (Recommended for End Users)

1. Download `main.exe` from the [releases](https://github.com/karefined-eng/eleviewer/releases) page
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

3. **Optional** — embedded web panel:
   ```bash
   pip install PySide6-WebEngine
   ```

4. Run the app:
   ```bash
   python main.py
   ```

## Settings

Open **File → Settings** to configure:

- **Autosave** — enable/disable and set interval (2–300 seconds)
- **Web panel URL** — default homepage for the embedded browser

Settings are stored in `%APPDATA%\EleViewer\settings.json`.

## Dependencies

| Package | Purpose |
|---------|---------|
| PySide6 | GUI framework |
| python-docx | Word document support |
| openpyxl | Excel spreadsheet support |
| markdown | Rich markdown preview |
| PyMuPDF | PDF viewing |
| PySide6-WebEngine | Optional embedded web panel |

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+N | New tab |
| Ctrl+O | Open file |
| Ctrl+S | Save |
| Ctrl+Shift+S | Save As |
| Ctrl+W | Close tab |
| Ctrl+Shift+T | Reopen closed tab |
| Ctrl+P | Quick switcher |

## User Data

All user data is stored in:
```
C:\Users\<YourName>\AppData\Roaming\EleViewer\
```

This includes recent files, pinned files, session state, and settings.
