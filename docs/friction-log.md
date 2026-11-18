# Friction Logging

## What Is Friction Logging?

Friction logging is the practice of recording points of confusion, difficulty, or frustration encountered while using or developing EleViewer. Each log entry captures:

- **What** you were trying to do
- **Where** it happened (file, feature, screen)
- **What went wrong** (error, confusion, slow workflow, missing affordance)
- **How it felt** (annoying, blocking, confusing, etc.)
- **Suggested fix** (if you have one)

The goal is to surface rough edges so they can be prioritized and fixed.

## How to Log Friction

Create a new entry in `docs/friction-log.md` (or add to an existing entry) using this format:

```markdown
## [YYYY-MM-DD] — <short title>

**Context:** What you were trying to do

**Friction:** What went wrong or was confusing

**Impact:** How it affected your workflow (annoying / blocking / confusing)

**Suggested fix:** What would make this smoother

**Files involved:** Relevant file paths
```

## Current Known Friction Points

### 1. Python 3.15 Incompatibility with PySide6 6.12.0

**Context:** Installing dependencies with `pip install -r requirements.txt`

**Friction:** PySide6 6.12.0 requires Python `<3.13`, but Python 3.15 is installed. `pip` cannot find a compatible version.

**Impact:** Blocking — cannot install dependencies on Python 3.15

**Suggested fix:** Use Python 3.12 or earlier, or wait for PySide6 6.13+ with Python 3.15 support. Document the supported Python version range in `requirements.txt` or `README.md`.

**Files involved:** `requirements.txt`, `requirements.lock.txt`

### 2. No Dedicated Annotation Eraser Tool

**Context:** Using PDF annotations (highlight, note, pen)

**Friction:** The "Clear annotations" button removes ALL annotations on the document. There's no way to erase a single annotation.

**Impact:** Annoying — users must clear all and redo annotations to remove one

**Suggested fix:** Add an eraser tool that removes individual annotations on click, or add a context menu on annotations to delete them.

**Files involved:** `pdf_viewer.py` (`AnnotationOverlay`, `_clear_annotations`)

### 3. Split View Only Moves One Tab

**Context:** Using `Ctrl+\` to enable split view

**Friction:** Only the current tab moves to the right pane. To split two already-open documents, you must manually open one in each pane.

**Impact:** Confusing — users expect both panes to show their open documents

**Suggested fix:** When enabling split view with multiple tabs open, offer to distribute existing tabs across panes, or add a "Move to Other Pane" command on tabs.

**Files involved:** `ui.py` (`toggle_split_view`)

### 4. No Visual Feedback for Annotation Save

**Context:** Drawing annotations on a PDF

**Friction:** Annotations save silently to the sidecar file. No toast, status message, or indicator confirms they were saved.

**Impact:** Confusing — users don't know if annotations persisted

**Suggested fix:** Add a brief status message ("Annotations saved") after annotation creation or document load with annotations.

**Files involved:** `pdf_viewer.py` (`_save_annotations`, `_on_annotation_created`)

### 5. Clipboard Paste Image Path is Absolute

**Context:** Pasting images into notes via `Ctrl+V`

**Friction:** Images are saved to `APP_DATA_DIR/images/` and referenced with an absolute path. If the vault is moved or synced across machines, the image references break.

**Impact:** Annoying — notes become non-portable

**Suggested fix:** Save images relative to the vault folder and use relative paths in Markdown.

**Files involved:** `editor.py` (`_save_image_and_insert`)

### 6. Export PDF for PDFs Not Yet Supported

**Context:** File > Export as PDF on an open PDF

**Friction:** The export path falls back to grabbing a pixmap of the widget for non-text viewers. PDFs are rendered page-by-page only in the print path, not the export path.

**Impact:** Missing feature — users can't export a PDF to a new PDF file

**Suggested fix:** Add PDF → PDF export support using `QPdfDocument.render()` to a `QPrinter` in PdfFormat mode.

**Files involved:** `ui.py` (`_render_to_printer`, `export_pdf`)

### 7. No High-Contrast Theme

**Context:** Accessibility for low-vision users

**Friction:** Only a dark theme is available. No high-contrast or system-contrast detection.

**Impact:** Blocking for some users with visual impairments

**Suggested fix:** Add a high-contrast theme variant and detect Windows high-contrast settings.

**Files involved:** `theme.py`, `settings.py` (`theme_mode`)

## Friction Log Review Process

1. **Weekly:** Review new friction entries during team sync
2. **Prioritize:** Blocking > Confusing > Annoying
3. **Assign:** Convert high-priority friction into GitHub issues
4. **Close:** Link the resolved issue back to the friction log entry

## Example Entry

```
## [2026-11-18] — PySide6 6.12.0 doesn't support Python 3.15

**Context:** Running `pip install -r requirements.txt` on a fresh machine with Python 3.15

**Friction:** pip reports "No matching distribution found for PySide6==6.11.2" because 6.12.0 requires Python <3.13

**Impact:** Blocking — cannot run the app at all

**Suggested fix:** Document Python 3.12 as the supported version. Add a version check at startup with a clear error message.

**Files involved:** `requirements.txt`, `main.py`
```
