# API Reference: editor.py

## EditorTab

**`class EditorTab(QWidget)`**

Text/Markdown editor widget using `QTextEdit`. Handles plain text, Markdown, and HTML files. Supports formatting toolbar (bold, italic, underline, strikethrough, headings, lists, tables, links) and undo/redo.

### Constructor

```python
EditorTab()
```

### Key Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `file_path` | str | Path to the currently open file |
| `is_modified` | bool | Whether the document has unsaved changes |
| `editor` | QTextEdit | The underlying text edit widget |
| `btn_undo` / `btn_redo` | QToolButton | Undo/Redo toolbar buttons |
| `btn_bold` / `btn_italic` / `btn_underline` / `btn_strike` | QToolButton | Formatting buttons |

### Methods

| Method | Description |
|--------|-------------|
| `setPlainText(text)` | Set editor content, block signals during update |
| `toPlainText()` | Return the current editor content as plain text |
| `find_text(text, match_case=False, whole_word=False, forward=True)` | Search text in the document |
| `replace_text(find_str, replace_str, match_case=False, whole_word=False)` | Replace current match or next match |
| `replace_all(find_str, replace_str, match_case=False, whole_word=False)` | Replace all matches, returns count |
| `set_bookmark_callback(callback)` | Set callback for bookmark creation |
| `_bookmark_payload()` | Return bookmark data (page, scroll position, label) |
| `_add_bookmark_here()` | Create a bookmark at current position |
| `go_to_bookmark(page_number=0, scroll_position_y=0.0)` | Navigate to a bookmarked position |
| `read_current_page(voice_id=None)` | Return selected text or full text for TTS |

### Clipboard-Aware Paste

EditorTab intercepts `Ctrl+V` via `keyPressEvent()` and routes to:

- **`_paste_from_clipboard()`** — Detects clipboard content type and dispatches accordingly
- **`_paste_image_from_clipboard(mime)`** — Saves clipboard image to `APP_DATA_DIR/images/` and inserts Markdown `![](path)`
- **`_paste_rich_text_from_clipboard(mime)`** — Converts HTML clipboard content to Markdown and inserts

### Signals

- `textChanged()` — Emitted when editor content changes

### Accessibility

All formatting toolbar buttons have `accessibleName` and `accessibleDescription` set for screen-reader support.
