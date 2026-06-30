import os
from pathlib import Path

APP_DATA_DIR = Path(os.getenv("APPDATA", Path.home())) / "EleViewer"
APP_DATA_DIR.mkdir(parents=True, exist_ok=True)

RECENT_FILE_PATH = APP_DATA_DIR / "recent_files.json"
PINNED_FILE_PATH = APP_DATA_DIR / "pinned_files.json"
SESSION_FILE_PATH = APP_DATA_DIR / "session.json"
SETTINGS_FILE_PATH = APP_DATA_DIR / "settings.json"
BOOKMARKS_FILE_PATH = APP_DATA_DIR / "bookmarks.json"
