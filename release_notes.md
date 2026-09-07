### EleViewer v1.4.0
A major feature and design update focusing on the split-screen web research panel, toolbar ergonomics, expanded settings, and visual bookmarks.

#### What's New
* **Enhanced Split-Screen Web Browser:**
  * **Smooth Page Zoom:** Scale web pages effortlessly with `Ctrl + +`, `Ctrl + -`, `Ctrl + 0`, or by holding `Ctrl` while scrolling. A dedicated zoom badge in the top bar shows your current zoom percentage.
  * **Integrated File Downloads:** Download course handouts, slides, and data files directly to your chosen Downloads folder with an animated progress bar.
  * **Quick Right-Click Menu:** Right-click anywhere in your web view to open links in a new tab, copy link addresses or selected text, save bookmarks, or adjust page zoom.
  * **Tab Preview Tooltips:** Hover over any web tab to see the complete page title and web address without crowding your workspace.
* **Intuitive Toolbar with Clear Labels:** Toolbar buttons proudly display clear text labels under each icon ("New File", "Vault", "Bookmarks", "Open", "Save", "Read Aloud", "Web", "Settings") so every action is immediately obvious, with layout options in Settings.
* **Expanded Settings & Preferences:** Six dedicated settings tabs allow you to tailor your workstation: set custom Web Panel download destinations, default zoom levels, editor font sizing and soft word wrapping, PDF display modes, Text-to-Speech reading speed, and vault search scopes.
* **Action-First Interactive Onboarding:** A dynamic, interactive playground designed to teach you EleViewer's core features (Split-Screen Web Panel, Search, Settings) by having you actively use them right when you launch the app, completely avoiding boring, passive tutorial slides.
* **Bulletproof Feedback Dialog:** Submitting bug reports is now foolproof. If the backend API ever experiences rate limits or network failures, EleViewer automatically degrades gracefully, opening your default web browser to a pre-filled GitHub issue page so your feedback is never lost.
* **Web Panel Video & Layout Polish:** Enjoy seamless, full-screen video playback in the browser panel with `Esc` to exit, perfectly proportioned 16px navigation icons, and tightened native-feeling margins.
* **Visual Bookmarks:** Dedicated icons for web links and document files make it simple to distinguish web research from local course documents at a glance, plus one-click bookmark deletion.

#### Bug Fixes & Stability
* Ensured reliable focus handling and keyboard shortcuts across side-by-side web and document panels.
* Streamlined bookmark deletion without affecting other open sessions.

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
