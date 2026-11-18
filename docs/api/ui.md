# API Reference: ui.py

## MainWindow

**`class MainWindow(QMainWindow)`**

The main application window. Manages tabs, toolbars, side panels, file opening, session restore, and global shortcuts.

### Constructor

```python
MainWindow()
```

### Key Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `tabs` | QTabWidget | Left tab group (primary document tabs) |
| `tabs_right` | QTabWidget | Right tab group (split view documents) |
| `editor_tabs_splitter` | QSplitter | Splitter between left and right tab groups |
| `vault_panel` | VaultExplorer | Left sidebar file navigator |
| `bookmarks_panel` | BookmarkPanel | Bookmarks sidebar |
| `tts_bar` | TtsReaderBar | Read-aloud control bar |
| `find_replace_panel` | FindReplaceWidget | Global find/replace panel |
| `tts_engine` | TtsEngine | Text-to-speech engine |
| `autosaver` | AutoSaver | Auto-save worker |

### File Operations

| Method | Shortcut | Description |
|--------|----------|-------------|
| `open_file()` | Ctrl+O | Open a file dialog and load the selected file |
| `save_file()` | Ctrl+S | Save the current document |
| `save_file_as()` | Ctrl+Shift+S | Save current document with a new name |
| `new_tab()` | Ctrl+N | Create a new blank note tab |
| `close_tab(index)` | Ctrl+W | Close the tab at the given index |
| `reopen_closed_tab()` | Ctrl+Shift+T | Reopen the most recently closed tab |

### Split View (Doc↔Doc)

| Method | Shortcut | Description |
|--------|----------|-------------|
| `toggle_split_view()` | Ctrl+\ | Toggle side-by-side document view. Moves current tab between left/right panes |

When split view is active, `tabs_right` becomes visible and the editor area is split 50/50 between the two tab groups. When disabled, all tabs move back to `tabs`.

### Undo/Redo

| Method | Shortcut | Description |
|--------|----------|-------------|
| `undo_current()` | Ctrl+Z | Undo on the currently focused editor |
| `redo_current()` | Ctrl+Y | Redo on the currently focused editor |

Routes to `QTextEdit.undo()`/`redo()` for EditorTab and MarkdownViewer.

### Print

| Method | Shortcut | Description |
|--------|----------|-------------|
| `print_file()` | Ctrl+P | Open print dialog and print the current document |
| `export_pdf()` | — | Export current document to a PDF file |
| `_render_to_printer(editor, printer)` | — | Internal: render any viewer type to a QPrinter |

Supports printing for: PdfViewer (page-by-page rendering), MarkdownViewer/HtmlViewer/EditorTab (QTextDocument), ImageViewer (pixmap).

### PDF Table of Contents

| Method | Shortcut | Description |
|--------|----------|-------------|
| `toggle_pdf_toc()` | Ctrl+Shift+L | Toggle TOC sidebar on the current PdfViewer |

### Tab Navigation

| Method | Shortcut | Description |
|--------|----------|-------------|
| `next_tab()` | Ctrl+Tab | Switch to next tab |
| `prev_tab()` | Ctrl+Shift+Tab | Switch to previous tab |
| `switch_to_tab_if_open(path)` | — | Switch to an already-open tab for the given file path |

### Global Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+N` | New tab |
| `Ctrl+O` | Open file |
| `Ctrl+S` | Save |
| `Ctrl+Shift+S` | Save As |
| `Ctrl+W` | Close tab |
| `Ctrl+Z` | Undo |
| `Ctrl+Y` | Redo |
| `Ctrl+F` | Find in document |
| `Ctrl+H` | Replace |
| `Ctrl+Shift+F` | Search vault |
| `Ctrl+Q` | Quick switcher |
| `Ctrl+T` | Open web tab |
| `Ctrl+\` | Toggle split view |
| `Ctrl+Shift+L` | Toggle PDF TOC |
| `Ctrl+D` | Bookmark current tab |
| `Ctrl+Alt+B` | Toggle bookmarks panel |
| `Ctrl+Alt+V` | Toggle vault panel |
| `Alt+V` | Toggle vault panel |
| `Alt+E` | Quick Note (system-wide hotkey) |
| `Alt+S` | Settings |
| `F9` | Read aloud / Toggle TTS bar |
| `F1` | Getting Started guide |
| `Esc` | Hide panels / escape |

### Session Management

- `restore_session()` — Restore open tabs from previous session
- `save_session()` — Persist current tab state
- `reopen_closed_tab()` — Reopen from closed tabs stack
- `DraftManager` — Crash-safety snapshots of modified tabs

### Accessibility

All main toolbar actions have `accessibleName` and `accessibleDescription` set for screen-reader support.
