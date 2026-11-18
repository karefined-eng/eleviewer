# Feature Guide: Auto-Update "Skip This Version"

## Overview

When a new version of EleViewer is available, the update dialog now includes a **"Skip this version"** button. Clicking it persists the version number so you won't be prompted about that specific release again.

## How It Works

1. An update check finds a newer version
2. The UpdateDialog shows release notes and action buttons
3. Click **"Skip this version"** to dismiss without installing
4. The version tag (e.g., `v1.3.8`) is saved to `skipped_update_versions` in settings
5. Future update checks will skip that version until a newer one is released

## Where It's Stored

Skipped versions are stored in `settings.json` under the `skipped_update_versions` key:

```json
{
  "skipped_update_versions": ["v1.3.8", "v1.3.9"]
}
```

## Manual Reset

To re-enable notifications for a skipped version, remove it from `skipped_update_versions` in your settings file, or wait for a newer release (the skip only applies to the specific version tag).

## Integration

- Auto-check on app launch respects skipped versions
- Manual check (`Check for Updates` in menu/status bar) also respects skipped versions
- The `CheckUpdateThread` emits `update_available` only for non-skipped versions
