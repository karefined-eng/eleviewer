import os
import sys
from pathlib import Path

# BASE_DIR: root of bundled resources. Handles three execution contexts:
#   1. PyInstaller frozen exe  -> sys._MEIPASS (temp extraction dir)
#   2. Source / dev run        -> directory containing main.py / this file
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys._MEIPASS)
else:
    BASE_DIR = Path(__file__).resolve().parent

APP_DATA_DIR = Path(os.getenv("APPDATA", Path.home())) / "EleViewer"
APP_DATA_DIR.mkdir(parents=True, exist_ok=True)

RECENT_FILE_PATH = APP_DATA_DIR / "recent_files.json"
PINNED_FILE_PATH = APP_DATA_DIR / "pinned_files.json"
SESSION_FILE_PATH = APP_DATA_DIR / "session.json"
SETTINGS_FILE_PATH = APP_DATA_DIR / "settings.json"
BOOKMARKS_FILE_PATH = APP_DATA_DIR / "bookmarks.json"
