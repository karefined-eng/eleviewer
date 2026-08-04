import json
from paths import SESSION_FILE_PATH
from save_utils import atomic_write


# IMPROVEMENT: persist scroll position and PDF zoom across sessions
def save_session(tabs_info, bookmarks_panel_visible=False, web_url=None):
    """
    Save current session (open tabs) to disk.

    tabs_info: list of dicts with file_path, content, is_active, is_modified, scroll_y, zoom, pdf_page
    """
    try:
        session_data = {
            "tabs": tabs_info,
            "version": 2,
            "bookmarks_panel_visible": bookmarks_panel_visible,
            "web_url": web_url,
        }
        # FIX: atomic write prevents 0-byte corruption on crash
        atomic_write(SESSION_FILE_PATH, json.dumps(session_data, indent=4))
    except Exception as e:
        print(f"Failed to save session: {e}")


def load_session():
    if not SESSION_FILE_PATH.exists():
        return {"tabs": [], "bookmarks_panel_visible": False, "web_url": None}
    try:
        with open(SESSION_FILE_PATH, "r", encoding="utf-8") as f:
            session_data = json.load(f)
        return {
            "tabs": session_data.get("tabs", []),
            "bookmarks_panel_visible": session_data.get("bookmarks_panel_visible", False),
            "web_url": session_data.get("web_url"),
        }
    except Exception as e:
        print(f"Failed to load session: {e}")
        return {"tabs": [], "bookmarks_panel_visible": False, "web_url": None}


def clear_session():
    try:
        if SESSION_FILE_PATH.exists():
            SESSION_FILE_PATH.unlink()
    except Exception as e:
        print(f"Failed to clear session: {e}")
