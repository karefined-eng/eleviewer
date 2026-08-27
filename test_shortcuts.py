from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtGui import QShortcut

from ui import MainWindow


SHORTCUTS = {
    "Escape": "handle_escape",
    "Alt+E": "bring_to_front_and_new_note",
    "Alt+V": "toggle_vault_panel",
    "Ctrl+Q": "open_quick_switcher",
    "Ctrl+T": "open_web_tab",
    "Ctrl+Shift+W": "toggle_web_panel",
    "Ctrl+Shift+T": "reopen_closed_tab",
    "F9": "toggle_tts_bar",
    "Ctrl+N": "new_tab",
    "Ctrl+O": "open_file",
    "Ctrl+S": "save_file",
    "Ctrl+Shift+S": "save_file_as",
    "Ctrl+W": "close_current_tab",
    "Ctrl+F": "show_find",
    "Ctrl+H": "show_replace",
    "Ctrl+Shift+F": "open_vault_search",
    "Ctrl+Alt+B": "toggle_bookmarks_panel",
    "Ctrl+D": "bookmark_current_tab",
    "F1": "open_getting_started",
    "Alt+S": "open_settings",
}


class ShortcutHost(QWidget):
    def __init__(self, called):
        super().__init__()
        self.called = called

    def record(self, name):
        self.called.append(name)

    def handle_escape(self): self.record("handle_escape")
    def bring_to_front_and_new_note(self): self.record("bring_to_front_and_new_note")
    def toggle_vault_panel(self): self.record("toggle_vault_panel")
    def open_quick_switcher(self): self.record("open_quick_switcher")
    def open_web_tab(self): self.record("open_web_tab")
    def toggle_web_panel(self): self.record("toggle_web_panel")
    def reopen_closed_tab(self): self.record("reopen_closed_tab")
    def toggle_tts_bar(self): self.record("toggle_tts_bar")
    def new_tab(self): self.record("new_tab")
    def open_file(self): self.record("open_file")
    def save_file(self): self.record("save_file")
    def save_file_as(self): self.record("save_file_as")
    def close_current_tab(self): self.record("close_current_tab")
    def show_find(self): self.record("show_find")
    def show_replace(self): self.record("show_replace")
    def open_vault_search(self): self.record("open_vault_search")
    def toggle_bookmarks_panel(self): self.record("toggle_bookmarks_panel")
    def bookmark_current_tab(self): self.record("bookmark_current_tab")
    def open_getting_started(self): self.record("open_getting_started")
    def open_settings(self): self.record("open_settings")


def test_documented_shortcuts_are_application_wide_and_connected():
    app = QApplication.instance() or QApplication([])
    called = []
    host = ShortcutHost(called)
    MainWindow._setup_global_shortcuts(host)

    shortcuts = {
        shortcut.key().toString(): shortcut
        for shortcut in host.findChildren(QShortcut)
    }
    shortcut_names = {"Escape": "Esc", **{key: key for key in SHORTCUTS if key != "Escape"}}
    assert set(shortcut_names.values()).issubset(shortcuts)
    assert all(shortcut.context() == Qt.ApplicationShortcut for shortcut in shortcuts.values())

    host.show()
    app.processEvents()
    for key_name, expected_method in SHORTCUTS.items():
        called.clear()
        shortcut = shortcuts[shortcut_names[key_name]]
        shortcut.activated.emit()
        assert called == [expected_method], f"{key_name} connected as {called}"

    host.close()
    host.deleteLater()
    app.processEvents()
