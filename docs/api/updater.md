# API Reference: updater.py

## Auto-Update System

EleViewer checks for updates on GitHub (`karefined-eng/eleviewer` releases) and downloads verified installer assets with SHA-256 hash verification.

### Classes

#### `CheckUpdateThread(QThread)`

Background thread that queries the GitHub API for the latest release and compares versions.

**Constructor:**
```python
CheckUpdateThread(current_version=CURRENT_VERSION, parent=None)
```

**Signals:**
| Signal | Payload | Description |
|--------|---------|-------------|
| `update_available` | (tag_name, release_notes, download_url, expected_hash) | A newer version is available |
| `no_update` | — | Running the latest version |
| `error_occurred` | (error_message) | Update check failed |

**Security:** Only downloads from trusted hosts (github.com, objects.githubusercontent.com, release-assets.githubusercontent.com). Requires SHA-256 hash verification before installing.

#### `DownloadThread(QThread)`

Background thread that downloads the update installer to a temp file and verifies its hash.

**Constructor:**
```python
DownloadThread(download_url, expected_hash, parent=None)
```

**Signals:**
| Signal | Payload | Description |
|--------|---------|-------------|
| `progress` | (percent) | Download progress (0-100) |
| `finished` | (exe_path) | Download completed and hash verified |
| `failed` | (error_message) | Download or hash verification failed |

#### `UpdateDialog(QDialog)`

Modal dialog shown when an update is available. Displays release notes, download progress, and action buttons.

**Constructor:**
```python
UpdateDialog(tag_name, release_notes, download_url, expected_hash, parent=None)
```

**Buttons:**
| Button | Action |
|--------|--------|
| "Update Now" | Download and launch the installer |
| "Skip this version" | Persist the version in `skipped_update_versions` and dismiss |
| "Remind Me Later" | Dismiss without skipping |

### Integration in ui.py

- `_check_for_updates_async()` — Auto-check on app launch
- `check_for_updates_manual()` — Manual check via menu/toolbar
- `_on_update_found(tag_name, ...)` — Shows `UpdateDialog`, unless version is in `skipped_update_versions`
