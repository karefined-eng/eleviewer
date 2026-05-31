import json
import os
from pathlib import Path


# Use safe user-writable location
APP_DATA_DIR = Path(os.getenv("APPDATA", Path.home())) / "EleViewer"
APP_DATA_DIR.mkdir(parents=True, exist_ok=True)

SESSION_FILE_PATH = APP_DATA_DIR / "session.json"


def save_session(tabs_info):
    """
    Save current session (open tabs) to disk.
    
    Args:
        tabs_info: List of dicts with keys:
            - file_path: str or None (None for untitled)
            - content: str (for unsaved files)
            - is_active: bool (which tab is currently active)
    """
    try:
        session_data = {
            "tabs": tabs_info,
            "version": 1
        }
        
        with open(SESSION_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(session_data, f, indent=4)
    
    except Exception as e:
        print(f"Failed to save session: {e}")


def load_session():
    """
    Load previous session from disk.
    
    Returns:
        List of tab info dicts, or empty list if no session exists.
    """
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
    """Clear saved session (called when app closes normally)."""
    try:
        if SESSION_FILE_PATH.exists():
            SESSION_FILE_PATH.unlink()
    except Exception as e:
        print(f"Failed to clear session: {e}")