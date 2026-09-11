# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.3.3] - 2026-09-10

### Added
- Bookmark manager dialog and interactive bookmarks bar to the web panel.
- Tools to export and import bookmarks and cookies.
- A new "Omnibar" on the Welcome widget for searching vault files and launching URLs.
- Recent files and bookmarks quick-access columns on the Welcome screen.

### Changed
- Standardized toolbar button sizes across the application.
- Refactored fullscreen web handling for better reliability.
- Optimized Nuitka build pipeline to exclude unused standard library modules (`tkinter`, `unittest`, etc.), reducing the final executable size.

### Fixed
- Crash related to the `paintEvent` drop indicator.
- Missing `.gitmodules` and restored `setup.iss` to resolve CI/CD build failures.
