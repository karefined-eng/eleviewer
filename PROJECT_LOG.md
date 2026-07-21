# 📖 The Grandmaster's Ledger (Project & Context Log)

> **⚠️ DIRECTIVE FOR ALL AI AGENTS ⚠️**
> **READ THIS FIRST**: Before executing *any* task, read this document to inherit the deep context, architectural decisions, and pain points of this workspace. 
> **WRITE THIS LAST**: Upon completing a major task, append your changes, insights, and new pain points to the **Historical Ledger** section below. Do not overwrite history; append to it. 
> *Treat this as a sacred developer-to-developer diary.*

## 🗺️ Workspace Topology

The ecosystem consists of two parallel repositories:

### 1. `eleviewer` (Core Application)
- **Path**: `c:\Users\kwadw\Documents\eleviewer`
- **Tech Stack**: Python 3.9+, PySide6
- **Purpose**: A lightweight, multi-tabbed Windows document editor (DOCX, XLSX, MD, CSV, HTML, TXT, PDF).
- **Key Modules**:
  - `main.py` & `ui.py`: Entry point and UI scaffolding (tabs, menus).
  - `file_handler.py`: Factory pattern router for different file types.
  - `pdf_viewer.py`, `docx_viewer.py`, `xlsx_viewer.py`, `editor.py` (Text/MD): Core viewers.
  - `vault_explorer.py`, `web_panel.py`, `bookmark_panel.py`: Sidebar panels.
  - `instance_lock.py`: Manages single-instance enforcement via local sockets.
- **Dependencies (`requirements.txt`)**: `PySide6`, `python-docx`, `openpyxl`, `markdown`, `pyttsx3`. 
  - *Note*: WebEngine is used (`PySide6-WebEngine`). PyMuPDF (`fitz`) was completely removed in v1.2.0 in favor of native QtPdf.

### 2. `eleviewer-site` (Marketing Website)
- **Path**: `c:\Users\kwadw\Documents\eleviewer-site`
- **Tech Stack**: Next.js (App Router), React, Tailwind CSS, Vercel
- **Purpose**: Landing page and distribution hub.
- **Key Modules**:
  - `app/layout.tsx`: Houses robust SEO tags, OpenGraph, and JSON-LD schemas.
  - `lib/links.ts`: Centralized URLs (including the direct `.exe` download URL).
  - `components/*`: UI blocks (hero, features, faq).

## 🧠 Agent Insights & Optimizations

*Context traps and credit-draining pitfalls to avoid.*

1. **The PyInstaller Build Trap**:
   - **Pain Point**: Building the executable is slow and produces a massive file (~222MB) because of `PySide6-WebEngine`.
   - **Optimization**: Do not initiate a build (`pyinstaller EleViewer.spec`) lightly. Only build when explicitly instructed or finalizing a release. `UPX` compression is disabled in the `.spec` file because it causes decompression errors on some Windows machines.
2. **The PDF Viewer Legacy Trap**:
   - **Pain Point**: Older documentation or comments might mention `fitz` or PyMuPDF. 
   - **Optimization**: We migrated to `QPdfView` (native Qt). Do not attempt to import `fitz` or PyMuPDF. 
3. **The PowerShell `&&` Trap**:
   - **Pain Point**: Using `&&` in Windows PowerShell via the `run_command` tool throws syntax errors.
   - **Optimization**: Always use `;` to chain commands in PowerShell.
4. **Website SEO Context**:
   - **Optimization**: The website uses direct asset download links (e.g., `.../releases/latest/download/EleViewer.exe`). If you change the executable name or release strategy, update `lib/links.ts` immediately.

## 📜 Historical Ledger (Task Log)

### [2026-07-21] Release v1.2.0 & SEO Overhaul
**Goal**: Publish v1.2.0 release and optimize web presence.
**Changes Made**:
- **eleviewer**:
  - Bumped `APP_VERSION = "1.2.0"` in `main.py` and `ui.py`.
  - Audited `README.md`: Added single-instance locking docs, cleaned up stale `fitz` references, added architecture map.
  - Deleted duplicate `gitignore` file (retained `.gitignore`).
  - Authored release notes and used `gh` CLI to publish `EleViewer.exe` (222MB) to GitHub.
  - Updated GitHub repo topics (14 tags) and description via API.
- **eleviewer-site**:
  - Corrected file size claim ("16 MB" -> "Single-file, portable").
  - Updated `lib/links.ts` to route downloads directly to the `latest/download/EleViewer.exe` GitHub asset.
  - Massive SEO optimization in `app/layout.tsx` (Keywords, Robots, Authors) and `structured-data.tsx` (SoftwareApplication schema, FAQ schema).
  - Updated GitHub repo topics and description.
**Agent Notes**: The release pipeline relies heavily on the `gh` CLI. Ensure you are authenticated (`gh auth status`) before attempting to manage releases. When checking GitHub repo metadata via `gh`, ensure `$env:GITHUB_TOKEN` is cleared if it contains an invalid token, allowing fallback to keyring authentication.
