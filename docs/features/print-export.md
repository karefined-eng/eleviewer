# Feature Guide: Print & Export to PDF

## Overview

Print any document to your system printer, or export any document to a PDF file.

## Print

| Shortcut | Menu | Description |
|----------|------|-------------|
| `Ctrl+P` | File > Print | Open system print dialog |

Supported document types:
- **PDF** — Each page rendered individually, printed page-by-page
- **Markdown / HTML / Text** — Rendered via Qt's document printing
- **Images** — Scaled to fit the print page

## Export to PDF

| Menu | Description |
|------|-------------|
| File > Export as PDF | Save current document as a PDF file |

Choose a filename and location in the save dialog. Supported types: Markdown, HTML, plain text, and images. PDFs can be re-exported (though native PDF → PDF copy is not yet supported).

## Implementation Notes

Printing uses `QPrinter` with `QPrintDialog`. The `_render_to_printer()` helper dispatches to the appropriate rendering strategy based on the viewer type.
