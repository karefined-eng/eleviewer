# Changelog

All notable changes to EleViewer are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.4.0] - 2026-09-08

### Added
- **Interactive Playground Tutorials:** Guided spotlight tours teaching EleViewer's study superpowers step-by-step (**Help > Interactive Tutorials**).
- **Split-Screen Web Panel Superpowers:**
  - **Full Page Zoom Controls:** Scale web pages effortlessly with shortcuts (`Ctrl++`, `Ctrl+-`, `Ctrl+0`), mouse scroll (`Ctrl+Scroll`), and a live zoom percentage badge.
  - **Integrated Downloads Manager:** Download course slides and research PDFs directly to a dedicated study folder with an animated progress bar and status feedback.
  - **Quick Context Menu:** Right-click inside any web page to copy text, copy links, open links in new tabs, add bookmarks, and adjust zoom.
  - **Tab Hover Previews:** Hovering over any web tab displays the full page title and web address.
- **Distraction-Free Reading Mode:** Toggle the top toolbar on and off (`Ctrl+Alt+T`) for a clean, minimalist study view.
- **Streamlined Welcome Dashboard:** Clean, card-based navigation to open documents, connect study folders (vaults), or launch the web browser, with instant folder search.
- **Action-First Interactive Onboarding:** A dynamic playground that introduces split-screen notes and research directly on first launch.
- **Full Screen Reader Accessibility:** Comprehensive screen reader compatibility (Windows Narrator and NVDA) across the dashboard, settings, and main toolbar.
- **Visual Bookmark Badges:** Distinct icons separating web bookmarks from local study documents.
- **Winget Package Distribution:** Official Windows Package Manager support (`winget install karefined-eng.EleViewer`).

### Changed
- **Expanded Settings & Preferences Hub:** Reorganized into six dedicated tabs for web downloads, default zoom, typography, document view modes, audio reading speed, and folder search.
- **Intuitive Toolbar Labels:** Toolbar buttons now feature clear text labels under icons by default, with customizable compact options in Settings.
- **Fail-Safe Feedback Submissions:** If submitting feedback encounters network issues, EleViewer automatically opens your browser with a pre-filled submission so your thoughts are never lost.
- **Ergonomic Toolbar Spacing:** Refined margins and icon proportions across the main toolbar for improved tap and click comfort.

### Fixed
- **Welcome Screen Action Cards:** Fixed button layout and icon rendering so quick-action cards and text labels display with clean, balanced proportions.
- **Complete Icon Coverage:** Added missing SVG icons for files, folders, download tasks, and history items.
- **Tutorial Spotlight Positioning:** Fixed tutorial card coordinates ensuring dialog cards always remain safely visible on-screen with escape key exit support.
- **Smooth Splash Screen Transition:** The launch animation smoothly fades directly into the main window, eliminating startup flicker.
- **Empty Startup Session Handling:** Closing the application with a blank scratchpad now reliably reopens to the Welcome dashboard on next launch.
- **Search Typing Responsiveness:** Added debounced search delays to keep typing responsive during live study folder queries.
- **Split-View Tab Routing:** Switching focus to existing tabs reliably checks both left and right split panes without creating duplicate tabs.

---

## [1.3.1] - 2026-09-06

### Added
- **Global Tab Cycling:** Added application-wide `Ctrl+Tab` and `Ctrl+Shift+Tab` shortcuts to cycle smoothly across active tabs, including split-view pane awareness.
- **Search Status Notifications:** Added user feedback in the status bar when invoking Find (`Ctrl+F`) or Replace (`Ctrl+H`) on documents that do not support raw text editing (such as PDFs).
- **Tab Close Button (`×`):** Restored clean, subtle close buttons on document tabs with a hover-to-reveal pattern to maintain an uncluttered tab bar.

### Changed
- **Accurate Keyboard Shortcuts Reference:** Updated the shortcuts dialog (`F1`):
  - Corrected Quick Switcher mapping to `Ctrl+Q`.
  - Separated the Split-Screen Web Browser toggle (`Ctrl+Shift+W`) and the Read Aloud speech reader (`F9`).
  - Fixed duplicate `Ctrl+Q` label under Quit by documenting standard `Alt+F4`.
- **Unambiguous Unsaved Changes Prompt:** Replaced the generic dialog on tab close with clear "Save", "Discard", and "Cancel" buttons showing the exact document filename.
- **Dynamic Vault Panel Theming:** Extracted live palette reapplication so folder dropdowns, action buttons, and tree views instantly adjust to Light and Dark mode switches.
- **Synchronized Web Panel Header:** The dockable side-by-side web browser title bar and controls now update dynamically when changing theme colors in settings.
- **Status Bar Theme Synchronization:** Extracted theme application for status bar labels to guarantee readability across all color modes.

### Fixed
- **Split-View Duplicate Tabs:** Switching tabs checks both left and right split panes, focusing existing tabs instead of opening duplicates.
- **Omnibar Typing Latency:** Debounced live vault search on the Welcome screen by 200ms, eliminating UI freezes on rapid typing.
- **Settings Overwrite Bug:** Resolved an issue where toggling the formatting toolbar pin in the editor could overwrite other user preferences.
- **Quick Switcher Palette:** Fixed Quick Switcher relying on dark-only constants by adopting runtime palette lookups.

[1.4.0]: https://github.com/karefined-eng/eleviewer/compare/v1.3.1...v1.4.0
[1.3.1]: https://github.com/karefined-eng/eleviewer/compare/v1.3.0...v1.3.1
