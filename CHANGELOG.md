# Changelog

## [1.3.1] - 2026-08-03

### Fixed
- **Fatal Infinite Crash Loop:** Fixed an issue where the Chromium WebEngine renderer triggered an aggressive restart loop on Windows, causing massive disk and CPU usage without displaying a window.
- **App Bloat Reduction (487MB -> <25MB):** Aggressively stripped `QWebEngineView` and excluded heavy AI data-science packages from the Nuitka build process to restore the lightweight standalone footprint.

### Changed
- **Web Browser Panel:** Replaced the embedded Chromium browser with a native OS web launcher. `Ctrl+T` now seamlessly opens web searches natively in your default system browser, saving ~450MB of binary bloat.

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2026-08-03

### Added
- **In-App Auto-Updater:** Automatically checks GitHub Releases for new versions on boot, offering a seamless 1-click upgrade.
- **SQLite FTS5 Vault Indexing:** Blazing-fast full-text search across entire folders/vaults using native Rust extensions and PyO3.
- **Inno Setup Installer:** Replaced portable binaries with a proper Windows installer (`.exe`) featuring registry integration, Start Menu shortcuts, and `Open With` context menus.
- **Automated CI/CD:** Complete GitHub Actions pipeline for compiling Rust, running Nuitka C++ LTO builds, and generating Inno Setup installers automatically.
- **Lucide Icons:** Replaced legacy glyphs with a crisp, professional SVG icon set across the entire UI.
- **Draft Recovery:** Background autosave logic via `QThread` workers with atomic write safeguards to prevent 0-byte file corruption.
- **Dynamic Theming:** Status bar, panels, and active icons now pop with a dynamic accent color based on user settings.
- **HTML XSS Sanitization:** Implemented `bleach` to securely sanitize HTML before rendering Markdown previews.
- **Symlink Path Traversal Guards:** Strict canonical root validation added to isolate local file access securely.

### Changed
- Refactored `QThread` shutdown logic to ensure safe termination on app exit, fixing silent crashes.
- Migrated CI/CD Rust packaging from `maturin develop` to `maturin build` for cloud runner compatibility.

## [1.2.0] - 2026-07-21

### Added
- **Web Browser Panel:** Integrated a secondary `QWebEngineView` panel to seamlessly browse the web alongside documents.
- **HTML Document Support:** Added support for viewing raw HTML files natively inside the editor.
- **Autosave Framework:** Initial implementation of session tracking and document recovery.
- **App Branding:** Added custom EleViewer splash screens, window icons, and UI identity.

### Fixed
- Stabilized single-instance IPC communication across threads.

## [1.1.0] - 2026-06-15

### Added
- **Find & Replace:** Full-text search and replace functionality added to the primary text editors.
- **Single-Instance Locking:** Added a local socket server to guarantee only one instance of EleViewer runs at a time, routing new files to the existing window.
- **Basic Web Panel:** Early prototype of the side-by-side web browser.

## [1.0.0] - 2026-05-31

### Added
- **Initial Release:** Lightweight, offline-first Windows document editor.
- **Multi-Format Support:** Native rendering for `.pdf`, `.docx`, `.xlsx`, `.pptx`, `.md`, `.csv`, `.tsv`, and `.txt`.
- **Text-to-Speech (TTS):** Universal F9 TTS reading for accessibility across all document types.
- **Keyboard-Centric Navigation:** Added the 4 Reflex keys (`Ctrl+Q`, `Alt+V`, `Ctrl+T`, `Ctrl+Shift+T`).
- **Zero Telemetry:** Privacy-first design with absolutely no data collection or tracking.
