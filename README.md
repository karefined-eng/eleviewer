<div align="center">
  <h1>EleViewer</h1>
  <p><strong>The Unified Offline-First Study Workstation</strong></p>
  <p>
    <a href="https://github.com/karefined-eng/eleviewer/releases"><img src="https://img.shields.io/github/v/release/karefined-eng/eleviewer?style=flat-square" alt="Version"></a>
    <a href="LICENSE"><img src="https://img.shields.io/badge/License-GPLv3-blue.svg?style=flat-square" alt="License"></a>
  </p>
</div>

A lightweight Windows document editor and web browser built for deep research. EleViewer supports DOCX, XLSX, PPTX, MD, TXT, CSV, TSV, HTML, and PDF, all powered natively by Python and PySide6.

## 📚 Why EleViewer? (The Killer Features)

Instead of a generic text editor, EleViewer is an interconnected workspace designed to eliminate context switching during your study or research sessions.

*   **🚀 The Unified Workspace**
    *   **Split-Screen Web Panel (`Ctrl+T`):** Browse the web directly alongside your local documents. Hyperlinks inside your PDFs or Markdown notes open in the Web Panel instead of kicking you out to Chrome.
    *   **Vaults & Live Search (`Alt+V`):** Connect your local study folders. The embedded background search engine silently scans everything, allowing you to instantly search across hundreds of course files simultaneously.
    *   **Persistent Bookmarks (`Ctrl+D`):** Drop a bookmark on page 342 of a massive textbook or deep within a Markdown file. EleViewer remembers the exact scroll coordinate so you can jump back instantly later.
    *   **Global Quick Note (`Alt+E`):** A system-wide Windows hotkey. Press `Alt+E` from anywhere in Windows to instantly bring EleViewer to the front and open a new blank scratchpad.

*   **🔊 Advanced Reading & Data Tools**
    *   **Hybrid Neural Text-to-Speech (`F9`):** Reads documents aloud to you. It automatically uses high-quality Microsoft Neural voices when online, and seamlessly falls back to native Windows offline voices when disconnected.
    *   **Dual-Mode CSV Workstation:** Toggle instantly between a beautiful Table Grid View and a raw text editor, with automatic encoding detection so your data never looks garbled.

*   **📁 Universal File Support (Zero Cloud Rendering)**
    *   Opens & edits DOCX, XLSX, PPTX, PDF, MD, TXT, CSV, TSV and HTML natively — no heavy LibreOffice wrappers and no uploading files to a cloud renderer.
    *   Inline Image Extraction natively renders embedded pictures inside DOCX and PPTX files.

*   **✨ Security & Reliability**
    *   **Atomic Writes:** Zero-byte file corruption prevention on sudden crash or power loss.
    *   **Zero Telemetry:** No mandatory logins, no tracking. Your files stay local.

## 🚀 Quick Start

### For End Users
EleViewer is a portable `~129 MB` standalone Windows executable. No installation required.
1. Download the latest `EleViewer.exe` from the [Releases page](https://github.com/karefined-eng/eleviewer/releases).
2. Run `EleViewer.exe`.

### For Developers
**Prerequisites:** Windows 10/11, Python 3.9+, Git.

1. Clone the repository:
```bash
git clone https://github.com/karefined-eng/eleviewer.git
cd eleviewer
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
.venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```
*(Note: To use the embedded Web Panel, ensure you have the optional `PySide6-WebEngine` package installed, which is included in the requirements).*

4. Run the application:
```bash
python main.py
```

## ⌨️ Keyboard Shortcuts & Usage

| Shortcut | Action |
|---|---|
| `Alt+E` | System-Wide Quick Note / Summon |
| `Ctrl+N` | New File picker |
| `Ctrl+O` / `Ctrl+S` | Open file / Save file |
| `Ctrl+Shift+S` | Save As |
| `Ctrl+W` | Close tab |
| `Ctrl+Shift+T` | Reopen closed tab |
| `Ctrl+F` / `Ctrl+H`| Find in document / Find and Replace |
| `Ctrl+Q` | Quick switcher (search files) |
| `Alt+V` | Toggle Vault (Folder Explorer) |
| `Ctrl+Alt+B`| Toggle Bookmarks Panel |
| `Ctrl+D` | Bookmark current file position / page |
| `F9` | Read Aloud / Toggle TTS Bar |
| `Ctrl+T` | Open Web Browser Panel / New Web Tab |
| `Ctrl++` / `Ctrl+-` | Zoom In / Zoom Out (Web Panel) |
| `Alt+S` | Open Settings |

## 🛠️ Building & Architecture

EleViewer uses a factory pattern for file handling. `filehandler.py` routes files to the correct viewer module (e.g., `docxviewer.py`, `xlsxviewer.py`, `pdfviewer.py`).

**Packaging:**
The release workflow uses Nuitka `--onefile` plus Inno Setup to produce a standalone portable executable and a Windows installer.
```bash
nuitka --onefile --plugin-enable=pyside6 --include-qt-plugins=sensible,styles --disable-console main.py
```

**Testing:**
All tests are run via `pytest` from the repository root:
```bash
pytest -s
```

## 🤝 Contributing
This project is open-source. Feel free to fork it, create a branch, and submit a pull request!

## 📄 License
GNU GPLv3 License — see the `LICENSE` file for details.