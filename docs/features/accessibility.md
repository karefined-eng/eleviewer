# Feature Guide: Accessibility

## Overview

EleViewer includes accessibility improvements for screen-reader users and keyboard navigation.

## Accessible Names & Descriptions

The following UI elements have `accessibleName` and `accessibleDescription` set:

### Main Toolbar
- New File, Toggle Vault Panel, Toggle Bookmarks Panel, Open File, Save File, Undo, Redo, Read Aloud, Web Panel, Settings, Toggle Split View

### PDF Viewer Toolbar
- Table of Contents, Find in Document, Previous Page, Next Page, Zoom Out, Fit to Page, Fit to Width, Zoom In, Two-Page View, Bookmark This Page, Highlight Tool, Sticky Note Tool, Freehand Pen Tool, Clear Annotations, Highlight Color

### Editor Formatting Toolbar
- Undo, Redo, Heading, Bullet List, Numbered List, Bold, Italic, Underline, Strikethrough, Link, Table, Clear Formatting, Pin Toolbar

## Keyboard-Only Navigation

All core actions are reachable via keyboard shortcuts (see `ui.py` API reference for the full list). The `Esc` key hides open panels (Find/Replace, Vault, Bookmarks, TTS bar) in priority order.

## Screen Reader Testing

Verify screen reader announcements by:
1. Enabling Windows Narrator (`Ctrl+Win+Enter`)
2. Tabbing through the main toolbar — each button should announce its name and description
3. Opening a PDF and tabbing to the annotation tools
4. Using Ctrl+V to paste — the editor should announce the insertion

## Known Limitations

- No high-contrast theme variant yet (planned)
- PDF annotation drawing is mouse-only (no keyboard drawing tool)
- TOC tree navigation via keyboard works but could be improved
