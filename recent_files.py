import json
import os
from pathlib import Path


# Use a safe user-writable location (NOT project folder)
APP_DATA_DIR = Path(os.getenv("APPDATA", Path.home())) / "EleViewer"
APP_DATA_DIR.mkdir(parents=True, exist_ok=True)

RECENT_FILE_PATH = APP_DATA_DIR / "recent_files.json"


def load_recent_files(validate=True):
    """
    Load list of recent file paths.
    
    Args:
        validate: If True, only return files that still exist on disk.
    """
    if not RECENT_FILE_PATH.exists():
        return []

    try:
        with open(RECENT_FILE_PATH, "r", encoding="utf-8") as file:
            files = json.load(file)
        
        # Validate files still exist
        if validate:
            original_count = len(files)
            files = [f for f in files if os.path.exists(f)]
            # Update file if it changed
            if len(files) != original_count:
                save_recent_files(files)
        
        return files

    except Exception:
        return []


def save_recent_files(files):
    """Save the entire recent files list (internal helper)."""
    with open(RECENT_FILE_PATH, "w", encoding="utf-8") as file:
        json.dump(files, file, indent=4)


def save_recent_file(path):
    """
    Add or move a file to the top of recent list.
    Keeps max 10 recent files.
    """
    files = load_recent_files(validate=False)

    if path in files:
        files.remove(path)

    files.insert(0, path)

    files = files[:10]

    with open(RECENT_FILE_PATH, "w", encoding="utf-8") as file:
        json.dump(files, file, indent=4)


def remove_recent_file(path):
    """Remove a file from recent list."""
    files = load_recent_files(validate=False)
    
    if path in files:
        files.remove(path)
    
    with open(RECENT_FILE_PATH, "w", encoding="utf-8") as file:
        json.dump(files, file, indent=4)