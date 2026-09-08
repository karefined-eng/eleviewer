# Changelog

All notable changes to EleViewer are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.4.0] - 2026-09-08

### Added
- **Advanced Web Panel Settings:** New toggles in Settings for Context Menus, 3D Apps (WebGL), Browser Extensions, Password Saving, and Global History.
- **Web Panel Zoom Controls:** Full page zoom support with keyboard shortcuts (`Ctrl++`, `Ctrl+-`, `Ctrl+0`) and a live zoom percentage badge.
- **Integrated Download Manager:** Native file download handling in the Web Panel with an animated progress bar and customizable downloads folder.
- **Web View Context Menu:** Right-click menu providing quick navigation, bookmarks, and zoom controls.
- **Action-First Interactive Onboarding:** A dynamic playground that teaches core features interactively on first launch.
- **Toggleable Main Toolbar:** A "Distraction-Free Mode" accessible via `Ctrl+Alt+T` to hide the main toolbar for focused reading.
- **Visual Bookmarks:** Type-specific icons for web links and local document files.

### Changed
- **Compact Web Browser Header:** Streamlined the web panel's navigation row by integrating Expand, Pop Out, and Close controls natively.
- **Expanded Settings & Preferences:** Completely reorganized into six dedicated tabs for a cleaner configuration experience.
- **Intuitive Toolbar Labels:** Reverted to clear text labels under icons by default, with new layout options in Settings (Icons only, Icons beside text).
- **Theme-Aware UI Elements:** Tab close buttons and web panel headers now dynamically sync with Dark and Light modes for better contrast.
- **Feedback Dialog Fail-Safe:** If the network fails, the feedback form automatically falls back to your default web browser with a pre-filled GitHub issue.

### Fixed
- **Web Panel Layout Margins:** Tightened native-feeling margins and fixed empty control icons.
- **Split-View Tab Duplication:** Focusing existing tabs now correctly checks both left and right split panes instead of opening duplicates.
- **Search Typing Latency:** Eliminated UI freezes on the Welcome screen by adding a 200ms delay to live vault searches.
- **Settings Overwrite Bug:** Resolved an issue where toggling the formatting toolbar could overwrite other user preferences.
