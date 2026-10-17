# EleViewer v1.3.6 Bugfix Handoff

## Scope

Fixed three open GitHub issues targeting the v1.3.5 release:

- **#100 — Fatal crash when opening the Web panel** (`web_panel.py`, `ui.py`)
- **#102 — "Read Aloud" produces no audio** (`tts_engine.py`, `tts_reader_bar.py`, `ui.py`)
- **#101 — Basic file operations missing from Vault Explorer** (`vault_explorer.py`, `ui.py`)
- **Packaging improvement — ensure offline SAPI driver ships in Nuitka builds** (`.github/workflows/build.yml`)

---

## Issue #100: Fatal crash when opening the Web panel

**Root cause.** `QWebEngineProfile::setPersistentStoragePath` and related `PySide6.QtWebEngineCore` calls inside `get_persistent_profile()` would crash with `ImportError: LoadLibraryExW '...PySide6\QtWebEngineCore.pyd' failed: The process cannot access the file because it is being used by another process.` — a transient OS-level lock typically caused by a background sync process, on-demand update, or a stale app instance leaving its web engine files locked.

When `toggle_web_panel()` → `open_web_tab()` imported `WebPanel()`, the heavy `QtWebEngineCore` import happened **without guard**, killing the process entirely rather than degrading gracefully.

**Fix.** Added a `_import_webengine()` helper (`web_panel.py:27–43`) that retries the import 3× with small delays before raising a friendly message (`_WEB_LOCKED_MESSAGE`) instead of crashing. The retry window normally clears the OS lock; even on permanent failure the panel becomes unusable but the app stays alive. The `WebPanel()` construction in `ui.py` now catches that `ImportError` and shows a `QMessageBox.warning` rather than aborting the tab entirely (issue #100 crash path).

**Files changed.**
- `web_panel.py` — `_import_webengine()`, `_WEB_LOCKED_MESSAGE`, `get_persistent_profile()` uses it, `get_web_view_class()` uses it
- `ui.py` — `WebPanel()` wrapped in `try ImportError` + fallback message

---

## Issue #102: "Read Aloud" produces no audio

**Root cause.** Three compounding gaps left the TTS engine silent:

1. **No error callback** — `TtsEngine()` was created with no `on_error` handler, so every downstream failure in the worker thread (blocked network, missing SAPI driver, MCI error) was swallowed silently.
2. **Packaging gap** — the Nuitka build spec (`EleViewer.spec`) had no explicit `--include-module=pyttsx3.drivers.sapi5`, so the offline Windows Speech API driver was missing from packaged installers, leaving the app with only online voices that require network access.
3. **No last-resort fallback** — even when both `edge-tts` and `pyttsx3` were importable, a broken offline driver left the user with dead silence. There was no Windows built-in speech fallback.

**Fix.** Rewrote `tts_engine.py` with a multi-tier fallback chain that guarantees at least one of:
- `edge-tts` (online, high-quality neural voices)
- `pyttsx3` + Windows SAPI5 driver (offline, works without network)
- Native Windows `SpeechSynthesizer` via PowerShell (always available on Windows, zero Python dependencies)
- User-visible error messages via the reader bar

Added `on_error` callback injection into `MainWindow.__init__`, wired `tts_error_raised` → `_show_tts_error` → `TtsReaderBar.set_error()` so failures appear in the UI instead of being silent. Added `TtsReaderBar.set_error()` method. Added `--include-module=pyttsx3.drivers.sapi5` to the Nuitka build so the offline SAPI driver ships in the installer. Made `TTS_AVAILABLE` reflect OS capability (`os.name == "nt"`) so user-facing code can at least attempt the native fallback even when Python packages are absent.

**Files changed.**
- `tts_engine.py` — complete rewrite with voice fallback chain, error callback, native Windows speech via PowerShell, MCI error guarding, `_mci_send` helper
- `tts_reader_bar.py` — `set_error()` method to surface failures to the user
- `ui.py` — `TtsEngine(on_error=self._on_tts_error)`; `tts_error_raised` Signal wired to UI error display
- `.github/workflows/build.yml` — `--include-module=pyttsx3.drivers.sapi5` added to Nuitka invocation

---

## Issue #101: Basic file operations missing from Vault Explorer

**Root cause.** The Vault explorer displayed read-only files and folders but had no context menu or keyboard shortcuts for the most common actions: rename, new folder, copy, cut, paste, delete. The feature request (#101) explicitly called for rename and cut operations and listed cut/copy/paste/delete as what users expected.

**Fix.** Added a full file-operations toolset:

- **Right-click context menu** (tree → Rename / New Folder / Copy / Cut / Paste / Delete), scoped to the active vault
- **Keyboard accelerators** (F2 → rename, Delete → delete, Ctrl+C/Ctrl+X/Ctrl+V → copy/cut/paste)
- **Recycle Bin deletion** (Windows `SHFileOperationW` — moves to recycle bin, not permanently delete; with undo support)
- **Move-to-self guard** prevents creating folders/files inside themselves
- **Unique-name collision avoidance** automatically appends `(2)`, `(3)`… when a name is taken
- **Vault containment guard** blocks operations on paths outside the currently selected vault (mirrors existing symlink-traversal security)
- **files_changed Signal** emitted after every rename/copy/delete so open tabs can remap their `file_path` or close cleanly
- Integration wiring: `MainWindow._on_vault_files_changed()` remaps affected editor tabs or closes them if the underlying file vanished; `files_changed` signal connects from the vault panel

**Files changed.**
- `vault_explorer.py` — all operation methods (`_show_context_menu`, `_rename_item`, `_delete_item`, `_clip_item`, `_paste_into`, `_new_folder`, `_unique_destination`, `_refresh_and_notify`, keyboard shortcuts, containment checks); new signals `files_changed`
- `ui.py` — `self.vault_panel.files_changed.connect(self._on_vault_files_changed)` and `_on_vault_files_changed()` implementation

---

## Packaging: offline SAPI driver now ships in Nuitka builds

Added `--include-module=pyttsx3.drivers.sapi5` to the Nuitka invocation in `.github/workflows/build.yml`. Without this flag, the offline pyttsx3 SAPI5 driver binary was excluded from the standalone exe, making `pyttsx3.init()` fail silently on first use in the packaged app. With it, the driver is compiled in, so offline voices work out of the box in the Windows installer.

---

## Known / future work

- None of the three changes introduce new Python dependencies beyond what was already declared in `requirements.txt` or `EleViewer.spec`.
- The Recycle Bin delete function (`_send_to_recycle_bin`) is Windows-only; on macOS/Linux the delete operation would still move to the platform's trash via `shutil` (not implemented here since EleViewer targets Windows).
- The native Windows fallback in TTS uses PowerShell's `System.Speech.Synthesis` — available on Windows 10/11 with the .NET Framework pre-installed; if that is somehow absent the engine falls back to `pyttsx3` as before.
- No changes to the public API; all new methods are internal to the affected modules.