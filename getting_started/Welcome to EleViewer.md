---
title: EleViewer Workstation Reference Manual
description: Official technical documentation, shortcut index, and workstation guide for the EleViewer local study workspace.
---

EleViewer Workstation: Official Reference Manual

EleViewer is a lightweight, local-first Windows study workstation for reading, editing, and organizing academic and professional documents. It natively supports DOCX, XLSX, PPTX, PDF, MD, TXT, CSV, and HTML/HTM files within a unified, high-speed tabbed interface.

This manual is your exhaustive technical reference for operating the workstation, mastering keyboard reflexes, managing local vaults, and understanding data protection mechanisms.

---

Workstation Overview & Vault Setup

EleViewer operates on a strict local-first, data sovereignty architecture. Your study materials, index databases, and application settings remain entirely on your local hard drive. There are no cloud accounts, mandatory logins, or background telemetry services.

Setting Up Your Vault Explorer (Alt + V)
The Vault Explorer is your project sidebar for indexing and navigating local document directories.

Press Alt + V or click the Folder icon on the left sidebar to toggle the Vault Explorer.
Click the Settings icon (⚙️) at the top of the sidebar or press Alt + S to open the Settings Dialog.
Under Vault Configuration, click Add Folder and select any local directory containing your study materials, lecture slides, or project notes.
Once added, EleViewer's background SQLite FTS5 full-text indexer automatically scans your documents. Your files immediately appear in the sidebar tree and become searchable across their full text.
Use the dropdown selector at the top of the sidebar to instantly switch between multiple registered vault directories.

> [!TIP]
> While in the Settings Dialog (Alt + S), navigate to the Theme section to select a dynamic accent color that matches your visual workflow while preserving high-contrast readability.

---

Master Reflex Shortcut & Command Index

To maximize reading and editing velocity, EleViewer is engineered around hotkeys called Reflexes. Keep your hands on the keyboard and execute commands without mouse friction.

File Navigation & Vault Management
| Shortcut | Command | Action Description |
|---|---|---|
| Ctrl + Q | Quick Switcher | Opens a fuzzy search overlay to find and open vault files by typing a few letters. |
| Alt + V | Toggle Vault Sidebar | Collapses or expands the left-hand directory tree for distraction-free focus mode. |
| Ctrl + N | New File Picker | Creates a new Markdown, TXT, CSV, or HTML document in your active directory. |
| Ctrl + O | Open File | Opens a native system file dialog to load external documents outside your vault. |
| Ctrl + S | Save File | Immediately writes active editor changes to disk using atomic save protection. |
| Ctrl + Shift + S | Save As | Saves the current document under a new filename or location. |

Tab & Window Control
| Shortcut | Command | Action Description |
|---|---|---|
| Ctrl + T | New Web Tab / Panel | Opens an integrated web browser tab directly alongside your local study notes. |
| Ctrl + W | Close Tab | Closes the currently active document or web tab. |
| Ctrl + Shift + T | Reopen Closed Tab | Restores the most recently closed tab, preserving exact scroll position and zoom level. |
| Ctrl + Alt + B | Toggle Bookmarks Panel | Opens or closes the right-hand persistent bookmarks panel. |

Reading, Search & Study Tools
| Shortcut | Command | Action Description |
|---|---|---|
| F9 | Toggle Universal TTS | Activates or pauses Read Aloud text-to-speech for the current document or text selection. |
| Ctrl + D | Bookmark Position | Drops a persistent bookmark at your exact scroll line or PDF page number for instant return. |
| Ctrl + F | Find in Document | Opens the in-page search bar to highlight matching text within the current tab. |
| Ctrl + H | Find and Replace | Opens the find and replace bar for batch text substitutions in editor tabs. |

System & Global Utilities
| Shortcut | Command | Action Description |
|---|---|---|
| Alt + E | System Quick Note | Global Windows hotkey: Brings EleViewer to front and opens an instant scratchpad from anywhere in Windows. |
| Alt + S | Open Settings | Opens the workstation configuration dialog for themes, vaults, and browser defaults. |
| F1 | Reference Manual | Opens this documentation document in a new tab. |

---

Document Workstations Guide

EleViewer routes file formats to specialized workstation modules designed for specific academic tasks.

PDF Reader & Universal Text-to-Speech (F9)
The PDF workstation provides smooth continuous scrolling, fit-to-page/fit-to-width toolbar controls, and direct keyboard navigation (Arrow keys, PageUp, PageDown).
Universal TTS Integration: Click the Speaker button on the toolbar or press F9 to hear the document read aloud using native Windows speech synthesis. If you highlight a specific paragraph, TTS reads only your selection; if no text is selected, it reads continuously from your current page position.
Persistent Bookmarks: Press Ctrl + D while reading lengthy textbooks or research papers. EleViewer stores the exact page number and file checksum in your local database so you can jump back instantly from the Bookmarks Panel (Ctrl + Alt + B).

Markdown & Plain Text Editor Workstation
The Markdown workstation features split-screen syntax editing with a debounced real-time HTML rendered preview.
Interactive Editing Modes: Double-click anywhere on the rendered markdown preview to switch into Plain-Text Edit Mode (hiding markdown syntax formatting for distraction-free writing). Triple-click to enter Full Syntax Edit Mode.
XSS Sanitization: All rendered markdown and HTML previews pass through strict bleach XSS sanitization pipelines before rendering, preventing script injection from untrusted downloaded files.
Table & Syntax Support: Natively supports GitHub-flavored markdown tables, code syntax highlighting, blockquotes, and task checklists.

CSV Table Workstation
The CSV workstation gives you dual-view control over tabular datasets and experimental logs.
Table Grid View ⇄ Raw Text View: Toggle between an interactive spreadsheet grid and a syntax-highlighted raw text editor. Edits made in either view synchronize instantly without data loss.
Cell & Structure Editing: Double-click any cell in Grid View to edit contents. Right-click column headers or row indexes to insert or delete rows and columns.
Delimiter Overrides: Use the toolbar selector to force custom column delimiters (Comma ,, Tab \t, Semicolon ;, or Pipe |). EleViewer preserves non-standard encapsulation and text formatting non-destructively.

Office Documents (DOCX, XLSX, PPTX)
EleViewer natively parses and renders Microsoft Office document formats locally without requiring Microsoft Office or Microsoft 365 licenses installed on your machine.
DOCX & PPTX: Inspect formatting, text content, tables, and presentation slides with clean pagination and scroll support.
XLSX Spreadsheets: View multi-tab Excel workbooks, inspect cell formulas and data rows, and search large spreadsheets with zero lag.

HTML Live Workstation & Web Panel
The workstation bridges local HTML development and online web research.
HTML Live Workstation: Open local .html or .htm files in a split-screen editor. Edits reflect instantly in the live web rendered preview. Click Migrate to Web Panel in the toolbar to promote a local HTML file into a full browser session.
Integrated Web Panel (Ctrl + T): An Obsidian-inspired web browser tab that persists active URLs across application restarts. Includes dedicated navigation, refresh, and bookmark toolbar controls.
Global Hyperlink Interception: Clicking web URLs or local file links inside PDF, Markdown, or Office documents automatically opens them inside a new EleViewer tab or Web Panel instead of launching external system browsers, keeping your focus inside the workspace.

---

Data Sovereignty, Auto-Save & Crash Protection

EleViewer incorporates defensive file engineering to prevent work loss during system failures, power outages, or battery drain.

60-Second Draft Auto-Save
When editing Markdown, Plain Text, CSV, or HTML documents, a background QThread worker silently snapshots your unsaved buffer to disk every 60 seconds. Auto-save runs completely off-thread, ensuring zero UI freezing or typing latency.

Atomic Write Protection
Traditional file savers open destination files directly and overwrite them byte-by-byte. If your laptop loses power or crashes midway through a write, the file becomes a 0-byte corrupted file.
EleViewer prevents this using Atomic Writes:
All changes are written to a temporary hidden file on the same disk partition.
The operating system flushes the temporary file data completely to physical storage.
EleViewer executes an instantaneous, atomic file replacement, swapping the old file with the new file in a single OS clock cycle. Your original file remains 100% intact until the new write is verified.

Local Storage Architecture
All workspace databases, session histories, and settings reside strictly in your local Windows user directory:
Settings & Configuration: %APPDATA%\EleViewer\settings.json
Session State & Scroll Recovery: %APPDATA%\EleViewer\session.json
SQLite FTS5 Search Index: %APPDATA%\EleViewer\vault_index.db
Recent Files & Bookmark History: %APPDATA%\EleViewer\recent_files.json
Auto-Save Draft Recovery: %APPDATA%\EleViewer\drafts\

Zero Telemetry & PII Protection
EleViewer contains zero background telemetry, analytics trackers, or advertising SDKs. No usage data or document contents ever leave your computer.
Secure Crash Reporter: If an unhandled system exception occurs, EleViewer presents an opt-in crash dialog. If you choose to copy diagnostic logs to your clipboard for support, an automated PII-stripping algorithm scrubs all Windows usernames, file paths, and personal directory structures before copying the stack trace.

---

Configuration & Customization (Alt + S)

The Settings Dialog allows you to tailor the workstation's behavior and aesthetics to your study environment.

Theme & Accent Customization
EleViewer follows a high-contrast monochromatic ink-on-canvas design system. In the Settings Dialog, you can toggle between Light Mode and Dark Mode, and select from curated Dynamic Accent Colors. Accent colors apply to active tab borders, status bar badges, toolbar highlights, and focus rings without compromising text legibility.

Session Restore & Startup Behavior
By default, EleViewer enables Full Session Restore. When you launch the application:
All open document tabs and Web Panels reload in their exact previous order.
Scroll positions, text cursor coordinates, PDF page numbers, and zoom percentages are restored precisely where you left off.
You can disable Session Restore in Alt + S if you prefer starting with a clean, empty workspace on every boot.

System Tray & Background Operation
When closing the main window, EleViewer can minimize to the Windows System Tray to keep background features active:
Global Quick Note (Alt + E): Remains active in background tray mode so you can summon scratchpads while working in other Windows applications.
Double-Click Restore: Double-click the tray icon to instantly restore your workspace window.
Toggle tray minimization behavior in Alt + S under Window Preferences.

---

Troubleshooting & Support FAQ

Why is Universal Text-to-Speech (F9) silent or not reading?
EleViewer uses Windows native speech synthesis via pyttsx3. If TTS is silent:
Open Windows Settings → Time & Language → Speech.
Verify that at least one Installed voice package (e.g., Microsoft David, Zira, or Mark) is installed and enabled.
In EleViewer, ensure your system audio is unmuted and check the TTS speech rate slider on the top toolbar.

How do I recover unsaved drafts after an unexpected laptop reboot?
If Windows reboots unexpectedly while you have unsaved text in an editor tab:
Reopen EleViewer.
The workstation automatically detects orphaned snapshots in %APPDATA%\EleViewer\drafts\.
A recovery dialog prompts you to restore your unsaved drafts into active tabs. Click Restore Drafts to recover your text.

Why does the Web Panel display "WebEngine Not Available"?
If you are running EleViewer from source code (Python script) instead of the standalone .exe release, the Web Panel requires the official PySide6 WebEngine bindings:
Open your terminal and run: pip install PySide6-WebEngine
Restart python main.py to activate browser capabilities.

How do I submit bug reports, feature requests, or developer feedback?
EleViewer is built around direct user feedback:
Click Help → Submit Feedback in the top menu bar.
Type your bug report or feature request in the dialog.
Click Submit. Your message is transmitted securely (with all PII and local file paths stripped) directly to the development backlog.

---

> [!NOTE]
> For updates, source code, and release downloads, visit the official repository: https://github.com/karefined-eng/eleviewer