"""Capture UI screenshots of the redesigned web dock / toolbar for visual review.

Uses a temp settings file so the user's real settings.json is untouched.
Run: python capture_ui_check.py
"""
import json
import os
import sys
import tempfile
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("QTWEBENGINE_CHROMIUM_FLAGS", "--disable-gpu --no-sandbox")

out_dir = Path(tempfile.gettempdir()) / "eleviewer_ui_check"
out_dir.mkdir(exist_ok=True)

# Redirect the whole config dir (settings, session, recents, bookmarks) before
# paths.py is imported, so captures never touch the real AppData profile.
os.environ["APPDATA"] = str(out_dir)

cap_settings = out_dir / "settings.json"

import settings as settings_mod
settings_mod.SETTINGS_FILE_PATH = cap_settings  # isolate from real config


def write_settings(theme_mode, show_toolbar):
    cap_settings.write_text(json.dumps({
        "theme_mode": theme_mode,
        "show_toolbar": show_toolbar,
        "launch_behavior": "fresh",
        "fresh_session_behavior": "blank_tab",
        "onboarding_completed": True,
    }), encoding="utf-8")


def capture(theme_mode, show_toolbar, name):
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import QTimer
    from ui import MainWindow

    write_settings(theme_mode, show_toolbar)
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.resize(1400, 900)
    window.new_tab()
    window.show()
    window.open_web_tab()

    shots = []
    def snap(label):
        path = out_dir / f"{name}_{label}.png"
        window.grab().save(str(path))
        shots.append(path)
        print(f"saved {path}")

    def step1():
        snap("webdock")
        if show_toolbar:
            window.toggle_main_toolbar()
        QTimer.singleShot(300, step2)

    def step2():
        snap("toolbar_hidden" if show_toolbar else "webdock_only")
        window._quitting = True
        window.close()
        QTimer.singleShot(200, app.quit)

    QTimer.singleShot(1500, step1)
    app.exec()
    return shots


mode = sys.argv[1] if len(sys.argv) > 1 else "dark"
all_shots = []
all_shots += capture(mode, True, mode)
print("DONE")
