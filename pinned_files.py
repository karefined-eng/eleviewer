import json
import os

from paths import PINNED_FILE_PATH


def load_pinned_files(validate=True):
    if not PINNED_FILE_PATH.exists():
        return []
    try:
        with open(PINNED_FILE_PATH, "r", encoding="utf-8") as file:
            files = json.load(file)
        if validate:
            original_count = len(files)
            files = [f for f in files if os.path.exists(f)]
            if len(files) != original_count:
                _save_pinned_files(files)
        return files
    except Exception:
        return []


def _save_pinned_files(files):
    with open(PINNED_FILE_PATH, "w", encoding="utf-8") as file:
        json.dump(files, file, indent=4)


def save_pinned_file(path):
    files = load_pinned_files(validate=False)
    if path in files:
        files.remove(path)
    files.insert(0, path)
    files = files[:10]
    _save_pinned_files(files)


def remove_pinned_file(path):
    files = load_pinned_files(validate=False)
    if path in files:
        files.remove(path)
    _save_pinned_files(files)


def is_pinned(path):
    return path in load_pinned_files(validate=False)
