# API Reference: pdf_viewer.py

## PdfViewer

**`class PdfViewer(QWidget)`**

Main PDF viewer widget using `QPdfView` (native Qt PDFium-based rendering) for vector-crisp document display.

### Constructor

```python
PdfViewer(file_path=None, status_callback=None)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `file_path` | str | Optional path to a PDF file to load on startup |
| `status_callback` | callable | Optional callback for status bar messages |

### Key Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `file_path` | str | Path to the currently loaded PDF |
| `current_page` | int | Index of the currently visible page (0-based) |
| `total_pages` | int | Total number of pages in the loaded PDF |
| `is_modified` | bool | Whether the document has unsaved changes |
| `_annotations` | list[dict] | List of annotation dicts (page, rect, color, type, text) |
| `_overlay` | AnnotationOverlay | The annotation overlay widget |
| `_toc_visible` | bool | Whether the Table of Contents sidebar is visible |
| `search_model` | QPdfSearchModel | Qt search model for in-document text search |

### Methods

#### `load_from_path(file_path)`
Load a PDF file from disk. Handles document caching (up to 8 cached documents) and restores annotations from sidecar `.eleviewer_annotations.json` if present.

#### `prev_page()` / `next_page()`
Navigate to the previous/next page. Wraps around at document boundaries.

#### `go_to_bookmark(page_number=0, scroll_position_y=0.0)`
Jump to a specific page number (0-based). Used by bookmark navigation and TOC clicks.

#### `fit_page()` / `fit_to_width()`
Set zoom mode to fit the page or width within the viewport.

#### `_toggle_toc()`
Show/hide the Table of Contents sidebar. Persists visibility to `pdf_toc_visible` setting. Bound to `Ctrl+Shift+L`.

#### `find_text(text, match_case=False, whole_word=False, forward=True)`
Search for text in the document using `QPdfSearchModel`. Returns `True` if matches found.

#### `read_current_page(voice_id=None)`
Extract text from the current page and read it aloud via TTS. Returns the extracted text string.

#### Annotation Methods

| Method | Description |
|--------|-------------|
| `_set_annot_highlight()` | Activate highlight tool (yellow/green/pink color) |
| `_set_annot_note()` | Activate sticky note tool |
| `_set_annot_pen()` | Activate freehand pen drawing tool |
| `_set_annot_color(name)` | Set highlight color ("yellow", "green", "pink") |
| `_clear_annotations()` | Remove all annotations from current page/document |
| `_save_annotations()` | Persist annotations to `.eleviewer_annotations.json` sidecar |
| `_load_annotations()` | Load annotations from sidecar file on document open |

### Signals

- `textChanged()` — Emitted when document content changes

---

## AnnotationOverlay

**`class AnnotationOverlay(QWidget)`**

Transparent overlay widget that sits on top of `QPdfView` for drawing annotations (highlights, notes, pen marks).

### Constructor

```python
AnnotationOverlay(parent=None)
```

### Methods

| Method | Description |
|--------|-------------|
| `set_annotations(annotations)` | Replace the annotation list and repaint |
| `set_tool(tool)` | Set active drawing tool ("none", "highlight", "note", "pen") |
| `set_color(color)` | Set the QColor for new annotations |
| `annotations()` | Return the current annotation list |
| `clear_annotations()` | Clear all annotations |
| `remove_annotation(index)` | Remove annotation at the given index |

### Signals

- `annotation_created(dict)` — Emitted when a new annotation is drawn
- `annotation_removed(int)` — Emitted when an annotation is removed

### Annotation Dict Format

```python
{
    "page": int,           # 0-based page index
    "rect": [x, y, w, h],  # Rectangle in widget coordinates
    "color": [r, g, b, a], # RGBA color values (0-255)
    "type": str,           # "highlight", "note", or "pen"
    "text": str,           # Note text (for "note" type)
}
```

---

## PdfTextWorker

**`class PdfTextWorker(QThread)`**

Background worker for extracting text from a PDF page without blocking the UI thread (used for TTS and page text prefetching).

### Signals

- `extracted(int, str)` — Emitted with `(page_index, extracted_text)`
