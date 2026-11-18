# Feature Guide: PDF Annotations & Highlighting

## Overview

EleViewer now supports annotating PDFs directly in the app. You can highlight text passages, add sticky notes, and draw freehand annotations. All annotations are saved automatically and persist across sessions.

## Keyboard & Toolbar

| Tool | Toolbar Button | Keyboard |
|------|---------------|----------|
| Highlight | Highlight icon | Select text, click highlight color |
| Sticky Note | Note icon | Click page, type note |
| Freehand Pen | Pen icon | Click-drag to draw |
| Erase/Clear | X icon | Clears all annotations on current document |
| Color picker | Color dropdown | Yellow, Green, Pink |

Highlight colors: **Yellow** (default), **Green**, **Pink**

## How to Use

1. Open a PDF file (`Ctrl+O`)
2. Click the **Highlight** tool in the PDF toolbar
3. Select text or draw on the page with your mouse
4. Choose a color from the color dropdown
5. Annotations save automatically to a sidecar file: `<filename>.pdf.eleviewer_annotations.json`
6. Reopen the PDF — annotations reload automatically

## TOC Sidebar

The Table of Contents sidebar shows the PDF's bookmark outline. Click any entry to jump to that page. Toggle with `Ctrl+Shift+L` or the "Contents" button. Visibility is remembered per session.

## File Format

Annotations are stored in JSON sidecar files next to each PDF:

```json
[
  {
    "page": 2,
    "rect": [100, 200, 150, 30],
    "color": [255, 255, 0, 120],
    "type": "highlight",
    "text": ""
  }
]
```

Do not delete the sidecar file if you want to keep your annotations.
