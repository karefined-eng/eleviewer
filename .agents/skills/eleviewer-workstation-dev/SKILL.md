---
name: eleviewer-workstation-dev
description: Develops, debugs, and refactors Python PySide6 modules for the EleViewer desktop application (`eleviewer`). Use this skill whenever working on desktop UI widgets, QThread concurrency, atomic file saves, zero-telemetry PII stripping, or universal TTS reading tools.
---

# EleViewer Sovereignty Workstation Development Skill (`eleviewer`)

When invoked to work on the Python PySide6 desktop application, adhere to these architectural and concurrency rules to maintain lightweight execution speed (~220MB standalone `.exe`), privacy sovereignty, and distraction-free study workflows.

## 1. Zero Telemetry & Data Sovereignty
- **Absolute Privacy:** Never add analytics, tracking scripts, or external telemetry pings.
- **PII Stripping:** When logging crash reports or handling feedback submissions in `feedback_dialog.py` / `main.py`, actively sanitize out user Personally Identifiable Information (PII). Specifically, replace Windows home directory paths (`os.path.expanduser("~")` or `C:\Users\<username>`) with `~` before copying to clipboard or network transmission.

## 2. UI Theming & Token Consistency (`theme.py`)
- Do not hardcode hex colors (e.g., `#1c1c1c`, `#6cb6ff`) in PySide6 UI modules (`ui.py`, `pdf_viewer.py`, `xlsx_viewer.py`, `vault_explorer.py`).
- Always import and reuse centralized theme constants defined in `theme.py`, which mirror the website's CSS variables:
  ```python
  from theme import BRAND_PRIMARY, BRAND_PANEL, BRAND_PANEL_2, BRAND_ACCENT, BRAND_BORDER, BRAND_BACKGROUND
  ```

## 3. Off-Thread Concurrency (`QThread`)
- To guarantee zero GUI freezing during heavy operations, all network requests, file indexing, and auto-save tasks MUST be executed on background `QThread` workers:
  - `FeedbackSubmitThread` / `FeedbackSubmitWorker` for GitHub issue submission.
  - `DraftWorker` for background autosaving.
  - `VaultSearchWorker` for local file indexing and vault searching.

## 4. The 4 Reflex Keys & Universal TTS (`F9`)
- Preserve seamless global shortcut operation for the 4 Reflex keys:
  - `Ctrl+Q`: Quit application / Lock workspace.
  - `Alt+V`: Toggle Vault sidebar drawer.
  - `Ctrl+T`: Open new workspace tab / web viewer.
  - `Ctrl+Shift+T`: Restore recently closed tab.
- Maintain Universal Text-to-Speech (`F9`), ensuring it can read aloud highlighted or full-page text across all document readers (`pdf_viewer.py`, `docx_viewer.py`, `pptx_viewer.py`, `xlsx_viewer.py`, `editor.py`, and `txt_viewer.py`).

## 5. Atomic File Operations (`atomic_write`)
- All user settings (`settings.json`), session state, and document drafts MUST be saved using atomic write patterns (`atomic_write` temp file renaming) to prevent 0-byte file corruption during unexpected Windows power cuts or system shutdowns.

## 6. Installer Creation & Copywriting Standards (`setup.iss`)
- **Flesch-Kincaid & Paul Graham Copywriting:** When creating or modifying installer scripts (`setup.iss`), PyInstaller specs (`EleViewer.spec`), or Winget manifests, never use dry corporate/technical boilerplate. All wizard messages, task descriptions, and option labels must speak in conversational, middle-grader accessible English (e.g., *"Open my study files with EleViewer by default"* instead of *"Register default file associations"*).
- **Distraction-Free Wizard Design:** Ensure custom installer messages (`WelcomeLabel2`, `FinishedLabelNoIcons`) emphasize our core student promise: offline privacy, zero telemetry, local storage, and lightweight speed.

