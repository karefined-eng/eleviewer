import json

from paths import SESSION_FILE_PATH


def save_session(tabs_info):
    """
    Save current session (open tabs) to disk.

    tabs_info: list of dicts with file_path, content (text-only tabs), is_active, is_modified
    """
    try:
        session_data = {"tabs": tabs_info, "version": 2}
        with open(SESSION_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(session_data, f, indent=4)
    except Exception as e:
        print(f"Failed to save session: {e}")


def load_session():
    if not SESSION_FILE_PATH.exists():
        return []
    try:
        with open(SESSION_FILE_PATH, "r", encoding="utf-8") as f:
            session_data = json.load(f)
        return session_data.get("tabs", [])
    except Exception as e:
        print(f"Failed to load session: {e}")
        return []


def clear_session():
    try:
        if SESSION_FILE_PATH.exists():
            SESSION_FILE_PATH.unlink()
    except Exception as e:
        print(f"Failed to clear session: {e}")
