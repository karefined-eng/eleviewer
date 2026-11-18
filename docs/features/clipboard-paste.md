# Feature Guide: Clipboard-Aware Paste

## Overview

Paste images and rich text from your clipboard directly into notes. Images are saved automatically and inserted as Markdown image references. Rich text/HTML is converted to Markdown.

## How to Use

1. Copy an image or formatted text from any application (browser, file explorer, etc.)
2. Click in a Markdown or text note in EleViewer
3. Press `Ctrl+V`

### Images

- The image is saved to `AppData/EleViewer/images/paste_YYYYMMDD_HHMMSS.png`
- A Markdown reference is inserted: `![](C:\Users\...\AppData\...\images\paste_....png)`
- The document is marked as modified

### Rich Text / HTML

- HTML from the clipboard (e.g., copied from a webpage) is converted to Markdown
- `<br>` → line breaks, `</p>` → paragraph breaks, HTML tags stripped
- HTML entities decoded (`&nbsp;`, `&amp;`, `&lt;`, `&gt;`)

### Plain Text

- Falls back to the standard Qt paste behavior

## Supported Sources

- Web browsers (images, formatted text)
- File Explorer (image files copied to clipboard)
- Screenshot tools
- Any application that copies images or HTML to the clipboard
