# API Reference: settings.py

## Settings Management

EleViewer stores user preferences in a JSON file at `SETTINGS_FILE_PATH` (defined in `paths.py`). All reads/writes use atomic writes (`tempfile.mkstemp` + `os.fsync` + `os.replace`) to prevent 0-byte corruption on crash.

### Functions

| Function | Description |
|----------|-------------|
| `load_settings()` | Load settings from disk, merge with defaults, run migrations |
| `save_settings(settings)` | Atomically write settings to disk as JSON |
| `get_vault_paths()` | Return list of valid vault directory paths |
| `add_vault_path(path)` | Add a vault path (moves to front of list) |
| `remove_vault_path(path)` | Remove a vault path |
| `set_active_vault_index(index)` | Set the active vault by index |

### DEFAULT_SETTINGS Keys

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `autosave_enabled` | bool | True | Auto-save modified documents periodically |
| `autosave_interval_seconds` | int | 5 | Auto-save interval in seconds |
| `pdf_fit_mode` | str | "width" | Default PDF zoom: "page" or "width" |
| `pdf_toc_visible` | bool | False | Whether PDF TOC sidebar is visible by default |
| `pdf_default_zoom` | str | "Fit to Width" | Default PDF zoom mode |
| `pdf_continuous_scroll` | bool | True | Continuous scrolling for PDFs |
| `theme_mode` | str | "dark" | UI theme: "dark" or "light" |
| `theme_accent` | str | "grey" | Accent color theme |
| `toolbar_button_style` | str | "text_under_icon" | Toolbar button display style |
| `show_toolbar` | bool | True | Show/hide main toolbar |
| `toolbar_order` | list[str] | [...ordered list] | Order of toolbar action IDs |
| `vault_paths` | list[str] | [] | Linked vault folder paths |
| `vault_show_all_files` | bool | False | Show hidden/system files in vault |
| `editor_font_size` | int | 14 | Default editor font size |
| `editor_font_family` | str | "Segoe UI" | Default editor font |
| `editor_word_wrap` | bool | True | Enable word wrap in editor |
| `editor_line_numbers` | bool | True | Show line numbers in editor |
| `tts_engine` | str | "neural" | TTS engine preference |
| `tts_speed` | str | "1.0x" | TTS playback speed |
| `skipped_update_versions` | list[str] | [] | Update versions the user has skipped |
| `onboarding_completed` | bool | False | Whether first-run onboarding is done |
| `restore_session` | bool | True | Restore previous session on startup |
