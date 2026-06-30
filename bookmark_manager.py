"""CRUD operations for document position bookmarks."""

import json
import os
from datetime import datetime, timezone
from uuid import uuid4

from paths import BOOKMARKS_FILE_PATH

EMPTY_DATA = {"bookmarks": []}


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _load_raw():
    if not BOOKMARKS_FILE_PATH.exists():
        return {"bookmarks": []}
    try:
        with open(BOOKMARKS_FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if "bookmarks" not in data or not isinstance(data["bookmarks"], list):
            return {"bookmarks": []}
        return data
    except Exception:
        return {"bookmarks": []}


def _save_raw(data):
    BOOKMARKS_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(BOOKMARKS_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def load_bookmarks(validate=True):
    bookmarks = _load_raw().get("bookmarks", [])
    if not validate:
        return bookmarks
    valid = [b for b in bookmarks if os.path.exists(b.get("file_path", ""))]
    if len(valid) != len(bookmarks):
        _save_raw({"bookmarks": valid})
    return valid


def add_bookmark(
    file_path,
    page_number=0,
    scroll_position_y=0.0,
    label=None,
    color_tag=None,
):
    file_path = os.path.abspath(file_path)
    if label is None:
        if page_number > 0:
            label = f"Page {page_number + 1}"
        else:
            label = os.path.basename(file_path)

    entry = {
        "id": str(uuid4()),
        "file_path": file_path,
        "page_number": int(page_number),
        "scroll_position_y": float(scroll_position_y),
        "label": label,
        "created_at": _now_iso(),
        "color_tag": color_tag,
    }
    data = _load_raw()
    data["bookmarks"].insert(0, entry)
    _save_raw(data)
    return entry


def remove_bookmark(bookmark_id):
    data = _load_raw()
    data["bookmarks"] = [b for b in data["bookmarks"] if b.get("id") != bookmark_id]
    _save_raw(data)


def rename_bookmark(bookmark_id, new_label):
    data = _load_raw()
    for bookmark in data["bookmarks"]:
        if bookmark.get("id") == bookmark_id:
            bookmark["label"] = new_label.strip() or bookmark["label"]
            break
    _save_raw(data)


def get_bookmark(bookmark_id):
    for bookmark in load_bookmarks(validate=False):
        if bookmark.get("id") == bookmark_id:
            return bookmark
    return None
