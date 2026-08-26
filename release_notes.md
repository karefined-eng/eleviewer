### EleViewer v1.3.1
A reliability and study-workflow update for the Windows document workspace.

#### What's New
* **Shortcuts work from every document:** Bookmark your place with `Ctrl+D`, open the Bookmarks panel with `Ctrl+Alt+B`, open Getting Started with `F1`, and switch tabs with `Ctrl+1` through `Ctrl+9` even when a child editor has focus.
* **Clearer first session:** The welcome dashboard now explains the common workflow of opening a document and then opening the PDF you need in another tab. Action buttons include helpful tooltips.
* **Better help:** The offline guide includes direct answers for keeping two files open, saving your place, and reporting a problem without sharing private course files.
* **Improved PowerPoint slides:** Embedded images now stay in their original position between slide text instead of being moved below all text.

#### Bug Fixes & Stability
* Centralized application-wide shortcut handling and removed the duplicate Escape binding.
* Added a regression test covering all documented shortcuts from a focused child editor.
* Added a regression test covering interleaved PPTX text and embedded images.

### EleViewer v1.3.0
A lightweight Windows document editor supporting DOCX, XLSX, MD, TXT, CSV, HTML, and PDF files.

#### What's New (since v1.2.0)

✨ **A More Polished Experience**
* **Beautiful Scrollbars**: We've removed the bulky, legacy Windows scrollbars and replaced them with custom, dark-themed scrollbars that match the app's sleek aesthetic.
* **Modern Tooltips**: Hovering over buttons now reveals soft, dark-themed tooltips instead of the bright yellow Windows 95 style boxes.
* **Consistent Branding**: Fixed a bug where the generic Windows icon would show up on some popups instead of the EleViewer logo.
* **Smoother Welcome Screen**: The Welcome Dashboard has been fine-tuned so that it resizes smoothly and looks perfect on any screen size without elements overlapping.

🔧 **Bug Fixes & Stability**
* **Smarter Search Bar**: Fixed an issue where typing a local file path into the search bar would sometimes accidentally trigger a web search instead of opening your document.
* **Under-the-hood**: Various stability improvements to make installing and updating the app faster and more reliable.
