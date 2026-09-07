# Changelog

All notable changes to EleViewer are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.5.0] - 2026-09-07

### Added
- **Toggleable Main Toolbar (Distraction-Free Mode):** A new **View** menu with a checkable **Show Main Toolbar** action (`Ctrl+Alt+T`). Toolbar visibility is saved to your preferences and restored on launch, reclaiming the full toolbar height for reading while every command stays reachable from the menu bar and status-bar quick menu.
- **Theme-Aware Tab Close Buttons:** The `×` on document tabs, split-view tabs, and web tabs now uses a dedicated high-contrast icon per theme (bright white in Dark mode, deep grey in Light mode), fixing close buttons that were nearly invisible on dark tab bars. Icons also resolve via an absolute path, so they render correctly in packaged builds.

### Changed
- **Compact Unified Browser Header:** Removed the web panel's redundant "WEB BROWSER" title row entirely. The Expand, Pop Out, and Close controls now live at the right end of the browser's navigation row behind a slim divider, so pages start one row higher. The Pop Out button doubles as Re-dock while the panel is floated.
- **Web Panel Docks "Hit the Roof":** The right dock area now owns the window's top-right corner, so the web panel extends flush up to the menu bar and the main toolbar stops at the panel's edge instead of stretching across it — noticeably more vertical space for side-by-side work.
- **Auto-Maximize State Sync:** Opening the web panel with no documents open now correctly reflects the maximized state on the expand button (icon and tooltip), and closing the panel restores the editor together with the button state.

### Fixed
- **Empty Web Panel Control Icons:** The Expand, Pop Out, and Reload buttons referenced missing icon assets (`maximize`, `minimize`, `external-link`, `refresh-cw`) and rendered blank; they now ship real Lucide icons (`maximize-2` / `minimize-2`, new `external-link` and `refresh-cw` glyphs).

## [1.4.0] - 2026-09-07

### Added
- **Web Panel Zoom Controls:** Added full page zoom support with keyboard shortcuts (`Ctrl++` / `Ctrl+-` / `Ctrl+0`), mouse wheel zoom (`Ctrl+Scroll`), and an interactive zoom percentage badge in the navigation bar.
- **Integrated Download Manager:** Native file download handling in the Web Panel via `downloadRequested`, supporting a customizable downloads folder in Settings, with a docked animated progress bar, status feedback, and dismiss action.
- **Web View Context Menu:** Custom right-click menu in web views providing quick navigation (Back, Forward, Reload), Open Link in New Tab, Copy Link Address, Copy selection, Bookmark Page, and Zoom controls.
- **Web Tab Hover Tooltips:** Tab headers now display full page title and complete URL on hover.
- **Expanded Settings & Preferences:** Completely overhauled the Settings Dialog into six dedicated tabs (Startup & Defaults, Text Editing, PDF Reading, Web Browser Panel, Audio & Read Aloud, and Folders & Organization) with options for custom downloads folder, default zoom, editor font size/family, soft line wrapping, line numbers, PDF default zoom, speech reading speed, and vault search scope.
- **Action-First Interactive Onboarding:** A dynamic, interactive playground designed to teach you EleViewer's core features (Split-Screen Web Panel, Search, Settings) by having you actively use them right when you launch the app, completely avoiding boring, passive tutorial slides.
- **Type-Specific Bookmark Icons:** Distinct visual Lucide icons for web bookmarks (globe) and local document files in the persistent bookmarks panel.

### Changed
- **Bulletproof Feedback Dialog:** Submitting bug reports is now foolproof. If the backend API ever experiences rate limits or network failures, EleViewer automatically degrades gracefully, opening your default web browser to a pre-filled GitHub issue page so your feedback is never lost.
- **Web Panel Video & Layout Polish:** Enjoy seamless, full-screen video playback in the browser panel with `Esc` to exit, perfectly proportioned 16px navigation icons, and tightened native-feeling margins.
- **Intuitive Toolbar Labels & Custom Layouts:** Preserved clear text labels under icons by default for maximum intuitiveness, and added a user preference in Settings to select between *Icons with text labels*, *Icons only (Compact)*, or *Icons beside text*.
- **Bookmark Item Polish:** Replaced raw text remove button with a clean Lucide 'x' icon button for faster bookmark management.
- **Onboarding & Help Guides:** Refreshed in-app guides, release modals, and documentation to feature the unified workspace, new web panel capabilities, and comprehensive preferences.

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
