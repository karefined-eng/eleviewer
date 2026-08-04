Developer Onboarding: Welcome to the Sovereignty Workstation

If you are reading this, you are contributing to EleViewer—a minimalist, multi-tabbed study workstation built on PySide6.

Before you write a single line of code, you must understand our philosophy.

The Prime Directives
Zero Telemetry: No analytics, no tracking, no hidden pings home. User data is sacred and lives locally. (Note: Unhandled crashes are caught by a secure sys.excepthook which allows the user to opt-in to reporting the stack trace directly to our Vercel feedback API.)
Speed over Features: If a feature requires a 5-second loading screen or a 200MB dependency, we don't build it. The app must run on old student laptops without lag.
Offline First: The app must function 100% offline. The Web Panel is an augmentative feature, not a core dependency.

---

Copywriting & Communication Standards (The Paul Graham / Ogilvy Framework)
To maintain our distraction-free student workflow, all user-facing copy (in desktop UI widgets, modals, feedback dialogs, and website components) must adhere to globally praised copywriting principles:
Middle-Grader Readability (Flesch-Kincaid Grade 6–8 Rule): Keep vocabulary accessible to a 6th-to-8th grade reading level (ages 11–13). Avoid bloated corporate jargon, obscure acronyms, and convoluted sentence structures.
Write Like You Talk: Follow the Paul Graham and David Ogilvy principle of direct, conversational English. Speak to the user as a respected peer and fellow builder.
Outcome-Driven Intake: When soliciting feedback or reporting errors, focus on user empowerment rather than system failure. Use inviting, direct prompts (e.g., "Is there something you wish EleViewer could do? Share your idea directly with the developer — every submission is reviewed for our upcoming builds.").

---

Architecture Overview

EleViewer relies heavily on standard PySide6 widgets and custom components to keep the footprint small.

The Entry Point
main.py: Bootstraps the application, enforces single-instance locking (so clicking a file opens it in the existing window), and binds sys.excepthook to route global unhandled exceptions securely to the feedback dialog.

UI & Shell
ui.py: The MainWindow class. Manages the tab widget, toolbars, and the side panels.
theme.py: CRITICAL. Do not hardcode hex colors in any UI file. Use the centralized constants (BRANDPRIMARY, BRANDPANEL, etc.) here to ensure the desktop app visually matches the website. Additionally, this module powers the Dynamic UI Accents (via getactiveaccent()) which dynamically injects the user's chosen accent color into active states like :pressed and :checked buttons.

Core File Factory
file_handler.py: The heart of the viewer. It reads a file extension and dynamically instantiates the correct viewer (e.g., MarkdownViewer, XlsxViewer, PdfViewer).

The Viewers
pdfviewer.py: Uses QPdfView (native Qt module, not PyMuPDF). Features Text-to-Speech integration via ttsengine.py.
editor.py: The text/Markdown editor. Now uses native C++ QTextBrowser to eliminate the Chromium RAM tax, providing live syntax highlighting and markdown preview.
xlsxviewer.py & csvviewer.py: Uses openpyxl and standard library csv to render spreadsheets natively into QTableWidget with cell/row/column insertion and F9 TTS table summaries.
docxviewer.py & pptxviewer.py: Converts Word docs (python-docx) and PowerPoint presentations (win32com silent PDF conversion) for rich visual rendering and F9 Universal TTS reading.
htmlviewer.py & webpanel.py: Dedicated HTML/XML workstation with an integrated Chromium browser dock that is strictly lazy-loaded to preserve memory, featuring Obsidian-inspired reload/bookmark controls and global hyperlink interception.

Sub-systems & Concurrency
file_icons.py & icons.py: Minimalist Lucide line-art SVG icon engine supporting two-tone state rendering (#6cb6ff active focus vs #888888 inactive).
instance_lock.py: Local socket IPC server (QLocalSocket) enforcing single-instance execution, --new/-n CLI flag routing, and system-wide hotkey interception (Alt+E for Quick Note scratchpad).
vaultexplorer.py & vaultindexer.py: The left sidebar for file navigation (filtering out system junk files like desktop.ini). The Vault Indexer is powered by a pure-Python SQLite FTS5 implementation for full-text background search.
quick_switcher.py: The Ctrl+Q fuzzy finder for fast file switching.
draft_recovery.py: Saves auto-snapshots of text using a background DraftWorker(QThread) to prevent UI stutter and data loss.
saveutils.py, sessionmanager.py, settings.py: Enforces atomic disk writes (tempfile.mkstemp + os.fsync + os.replace) to strictly guarantee physical disk writes and eliminate 0-byte corruption on crash, while persisting scroll position, zoom, and PDF page numbers across sessions.
release_hash.py: Standalone script for computing executable SHA-256 release hashes for Winget and package manager distribution.

---

Contributing Workflow

Check the Context: Read README.md before starting work. It contains historical context and the main repository map.
Design System: Ensure UI changes match the modern aesthetics described in the README and use variables from theme.py.
Testing: Run main.py directly for manual validation, or execute test suites located in the tests/ directory.
Pull Requests: Explain why a feature is needed, not just what it does. Ensure it doesn't break the "Offline First" or "Zero Telemetry" rules.

Welcome aboard!