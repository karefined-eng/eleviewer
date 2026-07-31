import urllib.request
import os
from pathlib import Path

ICONS = [
    "file-plus", "panel-left", "folder-open", "save", "globe", "settings",
    "book-open", "type", "table", "monitor", "volume-2", "x", "play", "square",
    "chevron-left", "chevron-right", "chevron-down", "menu", "maximize-2", "minimize-2",
    "search", "plus", "rotate-cw", "link", "pencil", "eraser", "bold", "italic",
    "underline", "strikethrough", "list", "list-ordered", "zoom-in", "zoom-out",
    "pin", "pin-off", "message-square", "help-circle", "pause", "volume-x",
    "arrow-up", "arrow-down", "bookmark"
]

ICONS_DIR = Path("icons")
ICONS_DIR.mkdir(exist_ok=True)

def download_lucide_icon(name, target_name=None):
    try:
        urllib.request.urlretrieve(
            f"https://raw.githubusercontent.com/lucide-icons/lucide/main/icons/{name}.svg",
            ICONS_DIR / f"{target_name or name}.svg"
        )
        print(f"Downloaded: {target_name or name}")
    except Exception as e:
        print(f"Error downloading {name}: {e}")

if __name__ == "__main__":
    for icon_name in ICONS:
        if icon_name == "help-circle":
            download_lucide_icon("circle-help", "help-circle")
            if not (ICONS_DIR / "help-circle.svg").exists():
                download_lucide_icon("help-circle")
        else:
            download_lucide_icon(icon_name)
