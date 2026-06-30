from PySide6.QtWidgets import (
    QMainWindow, QTabWidget, QFileDialog, QMessageBox,
    QSplitter, QMenu, QToolBar,
)
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt, QUrl, QSize
import os

try:
    from PySide6.QtWebEngineWidgets import QWebEngineView
    WEB_AVAILABLE = True
except ImportError:
    WEB_AVAILABLE = False

from file_handler import (
    create_viewer_widget, get_file_content, get_file_extension, is_binary_format,
)
from recent_files import load_recent_files, save_recent_file
from pinned_files import load_pinned_files, save_pinned_file, remove_pinned_file, is_pinned
from session_manager import load_session, save_session
from quick_switcher import QuickSwitcher
from settings import load_settings
from settings_dialog import SettingsDialog
from theme import main_window_stylesheet
from save_utils import atomic_write


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.autosaver = None
        self.closed_tabs = []
        self.web_panel = None

        self.setWindowTitle("EleViewer")
        self.resize(1200, 800)
        self.setStyleSheet(main_window_stylesheet())
        self.statusBar().showMessage("Ready")

        self._build_toolbar()
        self._build_tabs()
        self.create_menu()
        self.restore_session()

        if self.tabs.count() == 0:
            self.new_tab()

        self.tabs.currentChanged.connect(self.update_status_bar)

    def _build_toolbar(self):
        self.toolbar = QToolBar("Main Toolbar")
        self.toolbar.setMovable(False)
        self.toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(self.toolbar)

        open_btn = QAction("📂 Open", self)
        open_btn.setToolTip("Open File (Ctrl+O)")
        open_btn.triggered.connect(self.open_file)
        self.toolbar.addAction(open_btn)

        save_btn = QAction("💾 Save", self)
        save_btn.setToolTip("Save File (Ctrl+S)")
        save_btn.triggered.connect(self.save_file)
        self.toolbar.addAction(save_btn)

        if WEB_AVAILABLE:
            web_btn = QAction("🌐 Web", self)
            web_btn.setToolTip("Toggle Web Browser Panel")
            web_btn.triggered.connect(self.toggle_web_panel)
            self.toolbar.addAction(web_btn)

    def _build_tabs(self):
        self.splitter = QSplitter(Qt.Horizontal)
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tabs.customContextMenuRequested.connect(self.show_tab_context_menu)
        self.splitter.addWidget(self.tabs)
        self.setCentralWidget(self.splitter)

    def show_status_message(self, message, timeout_ms=0):
        self.statusBar().showMessage(message, timeout_ms)

    def update_status_bar(self):
        editor = self.current_editor()
        if not editor:
            self.show_status_message("Ready")
            return
        path = getattr(editor, "file_path", None)
        name = os.path.basename(path) if path else "Untitled"
        modified = " • Modified" if getattr(editor, "is_modified", False) else ""
        location = path if path else "Unsaved document"
        self.show_status_message(f"{name}{modified} — {location}")

    def _connect_editor_signals(self, editor):
        if hasattr(editor, "textChanged"):
            editor.textChanged.connect(lambda ed=editor: self._on_editor_changed(ed))

    def _on_editor_changed(self, editor):
        self.update_tab_title(editor)
        self.update_status_bar()

    def _add_editor_tab(self, editor, name):
        self._connect_editor_signals(editor)
        index = self.tabs.addTab(editor, name)
        self.tabs.setCurrentIndex(index)
        self.update_status_bar()
        return index

    def closeEvent(self, event):
        has_modified = any(
            getattr(self.tabs.widget(i), "is_modified", False)
            for i in range(self.tabs.count())
        )
        if has_modified:
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "Save all modified files before quitting?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
            )
            if reply == QMessageBox.Cancel:
                event.ignore()
                return
            if reply == QMessageBox.Yes:
                if not self.save_all_modified():
                    event.ignore()
                    return

        self.save_current_session()
        event.accept()

    def save_all_modified(self):
        for i in range(self.tabs.count()):
            editor = self.tabs.widget(i)
            if not getattr(editor, "is_modified", False):
                continue
            self.tabs.setCurrentIndex(i)
            path = getattr(editor, "file_path", None)
            if path:
                self.save_file()
            else:
                self.save_file_as()
            if getattr(editor, "is_modified", False):
                return False
        return True

    def save_current_session(self):
        tabs_info = []
        for i in range(self.tabs.count()):
            editor = self.tabs.widget(i)
            file_path = getattr(editor, "file_path", None)

            if file_path and os.path.exists(file_path):
                content = ""
            elif is_binary_format(file_path or ""):
                content = ""
            elif hasattr(editor, "toPlainText"):
                content = editor.toPlainText()
            else:
                content = ""

            tabs_info.append({
                "file_path": file_path,
                "content": content,
                "is_active": (i == self.tabs.currentIndex()),
                "is_modified": getattr(editor, "is_modified", False),
            })
        save_session(tabs_info)

    def restore_session(self):
        session = load_session()
        active_index = 0
        for tab_info in session:
            file_path = tab_info.get("file_path")
            content = tab_info.get("content", "")
            is_active = tab_info.get("is_active", False)
            try:
                if file_path and os.path.exists(file_path):
                    editor = create_viewer_widget(file_path)
                elif content:
                    from editor import EditorTab
                    editor = EditorTab()
                    editor.file_path = file_path
                    editor.setPlainText(content)
                    if tab_info.get("is_modified", False):
                        editor.is_modified = True
                else:
                    from editor import EditorTab
                    editor = EditorTab()
                    editor.file_path = file_path

                name = os.path.basename(file_path) if file_path else "Untitled"
                if getattr(editor, "is_modified", False):
                    name += "*"
                self._connect_editor_signals(editor)
                self.tabs.addTab(editor, name)
                if is_active:
                    active_index = self.tabs.count() - 1
            except Exception as e:
                print(f"Failed to restore tab: {e}")
        if self.tabs.count() > 0:
            self.tabs.setCurrentIndex(active_index)
            self.update_status_bar()

    def create_menu(self):
        menu = self.menuBar()
        file_menu = menu.addMenu("File")

        actions = [
            ("New", "Ctrl+N", self.new_tab),
            ("Open...", "Ctrl+O", self.open_file),
            ("Save", "Ctrl+S", self.save_file),
            ("Save As...", "Ctrl+Shift+S", self.save_file_as),
        ]
        for name, shortcut, trigger in actions:
            action = QAction(name, self)
            action.setShortcut(shortcut)
            action.triggered.connect(trigger)
            file_menu.addAction(action)

        file_menu.addSeparator()

        close_action = QAction("Close Tab", self)
        close_action.setShortcut("Ctrl+W")
        close_action.triggered.connect(lambda: self.close_tab(self.tabs.currentIndex()))
        file_menu.addAction(close_action)

        reopen_action = QAction("Reopen Closed Tab", self)
        reopen_action.setShortcut("Ctrl+Shift+T")
        reopen_action.triggered.connect(self.reopen_closed_tab)
        file_menu.addAction(reopen_action)

        self.pinned_menu = file_menu.addMenu("Pinned Files")
        self.recent_menu = file_menu.addMenu("Recent Files")

        file_menu.addSeparator()

        switcher_action = QAction("Quick Switcher", self)
        switcher_action.setShortcut("Ctrl+P")
        switcher_action.triggered.connect(self.open_quick_switcher)
        file_menu.addAction(switcher_action)

        file_menu.addSeparator()

        settings_action = QAction("Settings...", self)
        settings_action.triggered.connect(self.open_settings)
        file_menu.addAction(settings_action)

        self.update_menus()

    def open_settings(self):
        dialog = SettingsDialog(self)
        if dialog.exec():
            if self.autosaver:
                self.autosaver.apply_settings()
            settings = dialog.get_settings()
            if self.web_panel is not None and settings.get("web_url"):
                self.web_panel.setUrl(QUrl(settings["web_url"]))
            self.show_status_message("Settings saved", 2000)

    def update_menus(self):
        self.update_recent_files_menu()
        self.update_pinned_files_menu()

    def update_tab_title(self, editor):
        index = self.tabs.indexOf(editor)
        if index == -1:
            return
        path = getattr(editor, "file_path", None)
        name = os.path.basename(path) if path else "Untitled"
        if getattr(editor, "is_modified", False):
            name += "*"
        self.tabs.setTabText(index, name)

    def new_tab(self):
        from editor import EditorTab
        editor = EditorTab()
        self._add_editor_tab(editor, "Untitled")

    def show_tab_context_menu(self, pos):
        index = self.tabs.tabBar().tabAt(pos)
        if index == -1:
            return
        editor = self.tabs.widget(index)
        path = getattr(editor, "file_path", None)
        menu = QMenu(self)
        if path:
            if is_pinned(path):
                pin_action = menu.addAction("📌 Unpin File")
                pin_action.triggered.connect(lambda: self.unpin_file(path))
            else:
                pin_action = menu.addAction("📌 Pin File")
                pin_action.triggered.connect(lambda: self.pin_file(path))
            menu.addSeparator()
        close_action = menu.addAction("Close Tab")
        close_action.triggered.connect(lambda: self.close_tab(index))
        menu.exec_(self.tabs.mapToGlobal(pos))

    def pin_file(self, path):
        save_pinned_file(path)
        self.update_menus()

    def unpin_file(self, path):
        remove_pinned_file(path)
        self.update_menus()

    def close_tab(self, index):
        editor = self.tabs.widget(index)
        if not editor:
            return

        if getattr(editor, "is_modified", False):
            reply = QMessageBox.question(
                self, "Unsaved Changes", "Save before closing?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
            )
            if reply == QMessageBox.Yes:
                self.tabs.setCurrentIndex(index)
                self.save_file()
                if getattr(editor, "is_modified", False):
                    return
            elif reply == QMessageBox.Cancel:
                return

        self.closed_tabs.append({
            "content": editor.toPlainText() if hasattr(editor, "toPlainText") else "",
            "file_path": getattr(editor, "file_path", None),
            "modified": getattr(editor, "is_modified", False),
        })
        self.tabs.removeTab(index)
        if self.tabs.count() == 0:
            self.new_tab()
        else:
            self.update_status_bar()

    def reopen_closed_tab(self):
        if not self.closed_tabs:
            self.show_status_message("No closed tabs to reopen", 2000)
            return
        tab_data = self.closed_tabs.pop()
        file_path = tab_data["file_path"]
        if file_path and os.path.exists(file_path):
            editor = create_viewer_widget(file_path)
            if tab_data["modified"] and tab_data["content"] and not is_binary_format(file_path):
                editor.setPlainText(tab_data["content"])
                editor.is_modified = True
        elif tab_data["content"]:
            from editor import EditorTab
            editor = EditorTab()
            editor.file_path = file_path
            editor.setPlainText(tab_data["content"])
            editor.is_modified = tab_data["modified"]
        else:
            from editor import EditorTab
            editor = EditorTab()
            editor.file_path = file_path

        name = os.path.basename(file_path) if file_path else "Untitled"
        if tab_data["modified"]:
            name += "*"
        self._add_editor_tab(editor, name)

    def open_quick_switcher(self):
        recent = load_recent_files(validate=True)
        pinned = load_pinned_files(validate=True)
        switcher = QuickSwitcher(recent, pinned, self)
        switcher.file_selected.connect(self.open_recent_file)
        switcher.exec()

    def current_editor(self):
        return self.tabs.currentWidget()

    def switch_to_tab_if_open(self, path):
        normalized_path = os.path.abspath(path)
        for i in range(self.tabs.count()):
            editor = self.tabs.widget(i)
            tab_path = getattr(editor, "file_path", None)
            if tab_path and os.path.abspath(tab_path) == normalized_path:
                self.tabs.setCurrentIndex(i)
                self.update_status_bar()
                return True
        return False

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open File", "",
            "All Supported (*.md *.txt *.docx *.xlsx *.pdf);;"
            "Word (*.docx);;Excel (*.xlsx);;PDF (*.pdf);;"
            "Markdown (*.md);;Text (*.txt)",
        )
        if not path:
            return
        if self.switch_to_tab_if_open(path):
            return
        try:
            editor = create_viewer_widget(path)
            save_recent_file(path)
            self.update_menus()
            self._add_editor_tab(editor, os.path.basename(path))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open file: {str(e)}")

    def open_recent_file(self, path):
        if self.switch_to_tab_if_open(path):
            return
        try:
            editor = create_viewer_widget(path)
            self._add_editor_tab(editor, os.path.basename(path))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open file: {str(e)}")

    def save_file(self):
        editor = self.current_editor()
        if not editor:
            return False
        path = getattr(editor, "file_path", None)
        if not path:
            self.save_file_as()
            return not getattr(editor, "is_modified", False)
        try:
            content = get_file_content(editor, path)
            atomic_write(path, content)
            editor.is_modified = False
            self.update_tab_title(editor)
            self.show_status_message(f"Saved {os.path.basename(path)}", 3000)
            self.update_status_bar()
            return True
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save file: {str(e)}")
            return False

    def save_file_as(self):
        editor = self.current_editor()
        if not editor:
            return
        suggested_name = "Untitled.txt"
        if hasattr(editor, "toPlainText"):
            text = editor.toPlainText()
            if text:
                first_line = text.split("\n")[0].strip()
                if first_line and len(first_line) < 100:
                    suggested_name = first_line
        if not get_file_extension(suggested_name):
            suggested_name += ".txt"
        initial_path = os.path.join(os.getcwd(), suggested_name)
        path, _ = QFileDialog.getSaveFileName(
            self, "Save As", initial_path,
            "All Supported (*.md *.txt *.docx *.xlsx *.pdf)",
        )
        if not path:
            return
        try:
            content = get_file_content(editor, path)
            atomic_write(path, content)
            editor.file_path = path
            editor.is_modified = False
            save_recent_file(path)
            self.update_menus()
            self.update_tab_title(editor)
            self.show_status_message(f"Saved as {os.path.basename(path)}", 3000)
            self.update_status_bar()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save file: {str(e)}")

    def update_recent_files_menu(self):
        self.recent_menu.clear()
        recent_files = load_recent_files(validate=True)
        if not recent_files:
            self.recent_menu.addAction("(no recent files)")
            return
        for path in recent_files:
            action = QAction(os.path.basename(path), self)
            action.setToolTip(path)
            action.triggered.connect(lambda checked=False, p=path: self.open_recent_file(p))
            self.recent_menu.addAction(action)

    def update_pinned_files_menu(self):
        self.pinned_menu.clear()
        pinned_files = load_pinned_files(validate=True)
        if not pinned_files:
            self.pinned_menu.addAction("(no pinned files)")
            return
        for path in pinned_files:
            action = QAction(os.path.basename(path), self)
            action.setToolTip(path)
            action.triggered.connect(lambda checked=False, p=path: self.open_recent_file(p))
            self.pinned_menu.addAction(action)

    def _web_url(self):
        return load_settings().get("web_url", "https://sakai.ug.edu.gh")

    def toggle_web_panel(self):
        if self.web_panel is None:
            if not WEB_AVAILABLE:
                QMessageBox.warning(self, "Missing Module", "QtWebEngine not installed.")
                return
            self.web_panel = QWebEngineView()
            self.web_panel.setUrl(QUrl(self._web_url()))
            self.web_panel.setFixedWidth(800)
            self.splitter.addWidget(self.web_panel)
            self.splitter.setSizes([600, 800])

        visibility = self.web_panel.isVisible()
        self.web_panel.setVisible(not visibility)

        if not visibility:
            self.web_panel.setUrl(QUrl(self._web_url()))
            self.splitter.setSizes([600, 800])
        else:
            self.splitter.setSizes([1200, 0])
