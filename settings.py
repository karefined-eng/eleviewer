import json
import os

from paths import SETTINGS_FILE_PATH
from theme import ICON_SIZE_MARKDOWN

DEFAULT_WEB_TABS = [
    {"title": "EleViewer", "url": "https://eleviewer.vercel.app"},
    {"title": "Google", "url": "https://www.google.com"}
]

DEFAULT_SETTINGS = {
    "autosave_enabled": True,
    "autosave_interval_seconds": 5,
    "web_url": "https://www.google.com",
    "web_tabs": DEFAULT_WEB_TABS.copy(),
    "vault_path": "",
    "vault_paths": [],
    "active_vault_index": 0,
    "vault_show_all_files": False,
    "markdown_default_mode": "view",
    "markdown_icon_size": ICON_SIZE_MARKDOWN,
    "pdf_fit_mode": "width",
    "pdf_render_quality": "high",
    "launch_behavior": "remembered",
    "window_geometry": None,
    "draft_autosave_enabled": True,
    "draft_autosave_interval_seconds": 60,
    "theme_accent": "blue",
    "tts_voice_id": None,
    "tts_read_mode": "page",
    "onboarding_completed": False,
    "file_search_scope": "active_vault",
}


def _migrate_settings(data):
    """Migrate legacy single-vault and web_url settings."""
    if "vault_paths" not in data or not data["vault_paths"]:
        legacy = data.get("vault_path", "")
        if legacy and os.path.isdir(legacy):
            data["vault_paths"] = [legacy]
        else:
            data["vault_paths"] = []
    if "web_tabs" not in data or not data["web_tabs"]:
        url = data.get("web_url", DEFAULT_SETTINGS["web_url"])
        data["web_tabs"] = [{"title": "Web", "url": url}]
    return data


def load_settings():
    if not SETTINGS_FILE_PATH.exists():
        return DEFAULT_SETTINGS.copy()
    try:
        with open(SETTINGS_FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        data = _migrate_settings(data)
        merged = DEFAULT_SETTINGS.copy()
        merged.update(data)
        return merged
    except Exception:
        return DEFAULT_SETTINGS.copy()


def save_settings(settings):
    with open(SETTINGS_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4)


def get_vault_paths():
    settings = load_settings()
    paths = settings.get("vault_paths", [])
    return [p for p in paths if p and os.path.isdir(p)]


def add_vault_path(path):
    settings = load_settings()
    paths = settings.get("vault_paths", [])
    if path in paths:
        paths.remove(path)
    paths.insert(0, path)
    settings["vault_paths"] = paths
    settings["active_vault_index"] = 0
    settings["vault_path"] = path
    save_settings(settings)


def remove_vault_path(path):
    settings = load_settings()
    paths = settings.get("vault_paths", [])
    if path in paths:
        paths.remove(path)
    settings["vault_paths"] = paths
    if paths:
        settings["active_vault_index"] = min(settings.get("active_vault_index", 0), len(paths) - 1)
        settings["vault_path"] = paths[settings["active_vault_index"]]
    else:
        settings["active_vault_index"] = 0
        settings["vault_path"] = ""
    save_settings(settings)


def set_active_vault_index(index):
    settings = load_settings()
    paths = settings.get("vault_paths", [])
    if 0 <= index < len(paths):
        settings["active_vault_index"] = index
        settings["vault_path"] = paths[index]
        save_settings(settings)
