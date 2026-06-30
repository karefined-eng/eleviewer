from datetime import datetime

from PySide6.QtCore import QTimer

from file_handler import get_file_content
from save_utils import atomic_write
from settings import load_settings


class AutoSaver:

    def __init__(self, main_window):
        self.main_window = main_window
        self.timer = QTimer()
        self.timer.timeout.connect(self.autosave)
        self.apply_settings()

    def apply_settings(self):
        settings = load_settings()
        if settings.get("autosave_enabled", True):
            interval_ms = settings.get("autosave_interval_seconds", 5) * 1000
            self.timer.setInterval(interval_ms)
            if not self.timer.isActive():
                self.timer.start()
        else:
            self.timer.stop()

    def autosave(self):
        if not load_settings().get("autosave_enabled", True):
            return

        tabs = self.main_window.tabs
        saved_any = False

        for i in range(tabs.count()):
            editor = tabs.widget(i)
            if not editor or not getattr(editor, "is_modified", False):
                continue
            if not getattr(editor, "file_path", None):
                continue

            try:
                content = get_file_content(editor, editor.file_path)
                atomic_write(editor.file_path, content)
                editor.is_modified = False
                self.main_window.update_tab_title(editor)
                saved_any = True
            except Exception as e:
                self.main_window.show_status_message(f"Autosave failed: {e}", 5000)
                return

        if saved_any:
            self.main_window.show_status_message(
                f"Autosaved at {datetime.now().strftime('%H:%M:%S')}", 3000
            )
