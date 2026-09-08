<div align="center">
  <h1>EleViewer</h1>
  <p><strong>The Unified Offline-First Study Workstation</strong></p>
  <p>
    <a href="https://github.com/karefined-eng/eleviewer/releases"><img src="https://img.shields.io/github/v/release/karefined-eng/eleviewer?style=flat-square" alt="Version"></a>
    <a href="LICENSE"><img src="https://img.shields.io/badge/License-GPLv3-blue.svg?style=flat-square" alt="License"></a>
  </p>
</div>

A lightweight Windows document editor and web browser built for deep research and focused study. EleViewer opens and edits DOCX, XLSX, PPTX, MD, TXT, CSV, TSV, HTML, and PDF files natively—no heavy third-party suites or cloud rendering needed.

---

## 📚 Why EleViewer? (The Killer Features)

Instead of forcing you to juggle separate reader, editor, and browser windows, EleViewer combines your documents and research into one interconnected workspace.

* **🚀 The Unified Workspace**
  * **Split-Screen Web Panel (`Ctrl+T`):** Browse web pages and lecture notes right alongside your documents. Web links inside PDFs or notes open directly in the side panel with page zoom controls and dedicated file downloads.
  * **Vaults & Live Search (`Alt+V`):** Connect your course folders. An embedded background search engine scans your files silently so you can find exact terms across hundreds of study documents in seconds.
  * **Session Restore & Persistent Bookmarks (`Ctrl+D`):** EleViewer remembers your open tabs and the exact reading position across your documents, so you can pick up right where you left off.
  * **Global Quick Note (`Alt+E`):** A system-wide hotkey. Press `Alt+E` from anywhere in Windows to instantly bring EleViewer forward and open a clean scratchpad.

* **🎯 Interactive Learning & Focus**
  * **Interactive Playground Tutorials:** Learn power-user workflows with hands-on, spotlight tours (**Help > Interactive Tutorials**).
  * **Distraction-Free Mode (`Ctrl+Alt+T`):** Instantly toggle the main toolbar on or off to maximize your vertical reading space.
  * **Action-First Onboarding:** Start experimenting with split-screen research and note-taking from your very first launch.

* **🔊 Advanced Reading & Data Tools**
  * **Universal Read Aloud (`F9`):** Listens to your documents on the go. High-quality neural voices when online, with an automatic fallback to Windows offline voices when disconnected.
  * **Dual-Mode Data Workstation:** Toggle instantly between a structured table view and a raw text editor for CSV and tabular data.

* **📁 Universal File Support (Zero Cloud Uploads)**
  * Opens and edits DOCX, XLSX, PPTX, PDF, MD, TXT, CSV, TSV, and HTML natively.
  * Extracts embedded images inside Word and PowerPoint files automatically.

* **✨ Privacy & Data Integrity**
  * **Crash-Resistant Saving:** Atomic writes protect your files from corruption during sudden reboots or power loss.
  * **Zero Telemetry:** No user tracking, no forced accounts, and no telemetry. All files remain strictly on your computer.

---

## 🚀 Quick Start

### Install via Windows Package Manager (Recommended)
Open PowerShell or Command Prompt and run:
```powershell
winget install karefined-eng.EleViewer
```

### Manual Download
1. Download the latest installer (`EleViewer_Setup_v1.4.0.exe`) or portable zip (`EleViewer-Portable.zip`) from the [Releases page](https://github.com/karefined-eng/eleviewer/releases).
2. Run the installer or extract the portable folder and launch `EleViewer.exe`.

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

4. Run the application:
```bash
python main.py
```

---

## ⌨️ Keyboard Shortcuts & Quick Reference

| Shortcut | Action |
|---|---|
| `Alt+E` | Global Quick Note / Bring EleViewer Forward |
| `Ctrl+N` | New Document Picker |
| `Ctrl+O` / `Ctrl+S` | Open File / Save File |
| `Ctrl+Shift+S` | Save As |
| `Ctrl+W` | Close Current Tab |
| `Ctrl+Shift+T` | Reopen Last Closed Tab |
| `Ctrl+Tab` / `Ctrl+Shift+Tab` | Cycle Through Active Tabs |
| `Ctrl+F` / `Ctrl+H` | Find / Replace in Document |
| `Ctrl+Q` | Quick Switcher (Instant File Search) |
| `Alt+V` | Toggle Study Vault Sidebar |
| `Ctrl+Alt+B` | Toggle Bookmarks Panel |
| `Ctrl+D` | Bookmark Current Document Position |
| `Ctrl+T` | Open Web Browser Panel / New Web Tab |
| `Ctrl+Alt+T` | Toggle Toolbar (Distraction-Free Mode) |
| `Ctrl++` / `Ctrl+-` / `Ctrl+0` | Web Panel Zoom In / Zoom Out / Reset Zoom |
| `F9` | Read Aloud / Toggle Speech Bar |
| `Alt+S` | Open Settings & Preferences |
| `F1` | Keyboard Shortcuts & Help |

---

## 🛠️ Building & Architecture

EleViewer uses a lightweight factory router in `file_handler.py` to route documents to their dedicated viewers (such as `pdf_viewer.py`, `docx_viewer.py`, `markdown_renderer.py`, and `xlsx_viewer.py`).

**Local Compilation:**
```bash
nuitka --standalone --lto=yes --enable-plugin=pyside6 --include-qt-plugins=sensible,styles,qwebengine --disable-console main.py
```

**Testing:**
Run the complete automated test suite via `pytest`:
```bash
pytest -s
```

---

## 🤝 Contributing
Contributions, issue reports, and suggestions are welcome! Feel free to fork the repository, open an issue, or submit a pull request.

## 📄 License
Distributed under the GNU General Public License v3 (GPLv3). See [LICENSE](LICENSE) for full details.