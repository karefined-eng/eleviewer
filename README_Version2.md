# EleViewer

A lightweight Windows document editor supporting **DOCX**, **XLSX**, **MD**, **TXT**, **CSV**, and **PDF**. Built with Python and PySide6.

## Highlights

- **Lucide-style icon toolbar** with hamburger menu
- **Multi-vault sidebar** — add multiple course-material folders, cached between sessions
- **Markdown** — view mode, simple plain-text edit (double-click), syntax edit (triple-click or pencil icon)
- **PDF** — Edge-like fit-to-page, high-DPI rendering, arrow-key navigation, Windows TTS
- **Tabbed web panel** — Google, Gemini, ChatGPT, etc. with persisted tabs
- **Excel** — Google Sheets-style bottom sheet tabs
- **Draggable editor tabs**

## Installation

```bash
pip install -r requirements.txt
python main.py
```

Optional web panel: `pip install PySide6-WebEngine`

## Vault

1. **Vault → Add Vault...** or toolbar **+** in the vault panel
2. Switch vaults via the dropdown at the top of the sidebar
3. **Ctrl+Shift+E** toggles the panel
4. Expand folders with the chevron; double-click files to open
5. **Settings → Vault** — show all files (for code projects) vs documents only

Multiple vaults are saved in `%APPDATA%\EleViewer\settings.json`.

## Markdown editing

| Action | Result |
|--------|--------|
| Default open | Rendered view |
| Double-click preview | Simple plain-text edit (no `#` or `**`) |
| Triple-click preview | Syntax / markdown edit |
| Pencil icon | Syntax edit |
| Book icon | Back to rendered view |

## PDF

| Control | Action |
|---------|--------|
| Fit page / Fit width | Toolbar buttons |
| Arrow keys | Change pages |
| Speaker | Read aloud (Windows voices via pyttsx3) |
| Settings → PDF | Default fit mode and render quality |

## Web panel

- Globe toolbar icon toggles the panel
- **+** or **Ctrl+T** adds a tab
- Tabs and URLs persist between sessions
- Settings → Web sets default URL for new tabs

## Menus

- **File** — New, Open, Save, Close
- **Vault** — Add, remove, toggle panel
- **Session** — Reopen tab, quick switcher, recent/pinned
- **Settings** — tabbed preferences
- Toolbar **menu icon** — quick access to common actions

## Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+Shift+E | Toggle vault |
| Ctrl+Shift+T | Reopen tab |
| Ctrl+T | New web tab (when web panel focused) |
| Ctrl+P | Quick switcher |

## Dependencies

PySide6, python-docx, openpyxl, markdown, PyMuPDF, pyttsx3, PySide6-WebEngine (optional)
