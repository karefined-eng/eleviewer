# EleViewer Gap Analysis Implementation Plan

Based on gap-analysis.md, this plan covers the 12 missing features across 3 priority tiers.

---

## Implementation Status: ALL TASKS COMPLETE

| Feature | Status | Implementation |
|---------|--------|---------------|
| **1. PDF Text Search** | ✅ Already Implemented | QPdfSearchModel + search bar with Ctrl+F, hit navigation, match count |
| **2. PDF Annotations/Highlighting** | ✅ Implemented | AnnotationOverlay widget, highlight/note/pen tools, color selection, sidecar JSON persistence (.eleviewer_annotations.json) |
| **3. Drag-and-Drop File Opening** | ✅ Already Implemented | MainWindow dragEnter/dragMove/drop events open files via `open_file()` |
| **4. Print/Export to PDF** | ✅ Implemented | `print_file()` with QPrintDialog (Ctrl+P), existing `export_pdf()` with `_render_to_printer()` handles all viewer types |
| **5. Image File Support** | ✅ Already Implemented | ImageViewer handles PNG, JPG, GIF, BMP, SVG, WEBP, ICO with zoom/pan |
| **6. PDF Table of Contents** | ✅ Implemented | TOC persistence via `pdf_toc_visible` setting, Ctrl+Shift+L shortcut, expands on load |
| **7. Doc↔Doc Side-by-Side Split** | ✅ Implemented | `toggle_split_view()` moves tabs between left/right panes, Ctrl+\ shortcut |
| **8. Clipboard-Aware Paste** | ✅ Implemented | EditorTab intercepts Ctrl+V: images saved to vault/images/ as markdown `![](path)`, rich text converted to markdown |
| **9. File Associations** | ✅ Already Implemented | setup.iss Inno Setup script has full registry entries for .pdf, .md, .docx, .xlsx, .pptx, .csv, .tsv, .txt, .html, .htm + context menu |
| **10. Undo/Redo Toolbar** | ✅ Implemented | Undo/Redo buttons on main toolbar (Ctrl+Z/Ctrl+Y), works with EditorTab and MarkdownViewer |
| **11. Auto-Update Notifications** | ✅ Implemented | Existing updater.py + new "Skip this version" button, skipped versions persisted in settings |
| **12. Accessibility Basics** | ✅ Implemented | accessibleName/accessibleDescription on main toolbar, PdfViewer toolbar, EditorTab formatting buttons |

---

## Files Modified

| File | Changes |
|------|---------|
| `settings.py` | Added `pdf_toc_visible`, `skipped_update_versions` to DEFAULT_SETTINGS; added `undo`, `redo`, `split` to toolbar_order |
| `pdf_viewer.py` | Added AnnotationOverlay class, annotation state, toolbar buttons (highlight/note/pen/color/erase), sidecar JSON save/load, TOC persistence, Ctrl+Shift+L shortcut |
| `ui.py` | Added split view toggle (Ctrl+\), undo/redo actions + shortcuts (Ctrl+Z/Ctrl+Y), print_file(), toggle_pdf_toc (Ctrl+Shift+L), accessible names on toolbar widgets, skipped version check in _on_update_found |
| `editor.py` | Added clipboard-aware paste (Ctrl+V): image → markdown `![](path)`, rich text → markdown; accessible names on formatting buttons; keyPressEvent override |
| `updater.py` | Added "Skip this version" button to UpdateDialog, persists skipped versions |
| `IMPLEMENTATION_PLAN.md` | This document |
| `setup.iss` | Already had full file associations (no changes needed) |

---

## Progressive Documentation

- `IMPLEMENTATION_PLAN.md` — Master plan with task status
- Inline code comments — Document new methods and classes
- `CHANGELOG.md` — User-facing change log (to be added on release)
- Sidecar files — `*.eleviewer_annotations.json` stored alongside PDFs for annotation persistence

---

## Verification

All modules import successfully:
- `settings` ✅
- `pdf_viewer` ✅
- `ui` ✅
- `editor` ✅
- `updater` ✅

Keyboard shortcuts added:
- `Ctrl+Shift+L` — Toggle PDF Table of Contents
- `Ctrl+\` — Toggle Split View
- `Ctrl+Z` — Undo
- `Ctrl+Y` — Redo
- `Ctrl+V` — Clipboard-aware paste (images as markdown, rich text converted)
- `Ctrl+P` — Print dialog
