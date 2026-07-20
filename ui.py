from PySide6.QtWidgets import (
    QMainWindow, QTabWidget, QFileDialog, QMessageBox,
    QSplitter, QMenu, QToolBar, QToolButton, QVBoxLayout, QWidget,
    QDockWidget,
)
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtCore import Qt, QSize
import os

from editor import EditorTab
from bookmark_manager import add_bookmark, load_bookmarks
from bookmark_panel import BookmarkPanel
from find_replace import FindReplaceWidget

try:
    from web_panel import WebPanel, WEB_AVAILABLE
except ImportError:
    WEB_AVAILABLE = False

from file_handler import (
    create_viewer_widget, get_file_content, get_file_extension, is_binary_format,
)
from recent_files import load_recent_files, save_recent_file
from pinned_files import load_pinned_files, save_pinned_file, remove_pinned_file, is_pinned
from session_manager import load_session, save_session
from quick_switcher import QuickSwitcher
from settings import load_settings, save_settings
from settings_dialog import SettingsDialog
from theme import (
    main_window_stylesheet, ICON_SIZE_TOOLBAR, ICON_SIZE_COMPACT,
    BRAND_PRIMARY, BRAND_PANEL_2
)
from save_utils import atomic_write
from icons import icon
from vault_explorer import VaultExplorer
from branding_logo import create_eleviewer_icon
from file_handler import get_file_extension


# ── File-type icon helper ───────────────────────────────────────────
_TAB_ICON_MAP = {
    "md": "book-open",
    "txt": "type",
    "csv": "table",
    "pdf": "book-open",
    "docx": "file-plus",
    "xlsx": "table",
    "html": "globe",
    "htm": "globe",
}


def _tab_icon_for(path):
    """Return a small QIcon appropriate for the file extension."""
    if not path:
        return icon("file-plus", size=ICON_SIZE_COMPACT)
    ext = get_file_extension(path)
    name = _TAB_ICON_MAP.get(ext, "type")
    return icon(name, size=ICON_SIZE_COMPACT)


class MainWindow(QMainWindow):

    FILE_FILTER = (
        "All Supported (*.md *.txt *.docx *.xlsx *.pdf *.csv *.html *.htm);;"
        "Word (*.docx);;Excel (*.xlsx);;PDF (*.pdf);;"
        "Markdown (*.md);;HTML (*.html *.htm);;Text (*.txt);;CSV (*.csv)"
    )

    def __init__(self):
        super().__init__()
        self.autosaver = None
        self.closed_tabs = []
        self.vault_panel = None
        self._web_dock = None
        self.bookmarks_panel = None

        self.setWindowTitle("EleViewer")
        self.setWindowIcon(create_eleviewer_icon(64))
        self.resize(1200, 800)
        self.setStyleSheet(main_window_stylesheet())
        self.statusBar().showMessage("Ready")

        self._build_layout()
        self._build_toolbar()
        self.create_menu()
        self._restore_vault()
        self.restore_session()

        if self.tabs.count() == 0:
            self.new_tab()

        self.tabs.currentChanged.connect(self.update_status_bar)

    def _build_layout(self):
        self.main_splitter = QSplitter(Qt.Horizontal)

        self.vault_panel = VaultExplorer()
        self.vault_panel.setMinimumWidth(180)
        self.vault_panel.setMaximumWidth(420)
        self.vault_panel.file_opened.connect(self._open_vault_file)
        self.vault_panel.btn_add.clicked.connect(self.add_vault)
        self.main_splitter.addWidget(self.vault_panel)

        self.editor_splitter = QSplitter(Qt.Horizontal)
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setDocumentMode(True)
        self.tabs.tabBar().setMovable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tabs.customContextMenuRequested.connect(self.show_tab_context_menu)
        
        self.find_replace_panel = FindReplaceWidget()
        self.find_replace_panel.hide()
        self.find_replace_panel.find_next_requested.connect(self._on_find_next)
        self.find_replace_panel.replace_requested.connect(self._on_replace)
        self.find_replace_panel.replace_all_requested.connect(self._on_replace_all)

        editor_layout = QVBoxLayout()
        editor_layout.setContentsMargins(0, 0, 0, 0)
        editor_layout.setSpacing(0)
        editor_layout.addWidget(self.tabs)
        editor_layout.addWidget(self.find_replace_panel)
        
        editor_container = QWidget()
        editor_container.setLayout(editor_layout)
        
        self.editor_splitter.addWidget(editor_container)

        self.bookmarks_panel = BookmarkPanel()
        self.bookmarks_panel.setMinimumWidth(200)
        self.bookmarks_panel.setMaximumWidth(360)
        self.bookmarks_panel.bookmark_activated.connect(self._navigate_to_bookmark)
        self.bookmarks_panel.hide()
        self.editor_splitter.addWidget(self.bookmarks_panel)

        self.main_splitter.addWidget(self.editor_splitter)
        self.main_splitter.setSizes([0, 1200])
        self.vault_panel.hide()

        self.setCentralWidget(self.main_splitter)

    def _build_toolbar(self):
        self.toolbar = QToolBar("Main Toolbar")
        self.toolbar.setMovable(False)
        self.toolbar.setIconSize(QSize(ICON_SIZE_TOOLBAR, ICON_SIZE_TOOLBAR))
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.addToolBar(self.toolbar)





        new_file_action = QAction(icon("file-plus", size=ICON_SIZE_TOOLBAR), "New File", self)
        new_file_action.setToolTip("New File")
        new_file_action.triggered.connect(self._show_new_file_menu_from_toolbar)
        self.toolbar.addAction(new_file_action)

        vault_btn = QAction(icon("panel-left", size=ICON_SIZE_TOOLBAR), "Toggle Vault", self)
        vault_btn.setToolTip("Toggle Vault (Alt+V)")
        vault_btn.setShortcut("Alt+V")
        vault_btn.triggered.connect(self.toggle_vault_panel)
        self.toolbar.addAction(vault_btn)

        open_btn = QAction(icon("folder-open", size=ICON_SIZE_TOOLBAR), "Open", self)
        open_btn.setToolTip("Open File (Ctrl+O)")
        open_btn.setShortcut("Ctrl+O")
        open_btn.triggered.connect(self.open_file)
        self.toolbar.addAction(open_btn)

        save_btn = QAction(icon("save", size=ICON_SIZE_TOOLBAR), "Save", self)
        save_btn.setToolTip("Save File (Ctrl+S)")
        save_btn.setShortcut("Ctrl+S")
        save_btn.triggered.connect(self.save_file)
        self.toolbar.addAction(save_btn)

        if WEB_AVAILABLE:
            web_btn = QAction(icon("globe", size=ICON_SIZE_TOOLBAR), "Web Panel", self)
            web_btn.setToolTip("Open Web Browser (Ctrl+T)")
            web_btn.triggered.connect(self.open_web_tab)
            self.toolbar.addAction(web_btn)

        settings_btn = QAction(icon("settings", size=ICON_SIZE_TOOLBAR), "Settings", self)
        settings_btn.setToolTip("Settings")
        settings_btn.triggered.connect(self.open_settings)
        self.toolbar.addAction(settings_btn)

    def _add_menu_action(self, menu, text, slot, shortcut=None):
        action = QAction(text, self)
        if shortcut:
            action.setShortcut(shortcut)
        action.triggered.connect(slot)
        menu.addAction(action)
        return action

    def _build_popup_menu(self):
        menu = QMenu(self)
        self._add_menu_action(menu, "New Tab", self.new_tab)
        self._add_menu_action(menu, "Open File...", self.open_file)
        self._add_menu_action(menu, "Save", self.save_file)
        menu.addSeparator()
        menu.addAction("Open Folder", self.add_vault)
        self._add_menu_action(menu, "Toggle Vault", self.toggle_vault_panel, "Alt+V")
        menu.addSeparator()
        self._add_menu_action(menu, "Restore Tab", self.reopen_closed_tab, "Ctrl+Shift+T")
        self._add_menu_action(menu, "Quick Switcher", self.open_quick_switcher, "Ctrl+Q")
        menu.addSeparator()
        self._add_menu_action(menu, "Settings...", self.open_settings, "Alt+S")
        return menu

    def _restore_vault(self):
        settings = load_settings()
        self.vault_panel.set_show_all_files(settings.get("vault_show_all_files", False))
        self.vault_panel.restore_from_settings()

    def toggle_vault_panel(self):
        visible = self.vault_panel.isVisible()
        if visible:
            self.vault_panel.hide()
            self.main_splitter.setSizes([0, self.width()])
        else:
            self.vault_panel.show()
            self.main_splitter.setSizes([260, max(self.width() - 260, 400)])

    def add_vault(self):
        paths = load_settings().get("vault_paths", [])
        start = paths[0] if paths else os.getcwd()
        path = QFileDialog.getExistingDirectory(self, "Add Vault", start)
        if not path:
            return
        self.vault_panel.add_vault(path)
        if not self.vault_panel.isVisible():
            self.toggle_vault_panel()
        self.show_status_message(f"Vault added: {os.path.basename(path)}", 3000)

    def open_vault(self):
        self.add_vault()

    def _open_vault_file(self, path):
        if self.switch_to_tab_if_open(path):
            return
        try:
            editor = create_viewer_widget(path)
            self._wire_editor(editor)
            save_recent_file(path)
            self.update_menus()
            self._add_editor_tab(editor, os.path.basename(path))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open file: {str(e)}")

    def _wire_editor(self, editor):
        if hasattr(editor, "set_status_callback"):
            editor.set_status_callback(self.show_status_message)
        if hasattr(editor, "set_bookmark_callback"):
            editor.set_bookmark_callback(
                lambda data, ed=editor: self._add_bookmark_from_editor(ed, data),
            )

    @staticmethod
    def _elide_menu_label(path, max_len=36):
        name = os.path.basename(path)
        if len(name) <= max_len:
            return name
        keep = max_len - 3
        front = keep // 2
        back = keep - front
        return f"{name[:front]}...{name[-back:]}"

    def _add_bookmark_from_editor(self, editor, data):
        path = getattr(editor, "file_path", None)
        if not path:
            self.show_status_message("Save the file before bookmarking", 3000)
            return
        add_bookmark(
            path,
            page_number=data.get("page_number", 0),
            scroll_position_y=data.get("scroll_position_y", 0.0),
            label=data.get("label"),
        )
        self.bookmarks_panel.refresh()
        self.update_menus()
        self.show_status_message("Bookmark saved", 2000)

    def _navigate_to_bookmark(self, bookmark):
        path = bookmark.get("file_path")
        if not path or not os.path.exists(path):
            self.show_status_message("Bookmarked file not found", 3000)
            return
        if not self.switch_to_tab_if_open(path):
            try:
                editor = create_viewer_widget(path)
                self._wire_editor(editor)
                save_recent_file(path)
                self._add_editor_tab(editor, os.path.basename(path))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open file: {str(e)}")
                return
        editor = self.current_editor()
        if hasattr(editor, "go_to_bookmark"):
            editor.go_to_bookmark(
                bookmark.get("page_number", 0),
                bookmark.get("scroll_position_y", 0.0),
            )
        self.show_status_message(f"Opened bookmark: {bookmark.get('label', '')}", 2000)

    def toggle_bookmarks_panel(self):
        if self.bookmarks_panel is None:
            return
        visible = self.bookmarks_panel.isVisible()
        self.bookmarks_panel.setVisible(not visible)
        if not visible:
            self.bookmarks_panel.refresh()
            self.editor_splitter.setSizes([max(self.width() - 280, 400), 260])
        else:
            self.editor_splitter.setSizes([self.width(), 0])

    def show_status_message(self, message, timeout_ms=0):
        self.statusBar().showMessage(message, timeout_ms)

    def update_status_bar(self):
        editor = self.current_editor()
        if not editor:
            self.setWindowTitle("EleViewer")
            self.show_status_message("Ready")
            return
        path = getattr(editor, "file_path", None)
        name = os.path.basename(path) if path else "Untitled"
        modified = " • Modified" if getattr(editor, "is_modified", False) else ""

        # Dynamic window title  (matches site mockup: "EleViewer — filename.ext")
        self.setWindowTitle(f"EleViewer — {name}")

        # Rich status bar: tab count · shortcuts hint · file type
        tab_count = self.tabs.count()
        ext = get_file_extension(path) if path else ""
        ext_label = ext.upper() if ext else "TXT"
        parts = [
            f"{tab_count} tab{'s' if tab_count != 1 else ''}",
        ]
        if modified:
            parts.append("Modified")
        else:
            parts.append("session saved")
        shortcuts_hint = "Ctrl+Q quick switch · Alt+V vault"
        encoding = "UTF-8"
        left = " · ".join(parts)
        self.show_status_message(f"{left}    {shortcuts_hint}    {ext_label} · {encoding}")

    def _connect_editor_signals(self, editor):
        if hasattr(editor, "textChanged"):
            editor.textChanged.connect(lambda ed=editor: self._on_editor_changed(ed))

    def _on_editor_changed(self, editor):
        self.update_tab_title(editor)
        self.update_status_bar()

    def _add_editor_tab(self, editor, name):
        self._connect_editor_signals(editor)
        path = getattr(editor, "file_path", None)
        tab_icon = _tab_icon_for(path)
        index = self.tabs.addTab(editor, tab_icon, name)
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
                self, "Unsaved Changes",
                "Save all modified files before quitting?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
            )
            if reply == QMessageBox.Cancel:
                event.ignore()
                return
            if reply == QMessageBox.Yes and not self.save_all_modified():
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
        save_session(tabs_info, bookmarks_panel_visible=self.bookmarks_panel.isVisible())

    def restore_session(self):
        session = load_session()
        tabs = session.get("tabs", [])
        active_index = 0
        for tab_info in tabs:
            file_path = tab_info.get("file_path")
            content = tab_info.get("content", "")
            is_active = tab_info.get("is_active", False)
            try:
                if file_path and os.path.exists(file_path):
                    editor = create_viewer_widget(file_path)
                    self._wire_editor(editor)
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
        if session.get("bookmarks_panel_visible") and self.bookmarks_panel:
            self.bookmarks_panel.show()
            self.bookmarks_panel.refresh()
            self.editor_splitter.setSizes([max(self.width() - 280, 400), 260])

    def create_menu(self):
        menu = self.menuBar()

        file_menu = menu.addMenu("File")
        self._add_menu_action(file_menu, "New", self.new_tab, "Ctrl+N")
        self._add_menu_action(file_menu, "Open...", self.open_file, "Ctrl+O")
        self._add_menu_action(file_menu, "Save", self.save_file, "Ctrl+S")
        self._add_menu_action(file_menu, "Save As...", self.save_file_as, "Ctrl+Shift+S")
        file_menu.addSeparator()
        if WEB_AVAILABLE:
            self._add_menu_action(file_menu, "New Web Tab", self.open_web_tab, "Ctrl+T")
            file_menu.addSeparator()
        self._add_menu_action(
            file_menu, "Close Tab",
            lambda: self.close_tab(self.tabs.currentIndex()), "Ctrl+W",
        )

        edit_menu = menu.addMenu("Edit")
        self._add_menu_action(edit_menu, "Find...", self.show_find, "Ctrl+F")
        self._add_menu_action(edit_menu, "Replace...", self.show_replace, "Ctrl+H")

        vault_menu = menu.addMenu("Vault")
        vault_menu.addAction("Add Folder", self.add_vault)
        vault_menu.addAction("Remove Folder", self.vault_panel.remove_current_vault)
        self._add_menu_action(vault_menu, "Toggle Panel", self.toggle_vault_panel, "Alt+V")

        session_menu = menu.addMenu("Session")
        self._add_menu_action(session_menu, "Restore Tab", self.reopen_closed_tab, "Ctrl+Shift+T")
        self._add_menu_action(session_menu, "Quick Switcher", self.open_quick_switcher, "Ctrl+Q")
        session_menu.addSeparator()
        self._add_menu_action(
            session_menu, "Toggle Bookmarks", self.toggle_bookmarks_panel, "Ctrl+Alt+B",
        )
        session_menu.addSeparator()
        self.recent_menu = session_menu.addMenu("Recent Files")
        self.pinned_menu = session_menu.addMenu("Pinned Files")
        self.bookmarks_menu = session_menu.addMenu("Bookmarks")

        self._add_menu_action(menu, "Settings...", self.open_settings, "Alt+S")

        self.update_menus()

    def open_settings(self):
        dialog = SettingsDialog(self)
        if dialog.exec():
            if self.autosaver:
                self.autosaver.apply_settings()
            settings = dialog.get_settings()
            self.vault_panel.set_show_all_files(settings.get("vault_show_all_files", False))
            self.vault_panel.restore_from_settings()

            self.show_status_message("Settings saved", 2000)

    def update_menus(self):
        self.update_recent_files_menu()
        self.update_pinned_files_menu()
        self.update_bookmarks_menu()

    def update_tab_title(self, editor):
        index = self.tabs.indexOf(editor)
        if index == -1:
            return
        path = getattr(editor, "file_path", None)
        name = os.path.basename(path) if path else "Untitled"
        if getattr(editor, "is_modified", False):
            name += "*"
        self.tabs.setTabText(index, name)

    def _build_new_file_menu(self):
        menu = QMenu(self)
        
        def _add(text, ext, WidgetClass, **kwargs):
            action = QAction(text, self)
            action.triggered.connect(lambda: self._create_untitled_tab(ext, WidgetClass, **kwargs))
            menu.addAction(action)

        from editor import EditorTab
        from markdown_renderer import MarkdownViewer
        from docx_viewer import DocxViewer
        from xlsx_viewer import XlsxViewer
        
        _add("Plain Text (.txt)", ".txt", EditorTab)
        _add("Markdown (.md)", ".md", MarkdownViewer)
        _add("HTML (.html)", ".html", MarkdownViewer, is_html=True)
        _add("Word Document (.docx)", ".docx", DocxViewer)
        _add("Excel Spreadsheet (.xlsx)", ".xlsx", XlsxViewer)
        _add("CSV Spreadsheet (.csv)", ".csv", EditorTab)
        return menu

    def new_tab(self):
        self._create_untitled_tab(".txt", EditorTab)

    def _create_untitled_tab(self, ext, WidgetClass, **kwargs):
        if WidgetClass.__name__ == "EditorTab":
            editor = WidgetClass()
        else:
            editor = WidgetClass(None, **kwargs) if kwargs else WidgetClass(None)
        self._add_editor_tab(editor, f"Untitled{ext}")

    def _show_new_file_menu_from_toolbar(self):
        # Determine position for the popup menu
        # This is a bit of a hack: find the action in the toolbar and get its position
        action_widget = self.toolbar.widgetForAction(
            [a for a in self.toolbar.actions() if a.text() == "New File"][0]
        )
        if action_widget:
            pos = action_widget.mapToGlobal(action_widget.rect().bottomLeft())
            self._build_new_file_menu().exec(pos)
        else:
            # Fallback if widget for action not found (shouldn't happen with valid action)
            self._build_new_file_menu().exec(self.mapToGlobal(self.toolbar.pos()))

    def show_tab_context_menu(self, pos):
        index = self.tabs.tabBar().tabAt(pos)
        if index == -1:
            return
        editor = self.tabs.widget(index)
        path = getattr(editor, "file_path", None)
        menu = QMenu(self)
        if path:
            if is_pinned(path):
                pin_action = menu.addAction(icon("pin", size=ICON_SIZE_COMPACT), "Unpin File")
                pin_action.triggered.connect(lambda: self.unpin_file(path))
            else:
                pin_action = menu.addAction(icon("pin", size=ICON_SIZE_COMPACT), "Pin File")
                pin_action.triggered.connect(lambda: self.pin_file(path))
            menu.addSeparator()
        menu.addAction("Close Tab", lambda: self.close_tab(index))
        menu.exec(self.tabs.mapToGlobal(pos))

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
            self._wire_editor(editor)
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
        path, _ = QFileDialog.getOpenFileName(self, "Open File", "", self.FILE_FILTER)
        if not path:
            return
        if self.switch_to_tab_if_open(path):
            return
        try:
            editor = create_viewer_widget(path)
            self._wire_editor(editor)
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
            self._wire_editor(editor)
            save_recent_file(path)
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
            
        current_ext = ".txt"
        idx = self.tabs.indexOf(editor)
        if idx >= 0:
            title = self.tabs.tabText(idx).replace("*", "")
            ext = os.path.splitext(title)[1]
            if ext: current_ext = ext
            
        from markdown_renderer import MarkdownViewer
        from docx_viewer import DocxViewer
        from xlsx_viewer import XlsxViewer
        if isinstance(editor, MarkdownViewer):
            current_ext = ".html" if getattr(editor, "is_html", False) else ".md"
        elif isinstance(editor, DocxViewer): current_ext = ".docx"
        elif isinstance(editor, XlsxViewer): current_ext = ".xlsx"

        suggested_name = f"Untitled{current_ext}"
        if hasattr(editor, "toPlainText"):
            text = editor.toPlainText()
            if text:
                import re
                first_line = text.split("\n")[0].strip()
                first_line = re.sub(r'^#{1,6}\s+', '', first_line)
                first_line = re.sub(r'<[^>]+>', '', first_line)
                if first_line and len(first_line) < 100:
                    suggested_name = "".join(c for c in first_line if c.isalnum() or c in " -_") + current_ext

        default_folder = load_settings().get("default_save_folder", "")
        if not default_folder or not os.path.isdir(default_folder):
            default_folder = os.getcwd()

        initial_path = os.path.join(default_folder, suggested_name)
        
        ext_to_filter = {
            ".md": "Markdown (*.md)",
            ".html": "HTML (*.html *.htm)",
            ".htm": "HTML (*.html *.htm)",
            ".txt": "Text (*.txt)",
            ".docx": "Word (*.docx)",
            ".xlsx": "Excel (*.xlsx)",
            ".csv": "CSV (*.csv)"
        }
        selected_filter = ext_to_filter.get(current_ext, self.FILE_FILTER.split(";;")[0])
        
        path, _ = QFileDialog.getSaveFileName(
            self, "Save As", initial_path,
            self.FILE_FILTER, selected_filter
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
            action = QAction(self._elide_menu_label(path), self)
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
            action = QAction(self._elide_menu_label(path), self)
            action.setToolTip(path)
            action.triggered.connect(lambda checked=False, p=path: self.open_recent_file(p))
            self.pinned_menu.addAction(action)

    def update_bookmarks_menu(self):
        self.bookmarks_menu.clear()
        bookmarks = load_bookmarks()
        if not bookmarks:
            self.bookmarks_menu.addAction("(no bookmarks)")
            return
        for bookmark in bookmarks[:15]:
            label = bookmark.get("label", "Bookmark")
            path = bookmark.get("file_path", "")
            action = QAction(self._elide_menu_label(label) if len(label) > 36 else label, self)
            action.setToolTip(path)
            action.triggered.connect(
                lambda checked=False, b=bookmark: self._navigate_to_bookmark(b),
            )
            self.bookmarks_menu.addAction(action)
        self.bookmarks_menu.addSeparator()
        self.bookmarks_menu.addAction("Toggle Bookmarks Panel", self.toggle_bookmarks_panel)



    def open_web_tab(self):
        if not WEB_AVAILABLE:
            QMessageBox.warning(self, "Missing Module", "QtWebEngine not installed.")
            return

        # Toggle: if the web dock already exists, show/hide it
        if self._web_dock is not None:
            vis = self._web_dock.isVisible()
            self._web_dock.setVisible(not vis)
            return

        # First time: create as a dockable side panel (matches site's
        # "side-by-side" promise — the web panel is NOT a tab)
        web_panel = WebPanel()
        self._web_dock = QDockWidget("Web Browser", self)
        self._web_dock.setWidget(web_panel)
        self._web_dock.setMinimumWidth(360)
        self._web_dock.setFeatures(
            QDockWidget.DockWidgetClosable
            | QDockWidget.DockWidgetMovable
            | QDockWidget.DockWidgetFloatable
        )
        self.addDockWidget(Qt.RightDockWidgetArea, self._web_dock)

    def show_find(self):
        editor = self.current_editor()
        if hasattr(editor, "find_text"):
            self.find_replace_panel.show()
            self.find_replace_panel.focus_find()

    def show_replace(self):
        editor = self.current_editor()
        if hasattr(editor, "replace_text"):
            self.find_replace_panel.show()
            self.find_replace_panel.focus_replace()

    def _on_find_next(self, text, match_case, whole_word, forward):
        editor = self.current_editor()
        if hasattr(editor, "find_text"):
            found = editor.find_text(text, match_case, whole_word, forward)
            if not found:
                self.show_status_message(f"Cannot find '{text}'", 2000)

    def _on_replace(self, find_text, replace_text, match_case, whole_word):
        editor = self.current_editor()
        if hasattr(editor, "replace_text"):
            editor.replace_text(find_text, replace_text, match_case, whole_word)

    def _on_replace_all(self, find_text, replace_text, match_case, whole_word):
        editor = self.current_editor()
        if hasattr(editor, "replace_all"):
            count = editor.replace_all(find_text, replace_text, match_case, whole_word)
            self.show_status_message(f"Replaced {count} occurrences.", 3000)

