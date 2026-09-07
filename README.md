EleViewer

!Version
!License
!Downloads

A lightweight Windows document editor supporting DOCX, XLSX, PPTX, MD, TXT, CSV, TSV, HTML/HTM, and PDF. Built with Python and PySide6.

📚 Why EleViewer? (The Killer Features)

Instead of a generic text editor, EleViewer is an offline-first, interconnected study workstation. Here is what makes it unique:

🚀 The Unified Workspace
Split-Screen Web Panel (Ctrl+T) — Browse the web directly alongside your local documents. Includes smooth page zoom (Ctrl++, Ctrl+-, Ctrl+0), integrated file downloads with progress tracking, tab hover previews, and a right-click context menu. Hyperlinks inside your PDFs or Markdown notes open in the Web Panel instead of kicking you out to Chrome, keeping your focus locked.
Vaults & Live Search (Alt+V) — Connect your local study folders. The embedded background search engine silently scans everything, allowing you to instantly search across hundreds of course files simultaneously.
Session Restore — Respects your time. If you close the app with 8 tabs open, a split-screen web page, and a specific PDF zoom, your entire workstation restores exactly as you left it on the next launch.
Persistent Bookmarks (Ctrl+D) — Drop a bookmark on page 342 of a massive textbook or deep within a Markdown file. EleViewer remembers the exact scroll coordinate so you can jump back instantly later.
Global Quick Note (Alt+E) — A system-wide Windows hotkey. Press Alt+E from anywhere in Windows to instantly bring EleViewer to the front and open a new blank scratchpad.
Intuitive & Customizable Toolbar — Clear, readable text labels under each icon make every action immediately intuitive, with customizable display options in Settings.
Expanded Study Preferences (Alt+S) — Six dedicated settings tabs to tailor your downloads folder, default zoom, editor fonts, line wrapping, PDF continuous scrolling, speech speeds, and vault search scope.

🔊 Advanced Reading & Data Tools
Hybrid Neural Text-to-Speech (F9) — Reads documents aloud to you. It automatically uses high-quality Microsoft Neural voices when online, and seamlessly falls back to native Windows offline voices when disconnected.
Dual-Mode CSV Workstation — Toggle instantly between a beautiful Table Grid View and a raw text editor, with automatic encoding detection so your data never looks garbled.
HTML Live Workstation — Split-screen syntax editor with debounced live previews and 1-click migration into the Web Panel.

📁 Universal File Support (Zero Cloud Rendering)
Opens & edits DOCX, XLSX, PPTX, PDF, MD, TXT, CSV, TSV and HTML/HTM — all parsed natively using pure Python and PySide6.
No heavy LibreOffice wrappers. No uploading files to a cloud renderer.
XLSX View-Only Mode displays computed formula values to protect spreadsheet integrity.
Inline Image Extraction natively renders embedded pictures inside DOCX and PPTX files.

✨ Security & Reliability
Atomic Writes — zero-byte file corruption prevention on sudden crash or power loss.
Safe Previews — strict security sanitization before rendering Markdown and HTML.
Smooth Performance — draft recovery autosave and live vault searches run silently in the background to prevent your app from freezing.
Zero Telemetry — no mandatory logins, no tracking. Includes an opt-in, privacy-focused secure crash reporter.

💻 Specs
~129 MB compiled one-file portable Windows executable — no traditional installation required.
< 100 ms cold-start latency.
Windows 10/11 native integration (Jump Lists, AppUserModelID, ProgIDs).
No account, zero telemetry — your files stay local. Includes an opt-in, PII-stripped secure crash reporter that automatically copies technical logs to your clipboard without exposing your personal username or file paths.
Flesch-Kincaid Compliant Copy — all user-facing text follows the Paul Graham / Ogilvy "write like you talk" framework at a 6th-to-8th grade reading level for effortless scanning.
GNU GPLv3 licensed, open source (Python + PySide6).
Free forever, no ads.

🚀 Quick Start

For End Users
Download the latest EleViewer.exe from the releases page.
Run EleViewer.exe. The current published release is portable and does not require a traditional installation.

What’s new in v1.4.0
Enhanced Split-Screen Web Browser — Scale pages easily with keyboard zoom (Ctrl++, Ctrl+-, Ctrl+0) or Ctrl+Scroll with a live zoom badge, download study materials directly into your Downloads folder with an animated progress bar, hover over tabs to see full titles and web addresses, and enjoy a quick right-click context menu.
Action-First Interactive Onboarding — A dynamic, interactive playground designed to teach you EleViewer’s core features (Split-Screen Web Panel, Search, Settings) by having you actively use them right when you launch the app, completely avoiding boring, passive tutorial slides.
Bulletproof Feedback Dialog — Submitting bug reports is now foolproof. If the backend API ever experiences rate limits or network failures, EleViewer automatically degrades gracefully, opening your default web browser to a pre-filled GitHub issue page so your feedback is never lost.
Web Panel Video & Layout Polish — Enjoy seamless, full-screen video playback in the browser panel with `Esc` to exit, perfectly proportioned 16px navigation icons, and tightened native-feeling margins.
Intuitive Toolbar with Clear Labels — Prominent text labels under each icon make tools immediately obvious, with settings to customize layout (labels under icons, compact icons, or labels beside icons).
Expanded Settings Dialog — Six dedicated tabs for configuring downloads destination, default zoom levels, editor font size and word wrapping, PDF scrolling, speech speeds, and vault search scopes.
Visual Bookmarks — Type-specific icons (globe for web links, document icons for local files) and clean one-click bookmark deletion.

For Developers

Prerequisites: Windows 10/11, Python 3.9+, Git.

Clone the repository:
```bash
git clone https://github.com/karefined-eng/eleviewer.git
cd eleviewer
```

Create a virtual environment (recommended):
```bash
python -m venv venv
venv\Scripts\activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```
The requirements include PPTX parsing through python-pptx. For the embedded web panel, install the optional Qt WebEngine package as well: pip install PySide6-WebEngine. Without it, EleViewer remains usable for local documents but shows a clear warning when web-panel features are requested.

Run the application:
```bash
python main.py
```

⌨️ Keyboard Shortcuts & Usage

| Shortcut | Action |
|---|---|
| Alt+E | System-Wide Quick Note / Summon (Brings EleViewer to front & opens new note from anywhere in Windows) |
| Ctrl+N | New File picker |
| Ctrl+O / Ctrl+S | Open file / Save file |
| Ctrl+Shift+S | Save As |
| Ctrl+W | Close tab |
| Ctrl+Shift+T | Reopen closed tab |
| Ctrl+F | Find in document |
| Ctrl+H | Find and Replace |
| Ctrl+Q | Quick switcher (search files) |
| Alt+V | Toggle Vault (Folder Explorer) |
| Ctrl+Alt+B| Toggle Bookmarks Panel |
| Ctrl+D | Bookmark current file position / page |
| F9 | Read Aloud / Toggle TTS Bar |
| F1 | Open Getting Started Guide |
| Ctrl+T | Open Web Browser Panel / New Web Tab |
| Ctrl+Plus / Ctrl+Minus | Zoom In / Zoom Out (Web Panel) |
| Ctrl+0 | Reset Zoom to 100% (Web Panel) |
| Alt+S | Open Settings |

Feature Details
Markdown: Double-click the preview for a simple plain-text edit (hides markdown symbols). Triple-click for a full syntax edit. HTML previews are sanitized against XSS attacks.
PDFs: Use the toolbar to fit-to-page/width, use arrow keys to navigate, and click the speaker icon to read aloud.
Vaults: Add multiple project folders. Switch between them via the sidebar dropdown. Set up vaults via the + icon.
Web Panel: Persists URLs between sessions. Supports smooth page zoom (Ctrl++/Ctrl+-/Ctrl+0 or Ctrl+Scroll), inline file downloads to your Downloads folder, tab hover previews, and right-click context actions. Configure the default new tab URL in the Settings menu.

🛠️ Building Locally

The current desktop build path is a standard Python + PySide6 workflow.

```bash
Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate

Install the app dependencies
pip install -r requirements.txt

Start the app
python main.py
```

If you want a packaged build, the release workflow uses Nuitka --onefile plus Inno Setup to produce a standalone portable EleViewer.exe and a Windows installer.

```bash
nuitka --onefile --plugin-enable=pyside6 --include-qt-plugins=sensible,styles --disable-console main.py
```

Release hashes can still be generated from the packaged artifact with:

```bash
python release_hash.py
```

📁 Architecture & Structure

EleViewer uses a factory pattern for file handling. filehandler.py routes files to the correct viewer module (e.g., docxviewer.py, xlsxviewer.py, pdfviewer.py).

Key directories and modules:
main.py, ui.py, filehandler.py — First stop for new contributors. main.py boots the app, ui.py manages the main window and toolbar, and filehandler.py routes supported file types to viewer modules.
editor.py & markdown_renderer.py — Text and markdown editors with sanitized preview rendering.
pdfviewer.py, docxviewer.py, pptxviewer.py, xlsxviewer.py, csv_viewer.py — Format-specific viewers.
vaultexplorer.py, vaultsearch.py, vault_indexer.py — Vault browser, live search, and a pure-Python SQLite FTS5 indexer.
draftrecovery.py, feedbackdialog.py — Background QThread workers for auto-save and feedback submission.
sessionmanager.py, saveutils.py, settings.py — Atomic writes, settings, and session scroll/zoom/page restore.
release_hash.py — SHA-256 release hash generator used by the installer and GitHub release flow.
Tests live in the repository root as test_*.py files. Use them to understand current behavior and validate your work.
Data is stored in %APPDATA%\EleViewer\ (recentfiles.json, settings.json, session.json, vaultindex.db, etc.)

🧪 Testing

All tests are run via pytest from the repository root.

To run the full suite with live output:
```bash
pytest -s
```

To run a specific test file:
```bash
pytest -s testallui_actions.py
pytest -s testmarkdownrenderer.py
```

If a test fails due to missing dependencies, ensure you have installed the requirements:
```bash
pip install -r requirements.txt
```

ModuleNotFoundError (e.g., 'PySide6', 'docx'): Install missing packages from requirements.txt.
Web panel not available: Install the optional web engine dependency:
```bash
pip install PySide6-WebEngine
```
PDF read-aloud not working: Ensure pyttsx3 is installed and Windows speech voices are enabled in OS settings. For higher quality neural voices, install edge-tts.

🛡️ The Offline-First Philosophy
Independent utility apps often suffer from bloated file-rendering engines, heavy cloud dependencies, or unpolished UIs. EleViewer explicitly rejects this trend:
No Heavy Wrappers: Instead of bundling a 200MB LibreOffice clone, we use pure-Python data extraction (like mammoth and python-pptx) to parse binary data and base64-encode it directly into PySide6 native UIs.
Zero Cloud Rendering: No documents are ever uploaded to a server to be rendered.
Graceful Degradation: Cloud-assisted features (like Microsoft Neural TTS) seamlessly fall back to local Windows COM APIs when offline, ensuring your study session never crashes in a dead zone.

🤝 Contributing

This project is open-source. Feel free to fork it, create a branch, and submit a pull request!

📄 License

GNU GPLv3 License — see the LICENSE file for details.

✍️ Author
Built by karefined-eng