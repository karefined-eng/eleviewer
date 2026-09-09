# 🏛️ EleViewer Free Windows Document Reader — Current Implementation & Technical Outcomes Ledger

> **Document Status:** Comprehensive Synthesis of Ingested Context, Architectural Audits, Feature Roadmaps, and Live Codebase State.  
> **Target Audience:** Core Developers, AI Engineering Agents, Technical Auditors, and Maintainers.  
> **Last Updated:** September 8, 2026  
> **Repositories Covered:** `eleviewer` (Desktop App — PySide6/Python) & `eleviewer-site` (Web Platform — Next.js/Tailwind)

---

## 1. Executive Summary & Free Windows Document Reader Philosophy

**EleViewer** is an offline-first, portable document reader and study workstation designed primarily for undergraduates, academic power users, and researchers on Windows 10/11. It operates under the **"Free Windows Document Reader"** design philosophy:

* **Lightweight Footprint:** Sub-50MB idle RAM boot footprint (achieved via lazy-loading of Chromium), sub-100ms cold-start latency (via Nuitka LTO compilation), and smooth execution even on low-spec hardware.
* **Local File Privacy:** 100% offline-first operations. Zero telemetry, zero user tracking, and no required online accounts. All notes, bookmarks, drafts, and configurations live locally on the student's machine.
* **Zero-Cost Tooling:** Open-source under the **GNU GPLv3** license. Free forever to prevent proprietary "digital extractivism" while retaining optional SaaS cloud sync capabilities via the GPLv3 "SaaS Loophole".
* **Keyboard Ergonomics:** Built around core muscle-memory Keyboard Shortcuts (`Ctrl+Q` Quick Switcher, `Alt+V` Vault Sidebar, `Ctrl+T` Web Panel, `Ctrl+Shift+T` Restore Tab, `Ctrl+Alt+T` Distraction-Free Toolbar Toggle) and Universal Text-to-Speech (`F9`).

---

## 2. Core Architecture & Factory Pattern Routing

The application architecture is structured around strict separation of concerns, decoupling UI controls from file parsing logic via a dynamic **Factory Pattern Router** (`file_handler.py`).

```
                              ┌──────────────────────────────────┐
                              │            ui.py                 │
                              │   (EleViewerMainWindow / Tabs)   │
                              └─────────────────┬────────────────┘
                                                │
                                                ▼
                              ┌──────────────────────────────────┐
                              │         file_handler.py          │
                              │    (Factory Pattern Router)      │
                              └─────────────────┬────────────────┘
                                                │
        ┌───────────────┬───────────────────────┼───────────────┬──────────────┬──────────────┐
        ▼               ▼                       ▼               ▼              ▼              ▼
 ┌─────────────┐ ┌─────────────┐         ┌─────────────┐ ┌─────────────┐ ┌────────────┐ ┌────────────┐
 │ pdf_viewer  │ │ docx_viewer │         │ xlsx_viewer │ │ pptx_viewer │ │ markdown_  │ │csv/html/txt│
 │  (QPdfView) │ │(python-docx │         │ (QTableView │ │(python-pptx │ │  renderer  │ │  viewers   │
 │             │ │  + QText)   │         │  Virtual)   │ │  + win32com)│ │ (QTextBro- │ │            │
 └─────────────┘ └─────────────┘         └─────────────┘ └─────────────┘ │    wser)   │ └────────────┘
                                                                         └────────────┘
```

### Key Architectural Anchors:
1. **Dynamic Format Dispatching:** `file_handler.py` inspects file extensions (`.pdf`, `.docx`, `.xlsx`, `.pptx`, `.md`, `.csv`, `.html`, `.txt`) and instantiates the respective viewer widget, ensuring that a parsing failure in one format never crashes the global UI thread.
2. **Flexible Method Signatures:** All MainWindow file handlers (e.g. `open_file(self, file_path=None)`) support optional positional/keyword arguments to safely receive input from CLI arguments, IPC single-instance sockets (`instance_lock.py`), or onboarding dialogs without `TypeError` crashes.
3. **C++ Object Lifecycle Management:** Tab closures (`removeTab()`) explicitly invoke `.deleteLater()` on child widgets and `.page().deleteLater()` on web components to prevent memory leaks and orphaned C++ process allocations.

---

## 3. Supported Document Formats & Implementation Specifications

| Format | Parsing Engine | Rendering Component | Special Features & Highlights |
| :--- | :--- | :--- | :--- |
| **PDF (`.pdf`)** | Native QtPdf (`QPdfDocument`) | `QPdfView` (Native PySide6) | High-resolution vector zoom, page thumbnail panel, two-page layout, threaded text prefetching via `PdfTextWorker`, sidecar `.ele` JSON bookmark persistence, Universal TTS (`F9`). Replaced legacy `fitz`/PyMuPDF dependency in v1.2.0. |
| **Word (`.docx`)** | `python-docx` + `zipfile` XML fallback | `QTextBrowser` Rich-Text Canvas | **Structured Study Document Mode**: Extracts headings, text, tables, and Base64-embedded images (`data:image/png;base64,...`). Dual-Layer Editing locks layout/XML schema to prevent file corruption upon saving. |
| **Excel (`.xlsx`)** | `openpyxl` + `zipfile` fallback | `QTableView` (Model/View Virtualized) | Virtualized grid rendering handling 100,000+ rows at 60 FPS. Only viewport cells are processed, preventing RAM spikes. Cell-by-cell and row-by-row navigation for Universal TTS. |
| **PowerPoint (`.pptx`)** | Dual-Engine: `win32com` (MS Office) & `python-pptx` | `QPdfView` or Slide-by-Slide `QTextBrowser` | Silent background PDF conversion when MS Office is present; native `python-pptx` fallback extracting slide titles, text, and embedded images slide-by-slide when Office is absent. |
| **Markdown (`.md`)** | `markdown_utils.py` + `markdown` | `markdown_renderer.py` / `editor.py` | Dual Mode (Live Rendered Preview & Plain Text Editor). Integrated Math LaTeX rendering (`<sup>`, `<sub>`), task list checkboxes (`- [ ]`), dynamic syntax highlighting (`syntax_highlighter.py`), and atomic auto-saving. |
| **CSV (`.csv`)** | Python `csv` module | `csv_viewer.py` (`QTableView` Virtualized) | Auto-detects delimiters (comma, tab, semicolon), high-speed virtualized cell scrolling, search filtering, export to formatted CSV. |
| **HTML (`.html`)** | `html_viewer.py` | `QTextBrowser` / Native HTML Engine | Clean HTML parsing with sanitized tag whitelist. Protected against `white-space: pre-wrap` rendering glitches on embedded images. |
| **Plain Text (`.txt`)** | Native Python I/O (`UTF-8`) | `editor.py` (`QPlainTextEdit`) | Fast plain-text editing with line numbers, word count, cursor position tracking (`Ln X, Col Y`), and find/replace support. |

---

## 4. Key Subsystems & Technical Implementations

### 4.1. Universal TTS Engine & Floating Reader Bar (`tts_engine.py` & `tts_reader_bar.py`)
* **Shortcut:** `F9` (Read Aloud Toggle).
* **Multi-Engine Audio Layer:** Supports offline native Windows **SAPI5** (`pyttsx3`) as primary offline fallback, **`edge-tts`** for online Microsoft neural voices, and architecture prepared for **Kokoro-82M / Piper ONNX** local neural models.
* **Floating Dock Control Bar:** Shows document title, current page / total pages, playing/paused status, speed control slider, and a blue speaker indicator icon (`BRAND_ACCENT`).
* **Non-Blocking Interruption:** Thread cancellation instantly purges pending audio queues and calls native `engine.stop()` to abort blocking speech loops instantly without stalling the GUI.

### 4.2. Vault Explorer & Deep Search Engine (`vault_explorer.py` & `vault_search.py`)
* **Vault Sidebar (`Alt+V`):** Tree view of student course folders, fast directory expansion using `os.path.abspath()` string normalization (bypassing slow kernel calls like `Path.resolve()`).
* **Full-Vault Search (`VaultSearchDialog`):** SQLite **FTS5** virtual table indexing (`document_index`) using the **Porter unicode61** linguistic tokenizer (e.g. searching "genetics" matches "genetic").
* **UX Frictionless Dismissal:** Includes `QEvent.WindowDeactivate` event filters allowing users to dismiss popup search dialogs instantly by clicking anywhere outside the window.

### 4.3. Quick Switcher (`quick_switcher.py`) & Keyboard Ergonomics
* **Fuzzy Finder (`Ctrl+Q`):** VSCode-style overlay displaying recently opened files, pinned items, and active tabs with instant filtering.
* **Core Keyboard Shortcuts:**
  * `Ctrl+Q`: Summon Quick Switcher.
  * `Alt+V`: Toggle Vault Sidebar.
  * `Ctrl+T`: Open Web Browser Panel / New Tab.
  * `Ctrl+Shift+T`: Reopen last closed tab.
  * `Ctrl+Alt+T`: Toggle main toolbar (Distraction-Free Mode).

### 4.4. Built-in Web Browser Panel (`web_panel.py`)
* **Side-by-Side Research:** Allows students to browse course portals or research web pages directly alongside local notes.
* **Chromium Lazy-Loading:** `PySide6.QtWebEngineWidgets` is strictly lazy-loaded on first invocation of `Ctrl+T` or web navigation, preserving the <100ms cold start.
* **Full Page Zoom & Keyboard Shortcuts:** Dedicated zoom step handling (`Ctrl++`, `Ctrl+-`, `Ctrl+0`), mouse wheel zoom (`Ctrl+Scroll`), and interactive percentage badge in the browser header.
* **Native Downloads Manager:** Connects to QtWebEngine `downloadRequested` signal to route files directly to the user's configured downloads folder with dockable progress bars.
* **Rich Web Context Menu:** Custom menu providing link copy, back/forward navigation, tab opening, page zoom, and bookmarking.

### 4.5. Spotlight Interactive Tutorials (`tutorials.py`)
* **Visual Spotlight System:** Semitransparent darkened canvas with rounded cutout highlighting target UI elements.
* **Geometric Bounding Clamping:** Intelligent placement math detects wide targets (toolbar, tab bar) and positions instruction cards safely above/below while strictly clamping coordinates (`margin <= card_x <= win_w - card_w - margin`) to prevent off-screen positioning.
* **Interactive Navigation:** Supports `Esc` to exit, `Enter`/`Space`/Right-Arrow to advance, and Left-Arrow to navigate back. Accessible via **Help > Interactive Tutorials**.

### 4.6. Overhauled Settings & Preferences Hub (`settings_dialog.py`)
* **Six Categorized Tabs:**
  1. *Startup & Defaults:* Initial view mode, welcome dashboard toggle, session restore.
  2. *Text Editing:* Editor font family, size, line numbers, word wrapping.
  3. *PDF Reading:* Default zoom level, page layout mode (single/dual).
  4. *Web Browser Panel:* Custom downloads folder, default zoom factor.
  5. *Audio & Read Aloud:* Speech reading speed rate, default voice engine.
  6. *Folders & Organization:* Vault search recursion depth, file type filtering.
* **Toolbar Customization:** Preference for icons with text labels, compact icons only, or icons beside text.

### 4.7. Minimalist Welcome Dashboard & Accessibility (`welcome_widget.py`, `ui.py`)
* **Dashboard Action Cards:** Ergonomic cards for Open File, Add Vault, and Web Panel, styled with crisp Lucide icons and subtitle descriptions.
* **Live Vault Omnibar:** Instant vault searching with a 200ms debounce timer to prevent main thread typing latency.
* **Screen Reader Accessibility:** Comprehensive ARIA/AccessibleName and AccessibleDescription markup on Welcome cards, toolbar buttons, and preference tabs for Windows Narrator and NVDA.

### 4.8. Atomic State Management & Draft Recovery (`save_utils.py` & `draft_recovery.py`)
* Direct `json.dump()` and `open(..., "w")` calls for settings, session state, and bookmarks invoke `atomic_write()` with `os.fsync()` and `os.replace()`, preventing 0-byte corruptions.
* Background draft worker persists uncommitted text edits to `~/.eleviewer/drafts/` every 30 seconds.

### 4.9. Zero-PII Feedback Hub (`feedback_dialog.py` & Vercel Bridge)
* In-app bug and suggestion reporter with path scrubbing (`~` normalization) and automatic fallback to browser GitHub issue template if API is unreachable.

---

## 5. Visual Design System (Vercel Geist & Google Stitch Contract)

Both `eleviewer` (desktop) and `eleviewer-site` (web) adhere to a strict monochromatic design contract codified in `eleviewer-site/DESIGN.md` and `.agents/AGENTS.md`.

```
================================================================================
TOKEN / VARIABLE       DESKTOP (theme.py)      WEB (globals.css)    USAGE
================================================================================
BRAND_BACKGROUND       #131313                 --background (#1313) Main Canvas
BRAND_PANEL            #1c1c1c                 --panel (#1c1c1c)    Sidebar / Cards
BRAND_PANEL_2          #252526                 --panel-2 (#252526) Hover / Active
BRAND_ACCENT           #6cb6ff                 --accent (#6cb6ff)   Tab Top-Accent Line
BRAND_BORDER           #2a2a2a                 --border (#2a2a2a)   Hairline 1px Border
BRAND_PRIMARY          #f2f2f0                 --foreground (#f2f2) Primary Text / Ink
================================================================================
```

---

## 6. Build, OS Integration & Packaging Outcomes

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          PRODUCTION BUILD PIPELINE                          │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. Nuitka LTO Compiler:                                                     │
│    nuitka --standalone --lto=yes --include-qt-plugins=sensible,styles,      │
│           qwebengine main.py                                                │
├─────────────────────────────────────────────────────────────────────────────┤
│ 2. Azure Artifact Signing (Optional v0.5.0):                                │
│    Digitally signs EleViewer.exe to bypass Windows SmartScreen              │
├─────────────────────────────────────────────────────────────────────────────┤
│ 3. Inno Setup Per-User Installer (setup.iss):                               │
│    PrivilegesRequired=lowest -> Writes ProgIDs to HKCU\Software\Classes\    │
├─────────────────────────────────────────────────────────────────────────────┤
│ 4. Winget Releaser & Manifest Publishing:                                   │
│    Calculates dynamic SHA256, generates winget-installer.yaml, publishes    │
│    GitHub Release, and submits to Windows Package Manager (winget-pkgs)     │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6.1. Single Source of Truth Versioning
* App version is defined exclusively in `version.py` (`APP_VERSION = "1.4.0"`).
* Synchronized with `setup.iss` (`#define AppVersion "1.4.0"`), `version_sync.py`, and `winget/*.yaml`.

### 6.2. Registry & Shell Integration (`setup.iss`)
* Inno Setup script writes ProgIDs to `HKCU\Software\Classes\` (no admin rights needed on school lab machines).
* Configures Windows `AppUserModelID` (`EleViewer.Document.Reader`) for clean taskbar pinning and jump list recent files.

### 6.3. Windows Package Manager Distribution
* Official package manifests in `winget/karefined-eng.EleViewer*.yaml`.
* Installs cleanly with `winget install karefined-eng.EleViewer`.

---

## 7. Feature Improvement & Audit Tracker

| Feature / Target | Status | Implementation Detail / File Path |
| :--- | :--- | :--- |
| **Interactive Spotlight Tutorials** | ✅ Completed | Spotlight overlay with coordinate bounding safety (`tutorials.py`). |
| **Web Panel Page Zoom & Downloads** | ✅ Completed | Zoom hotkeys, percentage badge, and native downloads (`web_panel.py`). |
| **Web View Context Menu & Tooltips** | ✅ Completed | Right-click action menu and tab header hover tooltips (`web_panel.py`). |
| **Settings Dialog Overhaul** | ✅ Completed | 6 dedicated tabs for downloads, zoom, fonts, layout (`settings_dialog.py`). |
| **Welcome Dashboard Action Cards** | ✅ Completed | Refined card buttons with crisp icon rendering (`ui.py`, `icons.py`). |
| **Distraction-Free Mode** | ✅ Completed | `Ctrl+Alt+T` toolbar visibility toggle (`ui.py`). |
| **Screen Reader Accessibility** | ✅ Completed | ARIA/AccessibleName roles across Welcome cards & toolbar (`ui.py`). |
| **Debounced Vault Omnibar** | ✅ Completed | 200ms debounce timer on live vault search (`ui.py`, `welcome_widget.py`). |
| **Smooth Splash Transition** | ✅ Completed | Opacity fade on startup eliminating window flash (`main.py`, `ui.py`). |
| **Type-Specific Bookmarks** | ✅ Completed | Distinct globe vs document Lucide icons (`bookmark_panel.py`). |
| **Winget Manifests & CI/CD** | ✅ Completed | Automated tag-based builds & Winget submission (`.github/workflows/build.yml`). |
| **Status Bar Geometry** | ✅ Completed | Status bar right-aligned format & UTF-8 labels (`ui.py`). |
| **Universal TTS Across All Formats** | ✅ Completed | Floating TTS bar with page counters & play controls (`tts_engine.py`). |
| **Atomic File Persistence** | ✅ Completed | `atomic_write()` with `os.fsync()` across settings, session, recent files (`save_utils.py`). |
| **Zero-PII Bug Reporting** | ✅ Completed | Path sanitization + Vercel GitHub Issue bridge (`feedback_dialog.py`). |

---

> **Conclusion:** EleViewer v1.4.0 delivers a cohesive, fast, and offline-first study workstation. With interactive spotlight tutorials, integrated web research capabilities, distraction-free reading, and comprehensive accessibility, it equips students and researchers with an uncompromising local desktop tool.
