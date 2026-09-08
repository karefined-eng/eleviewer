### EleViewer v1.4.0

A major feature and design update focusing on the unified study workspace, web browser capabilities, and toolbar ergonomics.

#### What's New
* **Advanced Web Browser Capabilities:**
  * **Smooth Page Zoom:** Scale web pages effortlessly with `Ctrl + +`, `Ctrl + -`, `Ctrl + 0`, or by holding `Ctrl` while scrolling. A dedicated zoom badge in the top bar shows your current zoom percentage.
  * **Integrated File Downloads:** Download course handouts, slides, and data files directly to your chosen Downloads folder with an animated progress bar.
  * **Quick Right-Click Menu:** Right-click anywhere in your web view to open links in a new tab, copy link addresses or selected text, save bookmarks, or adjust page zoom.
  * **Tab Preview Tooltips:** Hover over any web tab to see the complete page title and web address without crowding your workspace.
* **New Advanced Settings:** A dedicated section in the Settings menu now allows you to enable hardware acceleration (WebGL) for 3D apps, context menus, and prepare for future extensions and global history features.
* **Intuitive Toolbar with Clear Labels:** Toolbar buttons proudly display clear text labels under each icon ("New File", "Vault", "Bookmarks", "Open", "Save", "Read Aloud", "Web", "Settings") so every action is immediately obvious, with layout options in Settings.
* **Distraction-Free Mode:** Easily toggle the main toolbar off (`Ctrl+Alt+T`) to reclaim vertical screen space while reading.
* **Expanded Settings & Preferences:** Six dedicated settings tabs allow you to tailor your workstation: set custom Web Panel download destinations, default zoom levels, editor font sizing and soft word wrapping, PDF display modes, Text-to-Speech reading speed, and vault search scopes.
* **Action-First Interactive Onboarding:** A dynamic, interactive playground designed to teach you EleViewer's core features (Split-Screen Web Panel, Search, Settings) by having you actively use them right when you launch the app.
* **Bulletproof Feedback Dialog:** Submitting bug reports is now foolproof. If the network ever fails, EleViewer automatically degrades gracefully, opening your default web browser to a pre-filled GitHub issue page so your feedback is never lost.
* **Web Panel Video & Layout Polish:** Enjoy seamless, full-screen video playback in the browser panel with `Esc` to exit, perfectly proportioned navigation icons, and tightened native-feeling margins.
* **Visual Bookmarks:** Dedicated icons for web links and document files make it simple to distinguish web research from local course documents at a glance.

#### Bug Fixes & Stability
* Eliminated UI freezes on the Welcome screen by adding intelligent typing delays to live vault searches.
* Ensured reliable focus handling and keyboard shortcuts across side-by-side web and document panels.
* Fixed an issue where toggling the formatting toolbar could accidentally overwrite other user preferences.
