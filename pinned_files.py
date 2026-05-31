import json
import os
from pathlib import Path


# Use safe user-writable location
APP_DATA_DIR = Path(os.getenv("APPDATA", Path.home())) / "EleViewer"
APP_DATA_DIR.mkdir(parents=True, exist_ok=True)

PINNED_FILE_PATH = APP_DATA_DIR / "pinned_files.json"


def load_pinned_files():
    """Load list of pinned file paths."""
    if not PINNED_FILE_PATH.exists():
        return []
    
    try:
        with open(PINNED_FILE_PATH, "r", encoding="utf-8") as file:
            return json.load(file)
    
    except Exception:
        return []


def save_pinned_file(path):
    """
    Add or move a file to the top of pinned list.
    Keeps max 10 pinned files.
    """
    files = load_pinned_files()
    
    # Remove if already exists
    if path in files:
        files.remove(path)
    
    # Add to top
    files.insert(0, path)
    
    # Keep only 10
    files = files[:10]
    
    with open(PINNED_FILE_PATH, "w", encoding="utf-8") as file:
        json.dump(files, file, indent=4)


def remove_pinned_file(path):
    """Remove a file from pinned list."""
    files = load_pinned_files()
    
    if path in files:
        files.remove(path)
    
    with open(PINNED_FILE_PATH, "w", encoding="utf-8") as file:
        json.dump(files, file, indent=4)


def is_pinned(path):
    """Check if a file is pinned."""
    return path in load_pinned_files()