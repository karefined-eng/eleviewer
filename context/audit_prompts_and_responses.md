# 📋 Audit Prompts and Responses Log (Ingested Context)

This file contains the complete audit prompts, deep-tech verification requirements, and QA findings ingested into the project context directory.

---

## 1. Core Architecture & UI Verification Audit
- **Active Tab Orientation**: QSS implementation of top-accent line (`BRAND_ACCENT`) on selected tabs (`border-top: 2px solid`).
- **Status Bar Geometry**: Far-right positioning for encoding (`UTF-8`) and format indicators to prevent left-aligned tooltip collision.
- **Modal Settings & Focus**: `Qt.ApplicationModal` focus handling and window lifecycle (`WA_DeleteOnClose`).
- **Global Dismissal Logic**: Escape key mapping for widget hiding without main loop termination.

---

## 2. Data Safety & Persistence Protocols Audit
- **Draft Recovery Engine**: Background `QThread` / `QTimer` serialization of text buffers to `~/.eleviewer/drafts/` with `os.replace()` atomic operations.
- **Atomic State Management**: Upgrading `save_settings()` and `save_session()` to use `atomic_write()` (`.tmp` write + `os.replace()`) to prevent 0-byte file truncation during crashes.
- **Concurrency & Encoding**: File locking for multi-instance vault access and `errors='replace'` UTF-8 fallback.
- **Frictionless Feedback Loop**: In-app Vercel serverless bug submission.

---

## 3. Functional, Specialized Deep-Tech & Reliability Audit
- **Universal TTS Integration**: `F9` shortcut with fallback support for SAPI5 (Windows), `NSSpeechSynthesizer` (macOS), `espeak` (Linux), and ONNX Kokoro/Piper neural voice preparation.
- **Vault Search Performance**: FTS5 SQLite indexing and 300ms debouncing for large vaults.
- **Path Traversal Security**: Strict `Path.resolve()` canonicalization preventing directory traversal attacks via symlinks or `../`.
- **DOCX/XLSX XML Safety**: Preserving original XML schemas, tables, and formatting when editing `.docx` and `.xlsx` files.
- **sys.excepthook Logging**: Overriding `sys.excepthook` in `main.py` to write unhandled exceptions in background threads or UI logic to `~/.eleviewer/logs/app.log`.
- **Non-Blocking Network Calls**: Threaded update checking (`CheckUpdateThread`) with strict network timeouts.
- **Dynamic Theme Repainting**: Instant QSS theme propagation across all child widgets without requiring restart.
- **Binary Dependency Trimming**: Excluding unused Qt modules (`PySide6.QtWebEngineCore` when using native previewers) to optimize binary footprint.

---

## 4. Build, Packaging & OS Integration Audit
- **Nuitka Compilation**: Transitioning from PyInstaller `onefile` to Nuitka for startup speed optimization and AV false-positive reduction.
- **Code Signing & Integrity**: Azure Trusted Signing workflow and local SHA-256 binary hash generation.
- **Registry & Shell Integration**: `setup.iss` Inno Setup script registering `HKCR` associations for `.pdf`, `.md`, `.docx`, `.xlsx` and right-click `"Open with EleViewer"`.
- **Winget Manifests**: `winget/` directory containing CLI installation manifests (`karefined-eng.EleViewer.yaml`).
- **Abednego Starter Vault**: First-year student onboarding bundle (`getting_started/START_HERE.html`).
- **Virtual Highlights Parser**: Sidecar `.ele` JSON highlight parser overlaying non-destructive highlights onto document views.
