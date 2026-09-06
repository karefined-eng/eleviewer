# Changelog

All notable changes to EleViewer are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.1] - 2026-09-06

### Added
- **Global Tab Cycling:** Added application-wide `Ctrl+Tab` and `Ctrl+Shift+Tab` (and `Ctrl+Backtab`) shortcuts to cycle smoothly across active tabs, including split-view pane awareness.
- **Search Status Notifications:** Added user feedback in the status bar when invoking Find (`Ctrl+F`) or Replace (`Ctrl+H`) on documents that do not support raw text search/replacement (such as PDFs).
- **Tab Close Button (`×`):** Restored clean, subtle close buttons on document tabs with a hover-to-reveal pattern to maintain an uncluttered tab bar.

### Changed
- **Accurate Keyboard Shortcuts Reference:** Updated the shortcuts dialog (`F1`):
  - Corrected Quick File Switcher mapping to `Ctrl+Q` (resolved collision with `Ctrl+P`).
  - Separated the Split-Screen Web Browser toggle (`Ctrl+Shift+W`) and the Read Aloud speech reader (`F9`).
  - Fixed duplicate `Ctrl+Q` label under Quit by documenting standard `Alt+F4`.
- **Unambiguous Unsaved Changes Prompt:** Replaced the generic "Yes / No / Cancel" dialog on tab close with standard "Save", "Discard", and "Cancel" buttons showing the exact document filename.
- **Dynamic Vault Panel Theming:** Extracted live palette reapplication in `VaultExplorer` so folder dropdowns, action buttons, and tree views instantly adjust to Light and Dark mode switches.
- **Synchronized Web Panel Header:** The dockable side-by-side web browser title bar and controls now update dynamically when changing theme colors in settings.
- **Status Bar Theme Synchronization:** Extracted theme application for status bar labels to guarantee readability across all color modes.
- **One-Time Milestone Community Prompt:** Gated the early-access community dialog behind a persistent preference and bypassed the modal prompt during automated tests.

### Fixed
- **Split-View Duplicate Tabs:** `switch_to_tab_if_open()` now checks both left and right split panes, focusing existing tabs instead of opening duplicates.
- **Omnibar Typing Latency:** Debounced live vault search on the Welcome screen by 200ms, eliminating UI freezes caused by synchronous directory scans on every keystroke.
- **Settings Overwrite Bug:** Resolved an issue where toggling the formatting toolbar pin in the editor could overwrite other user preferences.
- **Quick Switcher Palette:** Fixed Quick Switcher relying on dark-only constants by adopting runtime palette lookups.
