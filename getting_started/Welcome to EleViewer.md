---
title: Start Studying with EleViewer
description: A short first-session guide for opening course files, listening to readings, and organizing local study folders.
---

# Start studying with EleViewer

EleViewer keeps your course files in one Windows workspace. Open a Word document, PDF, slide deck, spreadsheet, or note without closing the file you are already using. Your files stay on your computer, and no account is required.

> **A common study task:** Open your document with `Ctrl + O`, then press `Ctrl + O` again to open the PDF you need. Switch between both tabs instead of closing one to reach the other.

## Your first three actions

1. Press `Alt + V`, open Settings with `Alt + S`, and add your course folder to unlock the **Vault Explorer & Background Search Engine**.
2. Press `Ctrl + T` to open the **Split-Screen Web Panel** and research alongside your local notes.
3. Close the app—**Session Restore** will remember your exact tabs and scroll positions next time.
4. Drop a **Persistent Bookmark** (`Ctrl + D`) or hit `Alt + E` from anywhere in Windows to open a **Global Quick Note**.

You can return to this guide at any time with `F1` or from **Help → Getting Started Guide**. The reference sections below explain the rest of the workspace when you are ready.

---

## 1. The Unified Workspace (Vaults, Tabs, and the Web)

EleViewer operates on a strict **local-first** architecture, but it's designed to be a complete study workstation rather than a generic text editor. Here is how to use the killer features:

### Setting Up Your Vault Explorer (`Alt + V`)
The Vault Explorer is your course-folder sidebar.
1. Press `Alt + V` to toggle the **Vault Explorer**.
2. Click the **Settings icon** (⚙️) or press `Alt + S` to open the **Settings Dialog**.
3. Click **Add Folder** and select any local directory containing your study materials.
4. EleViewer's **background search engine** instantly scans your documents, making them searchable across their full text.

### Split-Screen Web Panel (`Ctrl + T`)
You don't need to leave the app to research.
1. Press `Ctrl + T` to open the **Web Panel** right alongside your local notes.
2. If you click a web hyperlink inside any of your PDFs or Markdown documents, EleViewer will automatically intercept the click and open it in the Web Panel, keeping your focus locked in one window.

### Session Restore & Bookmarks (`Ctrl + D`)
EleViewer respects your time. 
- When you close the app, **Session Restore** remembers exactly which tabs you had open, your exact scroll position, and your PDF zoom levels. They will all restore perfectly on your next launch.
- Press `Ctrl + D` anywhere in a document (even a 400-page PDF) to drop a **Persistent Bookmark**. Use `Ctrl + Alt + B` to open the Bookmarks Panel and jump back instantly.

---

## 2. Shortcuts you can learn later

You do not need to memorize every shortcut to begin. These commands become useful as your study sessions grow longer:

### File Navigation & Vault Management
| Shortcut | Command | Action Description |
|---|---|---|
| **Ctrl + Q** | **Quick Switcher** | Opens a fuzzy search overlay to find and open vault files by typing a few letters. |
| **Alt + V** | **Toggle Vault Sidebar** | Collapses or expands the left-hand directory tree for distraction-free focus mode. |
| **Ctrl + N** | **New File Picker** | Creates a new Markdown, TXT, CSV, or HTML document in your active directory. |
| **Ctrl + O** | **Open File** | Opens a native system file dialog to load external documents outside your vault. |
| **Ctrl + S** | **Save File** | Immediately writes active editor changes to disk using atomic save protection. |
| **Ctrl + Shift + S** | **Save As** | Saves the current document under a new filename or location. |

### Tab & Window Control
| Shortcut | Command | Action Description |
|---|---|---|
| **Ctrl + T** | **New Web Tab / Panel** | Opens an integrated web browser tab directly alongside your local study notes. |
| **Ctrl + W** | **Close Tab** | Closes the currently active document or web tab. |
| **Ctrl + Shift + T** | **Reopen Closed Tab** | Restores the most recently closed tab, preserving exact scroll position and zoom level. |
| **Ctrl + Alt + B** | **Toggle Bookmarks Panel** | Opens or closes the right-hand persistent bookmarks panel. |

### Reading, Search & Study Tools
| Shortcut | Command | Action Description |
|---|---|---|
| **F9** | **Toggle Universal TTS** | Activates or pauses Read Aloud text-to-speech for the current document or text selection. |
| **Ctrl + D** | **Bookmark Position** | Drops a persistent bookmark at your exact scroll line or PDF page number for instant return. |
| **Ctrl + F** | **Find in Document** | Opens the in-page search bar to highlight matching text within the current tab. |
| **Ctrl + H** | **Find and Replace** | Opens the find and replace bar for batch text substitutions in editor tabs. |

### System & Global Utilities
| Shortcut | Command | Action Description |
|---|---|---|
| **Alt + E** | **System Quick Note** | Global Windows hotkey: Brings EleViewer to front and opens an instant scratchpad from anywhere in Windows. |
| **Alt + S** | **Open Settings** | Opens the workstation configuration dialog for themes, vaults, and browser defaults. |
| **F1** | **Reference Manual** | Opens this documentation document in a new tab. |

---

## 3. Reading, notes, and other file types

EleViewer routes file formats to specialized workstation modules designed for specific academic tasks.

### PDF Reader & Universal Text-to-Speech (`F9`)
The PDF workstation provides smooth continuous scrolling, fit-to-page/fit-to-width toolbar controls, and direct keyboard navigation (Arrow keys, `PageUp`, `PageDown`).
- **Universal TTS Integration:** Click the Speaker button on the toolbar or press `F9` to hear the document read aloud using native Windows speech synthesis. If you highlight a specific paragraph, TTS reads only your selection; if no text is selected, it reads continuously from your current page position.
- **Persistent Bookmarks:** Press `Ctrl + D` while reading lengthy textbooks or research papers. EleViewer stores the exact page number and file checksum in your local database so you can jump back instantly from the Bookmarks Panel (`Ctrl + Alt + B`).

### Markdown & Plain Text Editor Workstation
The Markdown workstation features split-screen syntax editing with a debounced real-time HTML rendered preview.
- **Interactive Editing Modes:** Double-click anywhere on the rendered markdown preview to switch into **Plain-Text Edit Mode** (hiding markdown syntax formatting for distraction-free writing). Triple-click to enter **Full Syntax Edit Mode**.
- **Safe Previews:** All rendered markdown and HTML previews pass through strict security sanitization before rendering, preventing malicious scripts from running in downloaded files.
- **Table & Syntax Support:** Natively supports GitHub-flavored markdown tables, code syntax highlighting, blockquotes, and task checklists.

### CSV Table Workstation
The CSV workstation gives you dual-view control over tabular datasets and experimental logs.
- **Table Grid View ↔ Raw Text View:** Toggle between an interactive spreadsheet grid and a syntax-highlighted raw text editor. Edits made in either view synchronize instantly without data loss.
- **Cell & Structure Editing:** Double-click any cell in Grid View to edit contents. Right-click column headers or row indexes to insert or delete rows and columns.
- **Delimiter Overrides:** Use the toolbar selector to force custom column delimiters (Comma `,`, Tab `\t`, Semicolon `;`, or Pipe `|`). EleViewer preserves non-standard encapsulation and text formatting non-destructively.

### Office Documents (DOCX, XLSX, PPTX)
EleViewer natively parses and renders Microsoft Office document formats locally without requiring Microsoft Office or Microsoft 365 licenses installed on your machine.
- **DOCX & PPTX:** Inspect formatting, text content, tables, presentation slides, and inline embedded images natively, with clean pagination and scroll support.
- **XLSX Spreadsheets:** View multi-tab Excel workbooks, inspect cell formulas and data rows, and search large spreadsheets with zero lag.

### HTML Live Workstation & Web Panel
The workstation bridges local HTML development and online web research.
- **HTML Live Workstation:** Open local `.html` or `.htm` files in a split-screen editor. Edits reflect instantly in the live web rendered preview. Click **Migrate to Web Panel** in the toolbar to promote a local HTML file into a full browser session.
- **Integrated Web Panel (`Ctrl + T`):** An Obsidian-inspired web browser tab that persists active URLs across application restarts. Includes dedicated navigation, refresh, and bookmark toolbar controls.
- **Global Hyperlink Interception:** Clicking web URLs or local file links inside PDF, Markdown, or Office documents automatically opens them inside a new EleViewer tab or Web Panel instead of launching external system browsers, keeping your focus inside the workspace.

---

## 4. Your files, drafts, and privacy

EleViewer incorporates defensive file engineering to prevent work loss during system failures, power outages, or battery drain.

### 60-Second Draft Auto-Save
When editing Markdown, Plain Text, CSV, or HTML documents, EleViewer silently snapshots your unsaved work to disk every 60 seconds. Auto-save runs completely in the background, ensuring zero freezing or typing lag.

### Safe Saving & Draft Protection
Traditional file savers open destination files directly and overwrite them byte-by-byte. If your laptop loses power midway through a write, the file becomes corrupted.
EleViewer prevents this using **Safe Saving**:
1. All changes are written to a temporary hidden file first.
2. The operating system completely finishes saving the temporary file.
3. EleViewer instantly swaps the old file with the new file in one quick motion. Your original file remains 100% intact until the new version is completely verified.

### Local Storage Architecture
All workspace databases, session histories, and settings reside strictly in your local Windows user directory:
- **Settings & Configuration:** `%APPDATA%\EleViewer\settings.json`
- **Session State & Scroll Recovery:** `%APPDATA%\EleViewer\session.json`
- **Search Index:** `%APPDATA%\EleViewer\vault_index.db`
- **Recent Files & Bookmark History:** `%APPDATA%\EleViewer\recent_files.json`
- **Auto-Save Draft Recovery:** `%APPDATA%\EleViewer\drafts\`

### Zero Telemetry & PII Protection
EleViewer contains **zero background telemetry, analytics trackers, or advertising SDKs**. No usage data or document contents ever leave your computer.
- **Secure Crash Reporter:** If an unhandled system exception occurs, EleViewer presents an opt-in crash dialog. If you choose to copy diagnostic logs to your clipboard for support, an automated privacy algorithm scrubs all Windows usernames, file paths, and personal folder names before copying the error report.

---

## 5. Settings and customization (`Alt + S`)

The Settings Dialog allows you to tailor the workstation's behavior and aesthetics to your study environment.

### Theme & Accent Customization
EleViewer follows a high-contrast monochromatic ink-on-canvas design system. In the Settings Dialog, you can toggle between **Light Mode** and **Dark Mode**, and select from curated **Dynamic Accent Colors**. Accent colors apply to active tab borders, status bar badges, toolbar highlights, and focus rings without compromising text legibility.

### Session Restore & Startup Behavior
By default, EleViewer enables **Full Session Restore**. When you launch the application:
- All open document tabs and Web Panels reload in their exact previous order.
- Scroll positions, text cursor coordinates, PDF page numbers, and zoom percentages are restored precisely where you left off.
- You can disable Session Restore in `Alt + S` if you prefer starting with a clean, empty workspace on every boot.

### System Tray & Background Operation
When closing the main window, EleViewer can minimize to the Windows System Tray to keep background features active:
- **Global Quick Note (`Alt + E`):** Remains active in background tray mode so you can summon scratchpads while working in other Windows applications.
- **Double-Click Restore:** Double-click the tray icon to instantly restore your workspace window.
- Toggle tray minimization behavior in `Alt + S` under **Window Preferences**.

### Automatic Updates & First-Run
To keep you focused on studying, EleViewer handles updates silently:
- **Auto-Updater:** A lightweight background check securely queries the latest release on GitHub. When an update is available, it gracefully notifies you and seamlessly downloads the installer without forcing an immediate restart.
- **Interactive Onboarding:** On your first run or major feature updates, EleViewer displays an interactive onboarding and release notes dialog so you are always up to speed with new reflexes and capabilities.

---

## 6. Troubleshooting and support

### I need a PDF while I am working on another document
Press `Ctrl + O` and choose the PDF. EleViewer opens it in a new tab, so your Word document, notes, and PDF can stay open together. Use `Ctrl + 1` through `Ctrl + 9` to move between tabs quickly.

### I want to save my place
Press `Ctrl + D` while the document has focus. In a PDF this saves the current page; in a text or office document it saves the current reading position. Press `Ctrl + Alt + B` to show your saved bookmarks.

### I found a problem or have an idea
Use [Report a bug](https://github.com/karefined-eng/eleviewer/issues) or [request a feature](https://github.com/karefined-eng/eleviewer/issues/new). Include what you were trying to do and which file type you opened. Do not attach private course files.

### Why is Universal Text-to-Speech (`F9`) silent or not reading?
EleViewer uses Windows native speech synthesis. If the speech is silent:
1. Open Windows **Settings → Time & Language → Speech**.
2. Verify that at least one **Installed voice package** (e.g., Microsoft David, Zira, or Mark) is installed and enabled.
3. In EleViewer, ensure your system audio is unmuted and check the speech rate slider on the top toolbar.

### How do I recover unsaved drafts after an unexpected laptop reboot?
If Windows reboots unexpectedly while you have unsaved text in an editor tab:
1. Reopen EleViewer.
2. The workstation automatically detects orphaned snapshots in `%APPDATA%\EleViewer\drafts\`.
3. A recovery dialog prompts you to restore your unsaved drafts into active tabs. Click **Restore Drafts** to recover your text.

### Why does the Web Panel display "WebEngine Not Available"?
If you are running EleViewer from source code (Python script) instead of the standalone `.exe` release, the Web Panel requires the official PySide6 WebEngine bindings:
- Open your terminal and run: `pip install PySide6-WebEngine`
- Restart `python main.py` to activate browser capabilities.

### How do I submit bug reports, feature requests, or developer feedback?
EleViewer is built around direct user feedback:
1. Click **Help â†’ Submit Feedback** in the top menu bar.
2. Type your bug report or feature request in the dialog.
3. Click **Submit**. Your message is transmitted securely (with all personal information and local file paths stripped) directly to the development backlog.

---

> [!NOTE]
> For updates, source code, and release downloads, visit the official repository: **https://github.com/karefined-eng/eleviewer**
