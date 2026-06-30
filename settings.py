import json
from paths import SETTINGS_FILE_PATH

DEFAULT_SETTINGS = {
    "autosave_enabled": True,
    "autosave_interval_seconds": 5,
    "web_url": "https://sakai.ug.edu.gh",
}


def load_settings():
    if not SETTINGS_FILE_PATH.exists():
        return DEFAULT_SETTINGS.copy()
    try:
        with open(SETTINGS_FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        merged = DEFAULT_SETTINGS.copy()
        merged.update(data)
        return merged
    except Exception:
        return DEFAULT_SETTINGS.copy()


def save_settings(settings):
    with open(SETTINGS_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4)
