# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.3.4] - 2026-09-11

### Changed
- Reduced web navigation icon sizes and button fixed sizes in the Web Panel.
- Refactored `_handle_fullscreen` in the Web Panel to use direct parent reparenting instead of the fragile `_fs_window` wrapper.

### Fixed
- Fixed runtime `NameError` related to unimported Qt elements (`QLineEdit`, `QListWidget`, `QColor`, etc.).
- Fixed `KeyError` during `BRAND_ACCENT` initialization in `theme.py` by transitioning to a unified `get_brand_accent()` getter.
- Fixed `test_link_interception.py` test failing because the newly created session window was replacing the Welcome Tab instead of adding a new one.

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
