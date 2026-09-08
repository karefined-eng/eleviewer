# Changelog

All notable changes to EleViewer are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.4.0] - 2026-09-08

### Added
- **Interactive Playground Tutorials:** Guided spotlight tutorials that teach power-user features interactively (**Help > Interactive Tutorials**).
- **Split-Screen Web Panel Enhancements:** Integrated downloads manager with progress bars, page zoom controls (`Ctrl++`, `Ctrl+-`, `Ctrl+0`), and right-click context menu with copy and navigation.
- **Minimalist Welcome Screen:** Clean card dashboard with quick actions (Open File, Add Vault, Web Panel), live vault search, and clean recent files list.
- **Action-First Interactive Onboarding:** Dynamic playground that introduces core workspace capabilities right from launch.
- **Accessibility Support:** Comprehensive screen reader support for the Welcome Screen, Settings dialog, and main toolbar.
- **Distraction-Free Mode:** Easily toggle the main toolbar on or off (`Ctrl+Alt+T`) for focused study.
- **Visual Bookmarks:** Clear indicators distinguishing web links from local study files.

### Changed
- **Expanded Settings & Preferences:** Reorganized into six dedicated tabs for web downloads, default zoom, fonts, document view modes, and search.
- **Intuitive Toolbar Labels:** Clear text labels under icons by default, with customizable layout options in Settings.
- **Fail-Safe Feedback Dialog:** Automatic browser fallback if direct submission encounters network issues.
- **Ergonomic Toolbar Spacing:** Generous padding and margins around main toolbar icons.

### Fixed
- **Welcome Screen Action Cards:** Fixed button layout and icon rendering so action labels and icons display with crisp proportions.
- **Icon Asset Coverage:** Added missing SVG assets for files, folders, downloads, and history.
- **Loading Screen Transition:** Splash screen smoothly fades into the main window, eliminating launch flicker.
- **Empty Startup Session Bug:** Closed sessions with blank notes now properly return to the Welcome dashboard.
- **Search Typing Responsiveness:** Added debounced search delays to keep typing responsive during live vault queries.
- **Split-View Tab Duplication:** Focusing existing tabs correctly checks both split panes.
