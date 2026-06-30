import json
import os

from paths import RECENT_FILE_PATH


def load_recent_files(validate=True):
    if not RECENT_FILE_PATH.exists():
        return []
    try:
        with open(RECENT_FILE_PATH, "r", encoding="utf-8") as file:
            files = json.load(file)
        if validate:
            original_count = len(files)
            files = [f for f in files if os.path.exists(f)]
            if len(files) != original_count:
                save_recent_files(files)
        return files
    except Exception:
        return []


def save_recent_files(files):
    with open(RECENT_FILE_PATH, "w", encoding="utf-8") as file:
        json.dump(files, file, indent=4)


def save_recent_file(path):
    files = load_recent_files(validate=False)
    if path in files:
        files.remove(path)
    files.insert(0, path)
    files = files[:10]
    with open(RECENT_FILE_PATH, "w", encoding="utf-8") as file:
        json.dump(files, file, indent=4)


def remove_recent_file(path):
    files = load_recent_files(validate=False)
    if path in files:
        files.remove(path)
    with open(RECENT_FILE_PATH, "w", encoding="utf-8") as file:
        json.dump(files, file, indent=4)
