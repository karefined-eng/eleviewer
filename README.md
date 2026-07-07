# EleViewer

A lightweight Windows text editor supporting **DOCX**, **XLSX**, **MD**, and **TXT** file formats. Built with Python and PySide6.

## Features

✅ **Multi-format support**
- Word documents (.docx) — view and edit
- Excel spreadsheets (.xlsx) — view, edit cells, multiple sheets
- PDF files (.pdf) — view, double-page layout, rotation, smart TOC sidebar, native text-to-speech
- Markdown files (.md) — full editing with split-view HTML preview (WebView2) and rich-text toolbar
- Plain text (.txt) — full editing

✅ **Advanced editing features**
- **Rich Formatting Toolbar** — bold, italic, strikethrough, headings, lists, tables, links (with Lucide icons)
- **Multi-tab interface** — work with multiple files simultaneously
- **Vault Sidebar (Alt+V)** — organize and open files easily from designated folder vaults
- **Web Browser Panel (Ctrl+T)** — side-by-side web browsing directly in the editor using Edge WebView2
- **PDF & File Bookmarks** — persistent bookmarking system with a dedicated sidebar panel
- **Session restore** — automatically reopens tabs from your last session
- **Quick switcher (Ctrl+Q)** — fuzzy search and jump to recent/pinned files (VSCode-style)
- **Pinned files** — keep frequently used files at the top for quick access
- **Recent files menu** — fast access to last 10 files with automatic validation
- **Default Save Folder** — automatically route all new files to a preferred directory

✅ **Clean, Dark UI**
- Professional dark luxury editorial aesthetic
- Responsive interface built with PySide6
- Crisp white Lucide SVG icons across the app

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
| **Ctrl+N** | New File picker (dropdown format selection) |
| **Ctrl+O** | Open file |
| **Ctrl+S** | Save file |
| **Ctrl+Shift+S** | Save as |
| **Ctrl+W** | Close tab |
| **Ctrl+Shift+T** | Reopen closed tab |
| **Ctrl+Q** | Quick switcher (search files) |
| **Alt+V** | Toggle Vault (Folder Explorer) |
| **Ctrl+Alt+B**| Toggle Bookmarks Panel |
| **Ctrl+D** | Bookmark current page (PDF) |
| **Alt+S** | Open Settings |
| **Ctrl+T** | Open Web Browser Panel / New Web Tab |

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
├── editor.py               # Text/Markdown editor widget with rich toolbar
├── file_handler.py         # File type router (factory pattern)
├── docx_viewer.py          # DOCX support
├── xlsx_viewer.py          # XLSX support
├── pdf_viewer.py           # PDF support with PyMuPDF
├── vault_explorer.py       # Vault/Folder sidebar management
├── web_panel.py            # Edge WebView2 browsing panel
├── bookmark_panel.py       # Bookmarks sidebar
├── bookmark_manager.py     # Bookmark persistence backend
├── autosave.py             # Automatic background saving
├── recent_files.py         # Recent files with validation
├── pinned_files.py         # Pinned files management
├── session_manager.py      # Session restore
├── quick_switcher.py       # Ctrl+Q quick switcher
├── settings.py             # App settings (JSON)
├── settings_dialog.py      # Settings GUI
├── markdown_renderer.py    # Markdown & HTML view toggling
├── icons.py                # Lucide SVG icon loader
├── theme.py                # Centralized dark theme stylesheet
└── icons/                  # SVG assets
```

## Dependencies

- **PySide6** — UI framework
- **PySide6-WebEngine** — QtWebEngine support for fallback web components
- **python-docx** — DOCX file handling
- **openpyxl** — XLSX file handling
- **PyMuPDF (fitz)** — PDF reading and rendering
- **Markdown** — Markdown to HTML rendering
- **pyttsx3** — Native Windows Text-to-Speech

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
