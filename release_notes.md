### EleViewer v1.4.0

A major feature, accessibility, and design update bringing interactive tutorials, unified web browser capabilities, a streamlined welcome dashboard, and toolbar ergonomics.

#### What's New
* **Interactive Playground Tutorials:** Learn power-user features through guided, step-by-step spotlights (**Help > Interactive Tutorials**).
* **Split-Screen Web Browser Enhancements:**
  * **Smooth Page Zoom:** Scale web pages effortlessly with `Ctrl + +`, `Ctrl + -`, `Ctrl + 0`, or by holding `Ctrl` while scrolling, complete with a top-bar zoom indicator badge.
  * **Integrated File Downloads:** Download course handouts and research files directly to your chosen downloads folder with an animated progress bar.
  * **Quick Right-Click Menu:** Right-click anywhere in web view to open links, copy addresses or text, save bookmarks, and adjust zoom.
  * **Tab Preview Tooltips:** Hover over any web tab to see the complete page title and web address without cluttering your workspace.
* **Streamlined Welcome Dashboard:** Clean, card-based navigation for opening documents, adding course vaults, and launching the web browser, with live vault search and recent files.
* **Full Accessibility Support:** Comprehensive screen reader compatibility with Windows Narrator and NVDA across the dashboard, settings, and main toolbar.
* **Distraction-Free Reading Mode:** Easily hide the main toolbar (`Ctrl+Alt+T`) to maximize your vertical reading space.
* **Intuitive Toolbar Labels:** Toolbar buttons display clear labels under each icon with layout preferences available in Settings.
* **Expanded Settings & Preferences:** Six dedicated tabs to customize web download destinations, default zoom, fonts, soft word wrapping, PDF display modes, and search scopes.
* **Fail-Safe Feedback Submissions:** If a direct feedback submission cannot reach the server, EleViewer automatically opens your browser with a pre-filled issue so your notes are never lost.

#### Bug Fixes & Stability
* **Dashboard Action Cards:** Corrected icon rendering and button proportions for all quick-action cards.
* **Icon Coverage:** Added missing SVG icon assets for document files, folders, download tasks, and history.
* **Smooth Splash Transition:** The animated startup screen now fades smoothly into the main window, eliminating launch flicker.
* **Empty Note Startup:** Closing the app with a blank note now properly re-opens to the Welcome dashboard on next launch.
* **Search Responsiveness:** Vault live searches now debounce typing to maintain fluid UI responsiveness.
* **Split-View Tab Routing:** Switching focus to existing tabs reliably checks both left and right split panes without duplicate tabs.
