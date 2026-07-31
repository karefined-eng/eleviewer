from PySide6.QtWidgets import (
    QMainWindow, QTabWidget, QFileDialog, QMessageBox,
    QSplitter, QMenu, QToolBar, QToolButton, QVBoxLayout, QHBoxLayout, QWidget,
    QDockWidget, QLabel, QSystemTrayIcon, QApplication, QScrollBar,
)
from PySide6.QtGui import QAction, QKeySequence, QShortcut, QIcon, QFontMetrics, QDrag
from PySide6.QtCore import Qt, QSize, QTimer, Slot, QUrl, Signal, QEvent, QMimeData
import os
import sys

APP_VERSION = "1.3.0"

from editor import EditorTab
from bookmark_manager import add_bookmark, load_bookmarks
from bookmark_panel import BookmarkPanel
from find_replace import FindReplaceWidget

WEB_AVAILABLE = True

from file_handler import (
    create_viewer_widget, get_file_content, get_file_extension, is_binary_format,
)
from recent_files import load_recent_files, save_recent_file
from pinned_files import load_pinned_files, save_pinned_file, remove_pinned_file, is_pinned
from session_manager import load_session, save_session, clear_session
from quick_switcher import QuickSwitcher
from settings import load_settings, save_settings, DEFAULT_SETTINGS
from theme import (
    main_window_stylesheet, ICON_SIZE_TOOLBAR, ICON_SIZE_COMPACT,
    BRAND_PRIMARY, BRAND_PANEL_2, compact_toolbar_stylesheet
)
from save_utils import atomic_write
from icons import icon
from vault_explorer import VaultExplorer
from branding_logo import create_eleviewer_icon, create_eleviewer_pixmap
from file_handler import get_file_extension
from tts_reader_bar import TtsReaderBar
from tts_engine import TtsEngine


# ── File-type icon helper ───────────────────────────────────────────
_TAB_ICON_MAP = {
    "md": "book-open",
    "txt": "type",
    "csv": "table",
    "pdf": "book-open",
    "docx": "file-plus",
    "xlsx": "table",
    "pptx": "monitor",
    "html": "globe",
    "htm": "globe",
}


def _tab_icon_for(path_or_name, active=False):
    """Return a small QIcon appropriate for the file extension or filename."""
    from file_icons import file_type_icon
    if not path_or_name:
        return file_type_icon(".txt", size=18, active=active)
    if path_or_name.startswith("."):
        ext = path_or_name.lower()
    else:
        ext = os.path.splitext(path_or_name)[1].lower()
    return file_type_icon(ext or ".txt", size=18, active=active)


class DraggableToolBar(QToolBar):
    order_changed = Signal(list)
    hidden_changed = Signal(list)

    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.setAcceptDrops(True)
        self._drag_action = None
        self._action_ids = {} # action -> id string
        self._id_actions = {} # id string -> action
        self._drop_indicator_x = -1
        
    def register_action(self, action_id, action):
        self._action_ids[action] = action_id
        self._id_actions[action_id] = action
        
    def add_action_by_id(self, action_id):
        action = self._id_actions.get(action_id)
        if action:
            self.addAction(action)
            widget = self.widgetForAction(action)
            if widget:
                widget.installEventFilter(self)

    def get_order(self):
        return [self._action_ids[a] for a in self.actions() if a in self._action_ids]
        
    def get_hidden(self):
        return [aid for aid, action in self._id_actions.items() if action not in self.actions()]

    def registered_action_ids(self):
        return list(self._id_actions.keys())

    def _insertion_index_at(self, x):
        """Return (index, insert-before-action) for the drop position x.
        
        Walks visible action widgets left-to-right. If x is left of a
        widget's horizontal midpoint we insert *before* that action;
        otherwise we continue. If x is past all widgets we append (None).
        """
        actions = self.actions()
        for i, action in enumerate(actions):
            w = self.widgetForAction(action)
            if not w or not w.isVisible():
                continue
            mid = w.x() + w.width() // 2
            if x < mid:
                return i, action
        return len(actions), None

    def _indicator_x_at(self, pos_x):
        """Return the x-pixel for the drop indicator line."""
        idx, before_action = self._insertion_index_at(pos_x)
        if before_action:
            w = self.widgetForAction(before_action)
            return w.x() - 1 if w else -1
        # Past all widgets   right edge of last visible widget
        for action in reversed(self.actions()):
            w = self.widgetForAction(action)
            if w and w.isVisible():
                return w.x() + w.width()
        return -1

    def eventFilter(self, obj, event):
        if isinstance(obj, QToolButton):
            if event.type() == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
                self._drag_start_pos = event.pos()
                return False
            elif event.type() == QEvent.MouseMove and (event.buttons() & Qt.LeftButton):
                if hasattr(self, '_drag_start_pos') and (event.pos() - self._drag_start_pos).manhattanLength() > QApplication.startDragDistance():
                    action = obj.defaultAction()
                    if action:
                        self._start_drag(action, obj)
                        return True
        return super().eventFilter(obj, event)
        
    def contextMenuEvent(self, event):
        from PySide6.QtWidgets import QMenu
        menu = QMenu(self)
        menu.setStyleSheet("QMenu { border-radius: 6px; padding: 4px; }")
        
        # Add toggles for all registered actions
        for action_id, action in self._id_actions.items():
            toggle_action = menu.addAction(action.text() or action_id.capitalize())
            toggle_action.setCheckable(True)
            # A registered action is considered "enabled" in the toolbar if it is in self.actions()
            toggle_action.setChecked(action in self.actions())
            toggle_action.toggled.connect(lambda checked, a_id=action_id: self._toggle_action_visibility(a_id, checked))
            
        menu.exec_(event.globalPos())
        
    def _toggle_action_visibility(self, action_id, visible):
        action = self._id_actions.get(action_id)
        if not action:
            return
            
        if visible and action not in self.actions():
            # Add it back to the end
            self.add_action_by_id(action_id)
            self.order_changed.emit(self.get_order())
            self.hidden_changed.emit(self.get_hidden())
        elif not visible and action in self.actions():
            self.removeAction(action)
            self.order_changed.emit(self.get_order())
            self.hidden_changed.emit(self.get_hidden())

    def _start_drag(self, action, widget):
        self._drag_action = action
        drag = QDrag(self)
        mime = QMimeData()
        mime.setText(self._action_ids.get(action, ""))
        drag.setMimeData(mime)
        drag.setPixmap(widget.grab())
        drag.exec(Qt.MoveAction)
        self._drag_action = None
        self._drop_indicator_x = -1
        self.update()
        
    def dragEnterEvent(self, event):
        if event.mimeData().hasText() and event.mimeData().text() in self._id_actions:
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasText() and event.mimeData().text() in self._id_actions:
            event.acceptProposedAction()
            new_x = self._indicator_x_at(event.pos().x())
            if new_x != self._drop_indicator_x:
                self._drop_indicator_x = new_x
                self.update()

    def dragLeaveEvent(self, event):
        self._drop_indicator_x = -1
        self.update()
        super().dragLeaveEvent(event)

    def dropEvent(self, event):
        _idx, before_action = self._insertion_index_at(event.pos().x())

        if self._drag_action and self._drag_action != before_action:
            self.removeAction(self._drag_action)
            if before_action:
                self.insertAction(before_action, self._drag_action)
            else:
                self.addAction(self._drag_action)
            self.order_changed.emit(self.get_order())

        self._drop_indicator_x = -1
        self.update()
        event.acceptProposedAction()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self._drop_indicator_x < 0:
            return
        from PySide6.QtGui import QPainter, QPen, QColor
        from theme import get_active_accent
        
        painter = QPainter(self)
        try:
            pen = QPen(QColor(get_active_accent().get("accent", "#6cb6ff")), 2)
            painter.setPen(pen)
            painter.drawLine(self._drop_indicator_x, 4, self._drop_indicator_x, self.height() - 4)
        except Exception as e:
            import logging
            logging.error(f"Error drawing drag indicator: {e}")
        finally:
            painter.end()


class MainWindow(QMainWindow):

    FILE_FILTER = (
        "All Supported (*.md *.txt *.docx *.xlsx *.pptx *.pdf *.csv *.html *.htm);;"
        "PowerPoint (*.pptx);;Word (*.docx);;Excel (*.xlsx);;PDF (*.pdf);;"
        "Markdown (*.md);;HTML (*.html *.htm);;Text (*.txt);;CSV (*.csv)"
    )

    def __init__(self):
        super().__init__()
        self.autosaver = None
        self.closed_tabs = []
        self.vault_panel = None
        self._web_dock = None
        self.bookmarks_panel = None
        self.tts_engine = TtsEngine()

        self.setWindowTitle(f"EleViewer — Untitled")
        self.setWindowIcon(create_eleviewer_icon(64))
        self.resize(1200, 800)
        self.setStyleSheet(main_window_stylesheet())
        self._setup_status_bar()

        self._build_layout()
        self._build_toolbar()
        self.create_menu()
        self._setup_global_shortcuts()
        self._restore_vault()
        from settings import load_settings
        settings = load_settings()
        if settings.get("restore_session_tabs", True):
            self.restore_session()
        else:
            self._new_session()

        if self.tabs.count() == 0:
            from settings import load_settings
            behavior = load_settings().get("fresh_session_behavior", "welcome")
            if behavior == "welcome":
                self.tabs.addTab(self._create_welcome_widget(), "Welcome")
            elif behavior == "blank_tab":
                self.new_tab()
            # if 'empty', do nothing

        self.tabs.currentChanged.connect(self.update_status_bar)
        self.update_status_bar()
        self._check_for_updates_async()
        
        # Global Esc shortcut for closing popups and sidebars
        self.esc_shortcut = QShortcut(QKeySequence(Qt.Key_Escape), self)
        self.esc_shortcut.activated.connect(self.handle_escape)

        # Register global URL handlers so links in PDFs, Markdown, HTML, What's New, etc. open in EleViewer instead of external browser!
        from PySide6.QtGui import QDesktopServices
        QDesktopServices.setUrlHandler("http", self, "handle_url")
        QDesktopServices.setUrlHandler("https", self, "handle_url")
        QDesktopServices.setUrlHandler("file", self, "handle_url")

        # IMPROVEMENT: system tray minimization with restore on double-click
        self.tray_icon = QSystemTrayIcon(create_eleviewer_icon(32), self)
        tray_menu = QMenu()
        tray_menu.addAction("Open EleViewer", self.show_and_raise)
        tray_menu.addAction("Quit", QApplication.quit)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self._on_tray_activated)
        self.tray_icon.show()
        self._register_system_wide_hotkey()

    def _register_system_wide_hotkey(self):
        """Register Alt+E system-wide Windows hotkey to bring EleViewer to front and open a new note."""
        if sys.platform != "win32":
            return
        try:
            import ctypes
            self._hotkey_id = 0x454C  # 'EL'
            MOD_ALT = 0x0001
            VK_E = 0x45
            hwnd = int(self.winId())
            ctypes.windll.user32.RegisterHotKey(hwnd, self._hotkey_id, MOD_ALT, VK_E)
        except Exception:
            pass

    def nativeEvent(self, eventType, message):
        """Catch Windows native WM_HOTKEY events (Alt+E) anywhere on the system."""
        if sys.platform == "win32" and eventType == b"windows_generic_MSG":
            try:
                import ctypes
                import ctypes.wintypes
                msg = ctypes.wintypes.MSG.from_address(int(message))
                WM_HOTKEY = 0x0312
                if msg.message == WM_HOTKEY and getattr(msg, "wParam", None) == getattr(self, "_hotkey_id", 0x454C):
                    self.bring_to_front_and_new_note()
                    return True, 0
            except Exception:
                pass
        return super().nativeEvent(eventType, message)

    def show_and_raise(self):
        self.showNormal()
        self.show()
        self.raise_()
        self.activateWindow()

    def bring_to_front_and_new_note(self):
        """Brings EleViewer to the foreground and opens a new scratchpad .txt document."""
        self.show_and_raise()
        self.new_tab()

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_and_raise()
        elif reason == QSystemTrayIcon.Trigger:
            # Show context menu on single left-click
            from PySide6.QtGui import QCursor
            self.tray_icon.contextMenu().popup(QCursor.pos())

    # FIX: guard prevents ESC double-fire when modal dialog is active
    def handle_escape(self):
        if QApplication.activeModalWidget() is not None:
            return
            
        if getattr(self, "_zen_mode_active", False):
            self.toggle_zen_mode()
            return

        # Hide Find/Replace if open in current editor
        current_widget = self.tabs.currentWidget()
        if current_widget:
            fr = getattr(current_widget, "find_replace_widget", None)
            if fr and fr.isVisible():
                fr.hide_panel()
                return

        # Hide Vault Sidebar if open
        if self.vault_panel and self.vault_panel.isVisible():
            self.vault_panel.hide()
            return
            
        # Hide Bookmarks Sidebar if open
        if self.bookmarks_panel and self.bookmarks_panel.isVisible():
            self.bookmarks_panel.hide()
            return

        # Hide global Find/Replace panel if visible
        if hasattr(self, "find_replace_panel") and self.find_replace_panel.isVisible():
            self.find_replace_panel.hide()
            return

        # Collapse TTS reader bar if visible
        if hasattr(self, "tts_bar") and self.tts_bar.isVisible():
            self.tts_bar.hide()
            return

    def keyPressEvent(self, event):
        """Override to guarantee Esc is processed by the MainWindow layer stack,
        even when a QWebEngineView or other child widget has keyboard focus."""
        if event.key() == Qt.Key_Escape:
            self.handle_escape()
            event.accept()
        else:
            super().keyPressEvent(event)

    def _check_for_updates_async(self):
        try:
            from updater import CheckUpdateThread
            self._update_thread = CheckUpdateThread(current_version=APP_VERSION, parent=self)
            self._update_thread.update_available.connect(self._on_update_found)
            self._update_thread.start()
        except Exception:
            pass

    def _on_update_found(self, tag_name, release_notes, download_url):
        from updater import UpdateDialog
        dlg = UpdateDialog(tag_name, release_notes, download_url, self)
        dlg.exec()

    def check_for_updates_manual(self):
        try:
            self.show_status_message("Checking for updates...", 3000)
            from updater import CheckUpdateThread
            self._manual_update_thread = CheckUpdateThread(current_version=APP_VERSION, parent=self)
            self._manual_update_thread.update_available.connect(self._on_update_found)
            
            def on_no_update():
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.information(self, "Up to Date", f"You are running the latest version of EleViewer (v{APP_VERSION}).")
            
            def on_error(err):
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Update Check Failed", f"Could not check for updates:\n{err}")

            self._manual_update_thread.no_update.connect(on_no_update)
            self._manual_update_thread.error_occurred.connect(on_error)
            self._manual_update_thread.start()
        except Exception:
            self.show_status_message("Update check failed.", 3000)


    def _setup_status_bar(self):
        status_bar = self.statusBar()
        status_bar.setSizeGripEnabled(False)
        
        from theme import get_active_palette
        p = get_active_palette()

        self.status_left = QLabel("0 tabs · session saved")
        self.status_left.setStyleSheet(f"color: {p['BRAND_MUTED_FG']}; font-family: monospace; font-size: 11px; padding-left: 8px;")

        self.status_center = QLabel("Ctrl+Q quick switch · Alt+V vault")
        self.status_center.setStyleSheet(f"color: {p['BRAND_MUTED_FG']}; font-family: monospace; font-size: 11px;")
        self.status_center.setAlignment(Qt.AlignCenter)

        self.status_right = QLabel("md · UTF-8")
        self.status_right.setStyleSheet(f"color: {p['BRAND_MUTED_FG']}; font-family: monospace; font-size: 11px; padding-right: 12px;")

        status_bar.addWidget(self.status_left)
        status_bar.addWidget(self.status_center, 1)
        status_bar.addPermanentWidget(self.status_right)

        self.shortcut_hints = [
            "Ctrl+Q quick switch",
            "Alt+V toggle vault",
            "Ctrl+T web browser",
            "Ctrl+D bookmark page",
            "Ctrl+Shift+F search vault",
            "Ctrl+Shift+T reopen tab",
        ]
        self.shortcut_index = 0
        self.shortcut_timer = QTimer(self)
        self.shortcut_timer.timeout.connect(self._rotate_shortcuts)
        self.shortcut_timer.start(4000)
        self._rotate_shortcuts()

    def _rotate_shortcuts(self):
        self.shortcut_index = (self.shortcut_index + 1) % len(self.shortcut_hints)
        next_idx = (self.shortcut_index + 1) % len(self.shortcut_hints)
        full_text = f"{self.shortcut_hints[self.shortcut_index]}  ·  {self.shortcut_hints[next_idx]}"
        # Elide center text so it never overlaps the right-side indicators on narrow windows
        fm = self.status_center.fontMetrics()
        available_w = max(200, self.width() - 320)  # 320px reserved for left + right labels
        elided = fm.elidedText(full_text, Qt.ElideRight, available_w)
        self.status_center.setText(elided)

    def _build_layout(self):
        self.main_splitter = QSplitter(Qt.Horizontal)

        self.vault_panel = VaultExplorer()
        self.vault_panel.setMinimumWidth(180)
        self.vault_panel.setMaximumWidth(420)
        self.vault_panel.file_opened.connect(self._open_vault_file)
        self.vault_panel.btn_add.clicked.connect(self.add_vault)
        self.main_splitter.addWidget(self.vault_panel)

        self.editor_tabs_splitter = QSplitter(Qt.Horizontal)
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setDocumentMode(True)
        self.tabs.setMovable(True)
        self.tabs.tabBar().installEventFilter(self)
        self.tabs.tabBar().setMovable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tabs.customContextMenuRequested.connect(self.show_tab_context_menu)
        
        self.tabs_right = QTabWidget()
        self.tabs_right.setTabsClosable(True)
        self.tabs_right.setDocumentMode(True)
        self.tabs_right.tabBar().setMovable(True)
        self.tabs_right.tabCloseRequested.connect(lambda i: self._close_tab_in_widget(self.tabs_right, i))
        self.tabs_right.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tabs_right.customContextMenuRequested.connect(lambda pos: self.show_tab_context_menu(pos, self.tabs_right))
        self.tabs_right.currentChanged.connect(self.update_status_bar)
        self.tabs_right.hide()
        
        self.editor_tabs_splitter.addWidget(self.tabs)
        self.editor_tabs_splitter.addWidget(self.tabs_right)
        
        self.find_replace_panel = FindReplaceWidget()
        self.find_replace_panel.hide()
        self.find_replace_panel.find_next_requested.connect(self._on_find_next)
        self.find_replace_panel.replace_requested.connect(self._on_replace)
        self.find_replace_panel.replace_all_requested.connect(self._on_replace_all)

        self.tts_bar = TtsReaderBar()
        self.tts_bar.hide()
        self.tts_bar.populate_voices(self.tts_engine.list_voices())
        self.tts_bar.speak_requested.connect(self._speak_current_tab)
        self.tts_bar.stop_requested.connect(self._stop_tts)
        self.tts_bar.voice_changed.connect(lambda vid: self._speak_current_tab())

        editor_layout = QVBoxLayout()
        editor_layout.setContentsMargins(0, 0, 0, 0)
        editor_layout.setSpacing(0)
        editor_layout.addWidget(self.editor_tabs_splitter)
        editor_layout.addWidget(self.find_replace_panel)
        editor_layout.addWidget(self.tts_bar)
        
        editor_container = QWidget()
        editor_container.setLayout(editor_layout)
        
        self.editor_splitter = QSplitter(Qt.Horizontal)
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
        self.vault_panel.search_requested.connect(self.open_vault_search)

        self.setCentralWidget(self.main_splitter)

        for i in range(1, 10):
            QShortcut(QKeySequence(f"Ctrl+{i}"), self).activated.connect(
                lambda idx=i-1: self.tabs.setCurrentIndex(min(idx, self.tabs.count()-1)) if self.tabs.count() > 0 else None
            )

    def apply_theme(self):
        self.setStyleSheet(main_window_stylesheet())
        self._setup_status_bar()
        self.create_menu()
        if self.vault_panel and hasattr(self.vault_panel, "reload_theme"):
            self.vault_panel.reload_theme()
        if self.bookmarks_panel and hasattr(self.bookmarks_panel, "reload_theme"):
            self.bookmarks_panel.reload_theme()
        if hasattr(self, "tabs"):
            for i in range(self.tabs.count()):
                w = self.tabs.widget(i)
                if hasattr(w, "reload_theme"):
                    w.reload_theme()

    def _build_toolbar(self):
        self.toolbar = DraggableToolBar("Main Toolbar")
        self.toolbar.setMovable(False)
        self.toolbar.setIconSize(QSize(ICON_SIZE_COMPACT, ICON_SIZE_COMPACT))
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.addToolBar(self.toolbar)

        new_file_action = QAction(icon("file-plus", size=ICON_SIZE_TOOLBAR), "New File", self)
        new_file_action.setToolTip("New File")
        new_file_action.triggered.connect(self._show_new_file_menu_from_toolbar)
        self.toolbar.register_action("new", new_file_action)

        vault_btn = QAction(icon("panel-left", size=ICON_SIZE_TOOLBAR), "Toggle Vault", self)
        vault_btn.setToolTip("Toggle Vault (Alt+V)")
        vault_btn.setShortcut("Alt+V")
        vault_btn.setShortcutContext(Qt.WidgetShortcut)
        vault_btn.triggered.connect(self.toggle_vault_panel)
        self.toolbar.register_action("vault", vault_btn)

        bookmark_btn = QAction(icon("bookmark", size=ICON_SIZE_TOOLBAR), "Bookmarks", self)
        bookmark_btn.setToolTip("Toggle Bookmarks Panel (Ctrl+Alt+B)")
        bookmark_btn.setShortcut("Ctrl+Alt+B")
        bookmark_btn.setShortcutContext(Qt.WidgetShortcut)
        bookmark_btn.triggered.connect(self.toggle_bookmarks_panel)
        self.toolbar.register_action("bookmarks", bookmark_btn)

        open_btn = QAction(icon("folder-open", size=ICON_SIZE_TOOLBAR), "Open", self)
        open_btn.setToolTip("Open File (Ctrl+O)")
        open_btn.setShortcut("Ctrl+O")
        open_btn.setShortcutContext(Qt.WidgetShortcut)
        open_btn.triggered.connect(self.open_file)
        self.toolbar.register_action("open", open_btn)

        save_btn = QAction(icon("save", size=ICON_SIZE_TOOLBAR), "Save", self)
        save_btn.setToolTip("Save File (Ctrl+S)")
        save_btn.setShortcut("Ctrl+S")
        save_btn.setShortcutContext(Qt.WidgetShortcut)
        save_btn.triggered.connect(self.save_file)
        self.toolbar.register_action("save", save_btn)
        
        tts_btn = QAction(icon("volume-2", size=ICON_SIZE_TOOLBAR), "Read Aloud", self)
        tts_btn.setToolTip("Read Aloud / Toggle TTS (F9)")
        tts_btn.setShortcut("F9")
        tts_btn.setShortcutContext(Qt.WidgetShortcut)
        tts_btn.triggered.connect(self.toggle_tts_bar)
        self.toolbar.register_action("tts", tts_btn)

        if WEB_AVAILABLE:
            web_btn = QAction(icon("globe", size=ICON_SIZE_TOOLBAR), "Web Panel", self)
            web_btn.setToolTip("Open Web Browser Panel / New Web Tab (Ctrl+T)")
            web_btn.triggered.connect(self.open_web_tab)
            self.toolbar.register_action("web", web_btn)

        settings_btn = QAction(icon("settings", size=ICON_SIZE_TOOLBAR), "Settings", self)
        settings_btn.setToolTip("Settings")
        settings_btn.triggered.connect(self.open_settings)
        self.toolbar.register_action("settings", settings_btn)

        settings_data = load_settings()
        toolbar_order = settings_data.get("toolbar_order")
        if not isinstance(toolbar_order, list):
            toolbar_order = DEFAULT_SETTINGS["toolbar_order"]
            
        toolbar_hidden = settings_data.get("toolbar_hidden")
        if not isinstance(toolbar_hidden, list):
            toolbar_hidden = DEFAULT_SETTINGS.get("toolbar_hidden", [])

        # Add actions in the saved order
        for action_id in toolbar_order:
            if action_id == "web" and not WEB_AVAILABLE:
                continue
            if action_id not in toolbar_hidden:
                self.toolbar.add_action_by_id(action_id)
            
        # Add any remaining actions that are registered but missing from the saved order (and not hidden)
        for action_id in self.toolbar.registered_action_ids():
            if action_id not in toolbar_order and action_id not in toolbar_hidden:
                if action_id == "web" and not WEB_AVAILABLE:
                    continue
                self.toolbar.add_action_by_id(action_id)

        # Connect the signal to save the order when changed
        def save_order(new_order):
            s = load_settings()
            s["toolbar_order"] = new_order
            save_settings(s)
            
        def save_hidden(new_hidden):
            s = load_settings()
            s["toolbar_hidden"] = new_hidden
            save_settings(s)
            
        self.toolbar.order_changed.connect(save_order)
        self.toolbar.hidden_changed.connect(save_hidden)

    def _add_menu_action(self, menu, text, slot, shortcut=None):
        action = QAction(text, self)
        if shortcut:
            action.setShortcut(shortcut)
            action.setShortcutContext(Qt.WidgetShortcut)
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
        self._add_menu_action(menu, "Reopen Closed Tab", self.reopen_closed_tab, "Ctrl+Shift+T")
        self._add_menu_action(menu, "Quick Switcher", self.open_quick_switcher, "Ctrl+Q")
        menu.addSeparator()
        self._add_menu_action(menu, "Settings...", self.open_settings, "Alt+S")
        return menu

    def _setup_global_shortcuts(self):
        from PySide6.QtGui import QShortcut, QKeySequence
        from PySide6.QtCore import Qt

        # Create global ApplicationShortcut instances for all Reflex Keys and common actions
        # so they trigger reliably regardless of which child widget has focus — including
        # when a QWebEngineView (Chromium) has captured keyboard focus.
        shortcuts = [
            ("Escape", self.handle_escape),
            ("Alt+E", self.bring_to_front_and_new_note),
            ("Alt+V", self.toggle_vault_panel),
            ("Ctrl+Q", self.open_quick_switcher),
            ("Ctrl+T", self.open_web_tab),
            ("Ctrl+Shift+T", self.reopen_closed_tab),
            ("F9", self.toggle_tts_bar),
            ("F11", self.toggle_zen_mode),
            ("Ctrl+N", self.new_tab),
            ("Ctrl+O", self.open_file),
            ("Ctrl+S", self.save_file),
            ("Ctrl+Shift+S", self.save_file_as),
            ("Ctrl+W", self.close_current_tab),
            ("Ctrl+F", self.show_find),
            ("Ctrl+H", self.show_replace),
            ("Ctrl+Shift+F", self.open_vault_search),
            ("Alt+S", self.open_settings),
        ]
        for key_seq, slot in shortcuts:
            sc = QShortcut(QKeySequence(key_seq), self)
            sc.setContext(Qt.ApplicationShortcut)
            sc.activated.connect(slot)

    def toggle_zen_mode(self):
        if not hasattr(self, "_zen_mode_active"):
            self._zen_mode_active = False
            
        self._zen_mode_active = not self._zen_mode_active
        if self._zen_mode_active:
            self.showFullScreen()
            self.toolbar.hide()
            self._zen_vault_was_visible = self.vault_panel.isVisible()
            if self._zen_vault_was_visible:
                self.vault_panel.hide()
            self.statusBar().hide()
            self.show_status_message("Zen Mode active. Press F11 or Esc to exit.", 3000)
        else:
            self.showNormal()
            self.toolbar.show()
            if getattr(self, "_zen_vault_was_visible", False):
                self.vault_panel.show()
            self.statusBar().show()

    def _restore_vault(self):
        settings = load_settings()
        self.vault_panel.set_show_all_files(settings.get("vault_show_all_files", False))
        self.vault_panel.restore_from_settings()

    def start_onboarding(self):
        from onboarding import InteractiveWelcomeWidget
        self.onboarding_widget = InteractiveWelcomeWidget(self)
        self.onboarding_widget.close_requested.connect(self._close_onboarding)
        idx = self.tabs.addTab(self.onboarding_widget, "Welcome")
        self.tabs.setCurrentIndex(idx)
        
    def _close_onboarding(self):
        if hasattr(self, "onboarding_widget"):
            idx = self.tabs.indexOf(self.onboarding_widget)
            if idx >= 0:
                self.tabs.removeTab(idx)

    def toggle_vault_panel(self):
        is_visible = not self.vault_panel.isVisible()
        self.vault_panel.setVisible(is_visible)
        if is_visible and hasattr(self, "onboarding_widget"):
            self.onboarding_widget.check_off("vault")
        if not is_visible:
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
        if not path:
            return
        if str(path).lower().startswith(("http://", "https://", "file://")):
            if not self._web_dock or not self._web_dock.isVisible():
                self.toggle_web_panel()
            if self._web_dock and self._web_dock.widget():
                self._web_dock.widget().open_url_in_new_tab(path, bookmark.get("label", "Bookmarked Page"))
            self.show_status_message(f"Opened web bookmark: {bookmark.get('label', '')}", 2000)
            return
        if not os.path.exists(path):
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

    def bookmark_current_tab(self):
        from PySide6.QtWidgets import QApplication
        focus_w = QApplication.focusWidget()
        if self._web_dock and self._web_dock.isVisible() and focus_w and (self._web_dock.isAncestorOf(focus_w) or focus_w == self._web_dock):
            self._web_dock.widget()._bookmark_current()
            return
        editor = self.current_editor()
        if not editor:
            return
        if hasattr(editor, "_add_bookmark_here"):
            editor._add_bookmark_here()
        else:
            self.show_status_message("Current file cannot be bookmarked", 3000)

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

    def open_feedback_dialog(self):
        from feedback_dialog import FeedbackDialog
        dlg = FeedbackDialog(self)
        dlg.exec()

    def open_review_page(self):
        if not WEB_AVAILABLE:
            from PySide6.QtGui import QDesktopServices
            from PySide6.QtCore import QUrl
            QDesktopServices.openUrl(QUrl("https://eleviewer.vercel.app/review"))
            return

        if self._web_dock is None:
            self.open_web_tab()
            
        if not self._web_dock.isVisible():
            self._web_dock.setVisible(True)
            
        # Add the specific URL as a new tab in the web panel
        self._web_dock.widget()._add_tab_widget("https://eleviewer.vercel.app/review", "Leave a Review")

    def open_getting_started(self):
        from paths import BASE_DIR
        welcome_file = BASE_DIR / "getting_started" / "Welcome to EleViewer.md"
        if welcome_file.exists():
            self._open_vault_file(str(welcome_file))
        else:
            self.show_status_message("Getting Started guide not found", 3000)

    def show_status_message(self, message, timeout_ms=0):
        self.statusBar().showMessage(message, timeout_ms)

    def update_status_bar(self):
        self._refresh_tab_icons()
        editor = self.current_editor()
        if not editor:
            self.setWindowTitle(f"EleViewer v{APP_VERSION}")
            self.status_left.setText("Ready")
            self.status_right.setText("UTF-8")
            return
        path = getattr(editor, "file_path", None)
        name = os.path.basename(path) if path else "Untitled"

        self.setWindowTitle(f"EleViewer — {name}")

        tab_count = self.tabs.count()
        ext = get_file_extension(path) if path else ""
        ext_label = ext.upper() if ext else "TXT"
        
        parts = [f"{tab_count} tab{'s' if tab_count != 1 else ''}"]
        
        # Add Line/Col numbers if the editor has a textCursor
        cursor_info = ""
        try:
            if hasattr(editor, "editor") and hasattr(editor.editor, "textCursor"):
                cursor = editor.editor.textCursor()
                cursor_info = f"Ln {cursor.blockNumber() + 1}, Col {cursor.columnNumber() + 1}"
            elif hasattr(editor, "get_text_cursor"):
                cursor = editor.get_text_cursor()
                if cursor:
                    cursor_info = f"Ln {cursor.blockNumber() + 1}, Col {cursor.columnNumber() + 1}"
        except Exception:
            pass

        if cursor_info:
            parts.append(cursor_info)

        parts.append("Modified" if getattr(editor, "is_modified", False) else "session saved")
        
        self.status_left.setText(" · ".join(parts))

        # Compute document metric text based on viewer type
        count_text = ""
        widget_type = type(editor).__name__
        if widget_type in ["EditorTab", "DocxViewer", "MarkdownViewer", "HtmlViewer"]:
            if hasattr(editor, "toPlainText"):
                text_content = editor.toPlainText()
                lines = text_content.count('\n') + 1 if text_content else 0
                count_text = f"{lines:,} lines · "
        elif widget_type in ["CsvViewer", "XlsxViewer"]:
            if hasattr(editor, "model"):
                rows = editor.model.rowCount()
                count_text = f"{rows:,} rows · "
        elif widget_type == "PptxViewer":
            if hasattr(editor, "total_slides"):
                count_text = f"{editor.total_slides} slides · "
        elif widget_type == "PdfViewer":
            if hasattr(editor, "document"):
                pages = editor.document.pageCount() if editor.document else 0
                count_text = f"{pages} pages · "

        self.status_right.setText(f"{count_text}{ext_label} · UTF-8")

    def _connect_editor_signals(self, editor):
        if hasattr(editor, "textChanged"):
            editor.textChanged.connect(lambda ed=editor: self._on_editor_changed(ed))
            
        # Hook cursor movement to update line numbers in status bar
        if hasattr(editor, "editor") and hasattr(editor.editor, "cursorPositionChanged"):
            try:
                editor.editor.cursorPositionChanged.connect(self.update_status_bar)
            except TypeError:
                pass
        if hasattr(editor, "pushToBrowserRequested"):
            editor.pushToBrowserRequested.connect(self._on_push_to_browser)

    def _on_push_to_browser(self, file_path, url_str):
        if not WEB_AVAILABLE:
            return
        if self._web_dock is None:
            self.toggle_web_panel()
        elif not self._web_dock.isVisible():
            self.toggle_web_panel()
        web_panel = self._web_dock.widget()
        title = os.path.basename(file_path) if file_path else "Live Feed"
        web_panel.open_url_in_new_tab(url_str, title)

    def _on_editor_changed(self, editor):
        self.update_tab_title(editor)
        self.update_status_bar()

    def _create_welcome_widget(self):
        from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout, QToolButton, QFrame, QLineEdit, QListWidget, QListWidgetItem, QSizePolicy, QScrollArea
        from PySide6.QtCore import Qt, QSize
        from PySide6.QtGui import QPixmap, QIcon
        from theme import get_active_palette, get_brand_accent
        p = get_active_palette()
        from branding_logo import create_eleviewer_pixmap
        from icons import icon
        from recent_files import load_recent_files
        from bookmark_manager import load_bookmarks
        
        w = QWidget()
        w.is_welcome_tab = True
        main_layout = QVBoxLayout(w)
        main_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        main_layout.setContentsMargins(0, 80, 0, 40)
        
        # Max-width container
        container = QWidget()
        container.setMinimumWidth(700)
        container.setMaximumWidth(850)
        c_layout = QVBoxLayout(container)
        c_layout.setSpacing(40)
        c_layout.setAlignment(Qt.AlignTop)
        
        # 1. Hero Section
        hero = QWidget()
        hero_layout = QVBoxLayout(hero)
        hero_layout.setAlignment(Qt.AlignCenter)
        hero_layout.setSpacing(15)
        
        logo_lbl = QLabel()
        logo_lbl.setPixmap(create_eleviewer_pixmap(72))
        logo_lbl.setAlignment(Qt.AlignCenter)
        
        title = QLabel("EleViewer")
        title.setStyleSheet(f"font-size: 34px; font-weight: 800; color: {p['BRAND_PRIMARY']}; letter-spacing: -0.5px;")
        title.setAlignment(Qt.AlignCenter)
        
        hero_layout.addWidget(logo_lbl)
        hero_layout.addWidget(title)
        c_layout.addWidget(hero)
        
        # 2. Premium Omnibar (Search)
        search_btn = QToolButton()
        search_btn.setText("   Search your vault, type a URL, or press 'Ctrl+Q'...")
        search_btn.setIcon(icon("search", size=20, color=p['BRAND_MUTED_FG']))
        search_btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        search_btn.setCursor(Qt.PointingHandCursor)
        search_btn.setStyleSheet(f"""
            QToolButton {{
                background: {p['BRAND_PANEL']};
                color: {p['BRAND_MUTED_FG']};
                border: 1px solid {p['BRAND_BORDER']};
                border-radius: 12px;
                padding: 14px 24px;
                font-size: 15px;
                text-align: left;
            }}
            QToolButton:hover {{
                border: 1px solid {get_brand_accent()};
                background: {p['BRAND_PANEL_2']};
                color: {p['BRAND_PRIMARY']};
            }}
        """)
        search_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        search_btn.clicked.connect(self.open_vault_search)
        c_layout.addWidget(search_btn)
        
        # 3. Two Columns: Activity & Actions
        columns = QWidget()
        cols_layout = QHBoxLayout(columns)
        cols_layout.setSpacing(50)
        cols_layout.setAlignment(Qt.AlignTop)
        
        # LEFT: Activity
        left_col = QWidget()
        left_layout = QVBoxLayout(left_col)
        left_layout.setSpacing(12)
        
        list_style = f"""
            QListWidget {{ background: transparent; border: none; color: {p['BRAND_PRIMARY']}; outline: none; font-size: 14px; }}
            QListWidget::item {{ padding: 10px; border-radius: 6px; color: {p['BRAND_PRIMARY']}; }}
            QListWidget::item:hover {{ background: {p['BRAND_PANEL_2']}; }}
        """
        
        recent_lbl = QLabel("RECENT FILES")
        recent_lbl.setStyleSheet(f"color: {p['BRAND_MUTED_FG']}; font-size: 12px; font-weight: bold; letter-spacing: 1px;")
        left_layout.addWidget(recent_lbl)
        
        recent_list = QListWidget()
        recent_list.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        recent_list.setStyleSheet(list_style)
        recent_list.setSelectionMode(QListWidget.NoSelection)
        recent_list.setCursor(Qt.PointingHandCursor)
        recent_files = load_recent_files(validate=True)[:3]
        if not recent_files:
            recent_list.addItem(QListWidgetItem("No recent files"))
        else:
            for path in recent_files:
                item = QListWidgetItem(icon("book-open", size=16, color=p['BRAND_PRIMARY']), "  " + os.path.basename(path))
                item.setData(Qt.UserRole, path)
                recent_list.addItem(item)
        recent_list.setFixedHeight(min(45 * max(1, len(recent_files)), 150))
        recent_list.itemClicked.connect(lambda it: self._open_vault_file(it.data(Qt.UserRole)) if it.data(Qt.UserRole) else None)
        left_layout.addWidget(recent_list)
        
        bm_lbl = QLabel("BOOKMARKS")
        bm_lbl.setStyleSheet(f"color: {p['BRAND_MUTED_FG']}; font-size: 12px; font-weight: bold; letter-spacing: 1px; margin-top: 15px;")
        left_layout.addWidget(bm_lbl)
        
        bm_list = QListWidget()
        bm_list.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        bm_list.setStyleSheet(list_style)
        bm_list.setSelectionMode(QListWidget.NoSelection)
        bm_list.setCursor(Qt.PointingHandCursor)
        bms = load_bookmarks()[:3]
        if not bms:
            bm_list.addItem(QListWidgetItem("No bookmarks"))
        else:
            for b in bms:
                item = QListWidgetItem(icon("bookmark", size=16, color=p['BRAND_PRIMARY']), "  " + b.get("label", "Bookmark"))
                item.setData(Qt.UserRole, b)
                bm_list.addItem(item)
        bm_list.setFixedHeight(min(45 * max(1, len(bms)), 150))
        
        def _handle_bm(it):
            b = it.data(Qt.UserRole)
            if b:
                self._open_vault_file(b["file_path"])
                ww = self.tabs.currentWidget()
                if hasattr(ww, "go_to_bookmark"): ww.go_to_bookmark(b.get("page_number", 0), b.get("scroll_position_y", 0.0))
        bm_list.itemClicked.connect(_handle_bm)
        left_layout.addWidget(bm_list)
        left_layout.addStretch()
        
        # RIGHT: Actions
        right_col = QWidget()
        right_layout = QVBoxLayout(right_col)
        right_layout.setSpacing(12)
        
        btn_style = f"""
            QToolButton {{
                background: {p['BRAND_PANEL']};
                color: {p['BRAND_PRIMARY']};
                border: 1px solid {p['BRAND_BORDER']};
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                font-weight: 500;
            }}
            QToolButton:hover {{
                background: {p['BRAND_PANEL_2']};
                border: 1px solid {get_brand_accent()};
            }}
        """
        
        btn_note = QToolButton()
        btn_note.setText(" New Text Note")
        btn_note.setIcon(icon("file-plus", size=18, color=p['BRAND_PRIMARY']))
        btn_note.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        btn_note.setStyleSheet(btn_style)
        btn_note.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        btn_note.setCursor(Qt.PointingHandCursor)
        btn_note.clicked.connect(self.new_tab)
        
        btn_web = QToolButton()
        btn_web.setText(" Open Web Browser")
        btn_web.setIcon(icon("globe", size=18, color=p['BRAND_PRIMARY']))
        btn_web.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        btn_web.setStyleSheet(btn_style)
        btn_web.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        btn_web.setCursor(Qt.PointingHandCursor)
        # FIX: Previously connected to new_tab incorrectly
        btn_web.clicked.connect(self.open_web_tab)
        
        right_layout.addWidget(btn_note)
        right_layout.addWidget(btn_web)
        
        # Sleek Shortcuts
        sc_lbl = QLabel("QUICK ACTIONS")
        sc_lbl.setStyleSheet(f"color: {p['BRAND_MUTED_FG']}; font-size: 12px; font-weight: bold; letter-spacing: 1px; margin-top: 15px;")
        right_layout.addWidget(sc_lbl)
        
        shortcuts = [
            ("Ctrl+O", "Open file"),
            ("Alt+V", "Toggle vault"),
            ("F11", "Zen mode")
        ]

        grid = QWidget()
        grid_layout = QGridLayout(grid)
        grid_layout.setSpacing(12)
        grid_layout.setContentsMargins(0, 5, 0, 0)
        for i, (key, desc) in enumerate(shortcuts):
            k_lbl = QLabel(key)
            k_lbl.setStyleSheet(f"background: {p['BRAND_BACKGROUND']}; border: 1px solid {p['BRAND_BORDER']}; padding: 4px 8px; border-radius: 4px; font-family: monospace; color: {get_brand_accent()}; font-size: 12px;")
            d_lbl = QLabel(desc)
            d_lbl.setStyleSheet(f"color: {p['BRAND_MUTED_FG']}; font-size: 13px;")
            grid_layout.addWidget(k_lbl, i, 0)
            grid_layout.addWidget(d_lbl, i, 1)
            
        right_layout.addWidget(grid)
        right_layout.addStretch()
        
        cols_layout.addWidget(left_col, stretch=1)
        cols_layout.addWidget(right_col, stretch=1)
        c_layout.addWidget(columns)
        
        main_layout.addWidget(container)
        main_layout.addStretch()
        return w

    def _replace_welcome_if_present(self):
        if self.tabs.count() == 1:
            w = self.tabs.widget(0)
            if getattr(w, "is_welcome_tab", False):
                self.tabs.removeTab(0)
                w.deleteLater()

    def add_editor_tab(self, widget, label, icon=None):
        """Helper to append an editor tab safely."""
        self._replace_welcome_if_present()
        idx = self.tabs.addTab(widget, icon or QIcon(), label)
        self.tabs.setCurrentIndex(idx)
        return idx

    def _add_editor_tab(self, editor, name):
        self._connect_editor_signals(editor)
        path = getattr(editor, "file_path", None) or name
        tab_icon = _tab_icon_for(path)
        index = self.add_editor_tab(editor, name, tab_icon)
        self.update_status_bar()
        
        self._check_file_load_milestone()
        
        return index

    def new_tab(self):
        self._replace_welcome_if_present()
        from editor import EditorTab
        editor = EditorTab()
        editor.file_path = None
        self._add_editor_tab(editor, "Untitled")

    def _check_file_load_milestone(self):
        settings = load_settings()
        count = settings.get("files_opened", 0) + 1
        settings["files_opened"] = count
        save_settings(settings)
        if count == 5:
            self._show_whatsapp_invite()

    def _show_whatsapp_invite(self):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("EleViewer — Join Nightly Insiders 🚀")
        msg.setText("Enjoying EleViewer?")
        msg.setInformativeText(
            "What is 'Nightly Insiders'?\n\n"
            "It's our official early-access community! As a Nightly Insider, you get:\n"
            "• Bleeding-edge unreleased feature previews\n"
            "• Direct voting on upcoming app updates & features\n"
            "• Instant feedback & chat directly with the developer\n\n"
            "Would you like to join our WhatsApp Insiders group?"
        )
        
        join_btn = msg.addButton("Join Nightly Insiders", QMessageBox.ActionRole)
        msg.addButton("Maybe Later", QMessageBox.RejectRole)
        msg.setDefaultButton(join_btn)
        
        msg.exec()
        
        if msg.clickedButton() == join_btn:
            if WEB_AVAILABLE:
                if self._web_dock is None:
                    self.open_web_tab()
                if not self._web_dock.isVisible():
                    self._web_dock.setVisible(True)
                self._web_dock.widget()._add_tab_widget("https://eleviewer.vercel.app/community", "Nightly Insiders")
            else:
                from PySide6.QtGui import QDesktopServices
                from PySide6.QtCore import QUrl
                QDesktopServices.openUrl(QUrl("https://eleviewer.vercel.app/community"))

    # IMPROVEMENT: system tray minimization with restore on double-click
    def closeEvent(self, event):
        from settings import load_settings, save_settings
        settings = load_settings()

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

        settings["window_geometry"] = self.saveGeometry().toBase64().data().decode()
        save_settings(settings)

        if settings.get("minimize_to_tray", True) and hasattr(self, "tray_icon") and self.tray_icon.isVisible():
            event.ignore()
            self.hide()
            self.tray_icon.showMessage(
                "EleViewer", "Running in background. Click tray icon to restore.",
                QSystemTrayIcon.Information, 2000
            )
        else:
            try:
                from vault_indexer import _active_worker as vault_worker
                if vault_worker and vault_worker.isRunning():
                    vault_worker.cancel()
                    vault_worker.wait(500)
            except Exception:
                pass
            if hasattr(self, "tts_bar") and self.tts_bar:
                try:
                    self.tts_bar.stop()
                except Exception:
                    pass
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

            scroll_y = 0
            if hasattr(editor, "verticalScrollBar"):
                scroll_y = editor.verticalScrollBar().value()
            elif hasattr(editor, "findChild"):
                from PySide6.QtWidgets import QScrollBar
                sb = editor.findChild(QScrollBar)
                if sb:
                    scroll_y = sb.value()

            zoom = getattr(editor, "zoom_level", getattr(editor, "scale_factor", 1.0))
            pdf_page = getattr(editor, "current_page", 0)

            tabs_info.append({
                "file_path": file_path,
                "content": content,
                "is_active": (i == self.tabs.currentIndex()),
                "is_modified": getattr(editor, "is_modified", False),
                "scroll_y": scroll_y,
                "scroll_pos": scroll_y,
                "zoom": zoom,
                "pdf_page": pdf_page,
            })
        save_session(tabs_info, bookmarks_panel_visible=self.bookmarks_panel.isVisible())

    # IMPROVEMENT: persist scroll position and PDF zoom across sessions
    def restore_session(self):
        session = load_session()
        tabs = session.get("tabs", [])
        active_index = 0
        for tab_info in tabs:
            file_path = tab_info.get("file_path")
            content = tab_info.get("content", "")
            is_active = tab_info.get("is_active", False)
            scroll_y = tab_info.get("scroll_y", tab_info.get("scroll_pos", 0))
            zoom = tab_info.get("zoom", 1.0)
            pdf_page = tab_info.get("pdf_page", 0)

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
                tab_icon = _tab_icon_for(file_path or name)
                self.tabs.addTab(editor, tab_icon, name)

                # QTimer.singleShot delay ensures widget has rendered before setting scroll/zoom
                QTimer.singleShot(150, lambda t=editor, s=scroll_y, z=zoom, p=pdf_page: (
                    t.verticalScrollBar().setValue(s) if hasattr(t, "verticalScrollBar") else (
                        t.findChild(QScrollBar).setValue(s) if hasattr(t, "findChild") and t.findChild(QScrollBar) else None
                    ),
                    t.set_zoom(z) if hasattr(t, "set_zoom") else None,
                    t.go_to_page(p) if hasattr(t, "go_to_page") else None,
                ))

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
            self._add_menu_action(file_menu, "Toggle Web Panel", self.toggle_web_panel, "Ctrl+Shift+W")
            file_menu.addSeparator()
        self._add_menu_action(
            file_menu, "Close Tab",
            lambda: self.close_tab(self.tabs.currentIndex()), "Ctrl+W",
        )

        edit_menu = menu.addMenu("Edit")
        self._add_menu_action(edit_menu, "Find...", self.show_find, "Ctrl+F")
        self._add_menu_action(edit_menu, "Replace...", self.show_replace, "Ctrl+H")
        self._add_menu_action(edit_menu, "Search in Vault...", self.open_vault_search, "Ctrl+Shift+F")

        vault_menu = menu.addMenu("Vault")
        vault_menu.addAction("Add Folder", self.add_vault)
        vault_menu.addAction("Remove Folder", self.vault_panel.remove_current_vault)
        self._add_menu_action(vault_menu, "Toggle Panel", self.toggle_vault_panel, "Alt+V")

        session_menu = menu.addMenu("Session")
        self._add_menu_action(session_menu, "New Session (Clear)", self._new_session)
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
        self._add_menu_action(self.bookmarks_menu, "Bookmark Current Tab", self.bookmark_current_tab, "Ctrl+D")

        self._add_menu_action(menu, "Settings...", self.open_settings, "Alt+S")

        help_menu = menu.addMenu("Help")
        self._add_menu_action(help_menu, "Getting Started Guide", self.open_getting_started, "F1")
        self._add_menu_action(help_menu, "Check for Updates...", self.check_for_updates_manual)
        help_menu.addSeparator()
        self._add_menu_action(help_menu, "Submit Feedback...", self.open_feedback_dialog)
        self._add_menu_action(help_menu, "Tell us what you think 💭", self.open_review_page)

        self.update_menus()

    # FIX: WA_DeleteOnClose=True ensures dialog is freed on close
    def open_settings(self):
        # Check if settings tab is already open
        for i in range(self.tabs.count()):
            widget = self.tabs.widget(i)
            if hasattr(widget, "_is_settings_view"):
                self.tabs.setCurrentIndex(i)
                return
                
        from settings_view import SettingsView
        settings_view = SettingsView(self)
        settings_view._is_settings_view = True
        
        idx = self.tabs.addTab(settings_view, "Settings")
        self.tabs.setCurrentIndex(idx)

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
        from pptx_viewer import PptxViewer
        from html_viewer import HtmlViewer
        from csv_viewer import CsvViewer
        
        _add("Plain Text (.txt)", ".txt", EditorTab)
        _add("Markdown (.md)", ".md", MarkdownViewer)
        _add("HTML (.html)", ".html", HtmlViewer)
        _add("Word Document (.docx)", ".docx", DocxViewer)
        _add("Excel Spreadsheet (.xlsx)", ".xlsx", XlsxViewer)
        _add("PowerPoint Presentation (.pptx)", ".pptx", PptxViewer)
        _add("CSV Spreadsheet (.csv)", ".csv", CsvViewer)
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

    def show_tab_context_menu(self, pos, tab_widget=None):
        tw = tab_widget or self.tabs
        index = tw.tabBar().tabAt(pos)
        if index == -1:
            return
        editor = tw.widget(index)
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
            
        if tw == self.tabs:
            split_action = menu.addAction(icon("sidebar", size=ICON_SIZE_COMPACT), "Split screen with this tab")
            split_action.triggered.connect(lambda: self._move_tab_between_widgets(self.tabs, self.tabs_right, index))
        else:
            split_action = menu.addAction(icon("sidebar", size=ICON_SIZE_COMPACT), "Unsplit (Return to main)")
            split_action.triggered.connect(lambda: self._move_tab_between_widgets(self.tabs_right, self.tabs, index))
            
        def _open_new_window():
            if getattr(editor, "is_modified", False):
                self.save_editor(editor)
            new_win = self.__class__()
            if hasattr(self, "autosaver"):
                from autosave import AutoSaver
                new_win.autosaver = AutoSaver(new_win)
            new_win.setAttribute(Qt.WA_DeleteOnClose)
            new_win.show()
            if path:
                new_win._open_vault_file(path)
            self._close_tab_in_widget(tw, index)
            
        sep_action = menu.addAction(icon("external-link", size=ICON_SIZE_COMPACT), "Move to New Window")
        sep_action.triggered.connect(_open_new_window)
            
        menu.addAction("Close Tab", lambda: self._close_tab_in_widget(tw, index))
        menu.exec(tw.mapToGlobal(pos))
        
    def _move_tab_between_widgets(self, src, dst, index):
        w = src.widget(index)
        text = src.tabText(index)
        ic = src.tabIcon(index)
        src.removeTab(index)
        if src == self.tabs_right and src.count() == 0:
            src.hide()
        dst.addTab(w, ic, text)
        dst.show()
        dst.setCurrentWidget(w)
        
    def _close_tab_in_widget(self, tw, index):
        if tw == self.tabs:
            self.close_tab(index)
        else:
            w = tw.widget(index)
            tw.removeTab(index)
            w.deleteLater()
            if tw.count() == 0:
                tw.hide()
            self.update_status_bar()

    def pin_file(self, path):
        save_pinned_file(path)
        self.update_menus()

    def unpin_file(self, path):
        remove_pinned_file(path)
        self.update_menus()

    def close_current_tab(self):
        from PySide6.QtWidgets import QApplication
        focus_w = QApplication.focusWidget()
        if self._web_dock and self._web_dock.isVisible() and focus_w and (self._web_dock.isAncestorOf(focus_w) or focus_w == self._web_dock):
            web_panel = self._web_dock.widget()
            if web_panel and hasattr(web_panel, "tabs") and web_panel.tabs.count() > 0:
                web_panel._close_tab(web_panel.tabs.currentIndex())
                return
        self.close_tab(self.tabs.currentIndex())

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
            elif reply == QMessageBox.No:
                if hasattr(self, "draft_manager"):
                    self.draft_manager.cleanup(path=getattr(editor, "file_path", None), editor_id=id(editor))

        tab_type = "editor"
        url = ""
        if hasattr(editor, "url"):
            tab_type = "web"
            url = editor.url().toString()
        elif hasattr(editor, "_is_welcome_screen"):
            tab_type = "welcome"
        elif hasattr(editor, "_is_settings_view"):
            tab_type = "settings"

        self.closed_tabs.append({
            "type": tab_type,
            "url": url,
            "content": editor.toPlainText() if hasattr(editor, "toPlainText") else "",
            "file_path": getattr(editor, "file_path", None),
            "modified": getattr(editor, "is_modified", False),
        })
        # FIX: deleteLater() prevents cumulative memory leak on tab close
        widget = self.tabs.widget(index)
        self.tabs.removeTab(index)
        if widget is not None:
            if hasattr(widget, 'cleanup'):
                widget.cleanup()
            if hasattr(widget, 'page'):
                widget.page().deleteLater()
            widget.deleteLater()

        if self.tabs.count() == 0:
            self.new_tab()
        else:
            self.update_status_bar()

    def reopen_closed_tab(self):
        if not self.closed_tabs:
            self.show_status_message("No closed tabs to reopen", 2000)
            return
        tab_data = self.closed_tabs.pop()
        
        tab_type = tab_data.get("type", "editor")
        if tab_type == "web":
            self.open_web_tab(tab_data.get("url", ""))
            return
        elif tab_type == "welcome":
            self.start_onboarding()
            return
        elif tab_type == "settings":
            self.open_settings()
            return
            
        file_path = tab_data["file_path"]
        if file_path and os.path.exists(file_path):
            editor = create_viewer_widget(file_path)
            self._wire_editor(editor)
            if tab_data["modified"] and tab_data["content"] and not is_binary_format(file_path):
                editor.setPlainText(tab_data["content"])
                editor.is_modified = tab_data["modified"]
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
        if hasattr(self, "onboarding_widget"):
            self.onboarding_widget.check_off("quick_switch")
        recent = load_recent_files(validate=True)
        pinned = load_pinned_files(validate=True)
        open_tabs = []
        for i in range(self.tabs.count()):
            editor = self.tabs.widget(i)
            path = getattr(editor, "file_path", None)
            if path: open_tabs.append(path)
            
        switcher = QuickSwitcher(recent, pinned, open_tabs, self)
        switcher.file_selected.connect(self.open_recent_file)
        switcher.exec()

    def _new_session(self):
        """Clear session state and close all tabs."""
        while self.tabs.count() > 0:
            w = self.tabs.widget(0)
            self.tabs.removeTab(0)
            if w:
                w.deleteLater()
        clear_session()
        self.tabs.addTab(self._create_welcome_widget(), "Welcome")
        self.show_status_message("Started new fresh session", 3000)

    def open_vault_search(self, active_vault=None):
        if not active_vault or not isinstance(active_vault, str):
            if hasattr(self, 'vault_panel') and self.vault_panel.vault_selector.currentData():
                active_vault = self.vault_panel.vault_selector.currentData()
            else:
                active_vault = None
                
        all_vaults = load_settings().get("vault_paths", [])
        if not all_vaults and not active_vault:
            QMessageBox.information(self, "No Vaults", "You don't have any vaults opened.")
            return
            
        from vault_search import VaultSearchDialog
        dlg = VaultSearchDialog(active_vault, all_vaults, self)
        dlg.file_selected.connect(self.open_file)
        dlg.exec()

    def current_editor(self):
        from PySide6.QtWidgets import QApplication
        fw = QApplication.focusWidget()
        if self.tabs_right.isVisible() and fw and (self.tabs_right.isAncestorOf(fw) or fw == self.tabs_right):
            return self.tabs_right.currentWidget()
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

    def open_file(self, file_path=None):
        path = file_path
        if not path:
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
            if hasattr(self, "draft_manager"):
                self.draft_manager.cleanup(path=path, editor_id=id(editor))
            self.update_tab_title(editor)
            self.show_status_message(f"Saved {os.path.basename(path)}", 3000)
            self.update_status_bar()
            if WEB_AVAILABLE and self._web_dock and self._web_dock.isVisible():
                from PySide6.QtCore import QUrl
                file_url = QUrl.fromLocalFile(os.path.abspath(path)).toString()
                self._web_dock.widget().reload_url(file_url)
            return True
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save file: {str(e)}")
            return False

    # FIX: dynamic extension detection replaces hardcoded .docx default
    def save_file_as(self):
        editor = self.current_editor()
        if not editor:
            return
            
        current_ext = ".txt"
        if hasattr(editor, "file_path") and editor.file_path:
            current_ext = os.path.splitext(editor.file_path)[1].lower() or ".txt"
        else:
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
            if hasattr(self, "draft_manager"):
                self.draft_manager.cleanup(path=path, editor_id=id(editor))
            save_recent_file(path)
            self.update_menus()
            self.update_tab_title(editor)
            self.show_status_message(f"Saved as {os.path.basename(path)}", 3000)
            self.update_status_bar()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save file: {str(e)}")

    save_tab_as = save_file_as

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



    def toggle_web_panel(self):
        if not WEB_AVAILABLE:
            QMessageBox.warning(self, "Missing Module", "QtWebEngine not installed.")
            return
        if self._web_dock is not None:
            self._web_dock.setVisible(not self._web_dock.isVisible())
        else:
            self.open_web_tab()

    def open_web_tab(self):
        from PySide6.QtWidgets import QDockWidget, QWidget, QLabel, QToolButton, QHBoxLayout, QMessageBox
        from theme import get_active_palette, compact_toolbar_stylesheet
        global WEB_AVAILABLE
        if hasattr(self, "onboarding_widget"):
            self.onboarding_widget.check_off("web")
        if not WEB_AVAILABLE:
            QMessageBox.warning(self, "Missing Module", "QtWebEngine not installed.")
            return

        if self._web_dock is not None:
            if not self._web_dock.isVisible():
                self._web_dock.setVisible(True)
            self._web_dock.widget().add_tab()
            return

        # First time: create as a dockable side panel (matches site's
        # "side-by-side" promise — the web panel is NOT a tab)
        # Lazy-load Chromium only when Ctrl+T is pressed!
        try:
            from web_panel import WebPanel, WEB_AVAILABLE as _WEB_AVAILABLE
            WEB_AVAILABLE = _WEB_AVAILABLE
        except ImportError:
            WEB_AVAILABLE = False
            QMessageBox.warning(self, "Missing Module", "QtWebEngine not installed.")
            return

        web_panel = WebPanel()
        web_panel.expand_requested.connect(self.toggle_web_focus)
        
        self._web_dock = QDockWidget("Web Browser", self)
        self._web_dock.setWidget(web_panel)
        self._web_dock.setMinimumWidth(480)
        self._web_dock.setFeatures(
            QDockWidget.DockWidgetClosable
            | QDockWidget.DockWidgetMovable
            | QDockWidget.DockWidgetFloatable
        )
        self.addDockWidget(Qt.RightDockWidgetArea, self._web_dock)

    def toggle_web_focus(self):
        from icons import icon
        if self._web_dock and self._web_dock.isVisible():
            if self.main_splitter.isVisible():
                self.main_splitter.hide()
                self._web_dock.widget().btn_expand.setIcon(icon("minimize-2", size=24))
                self._web_dock.widget().btn_expand.setToolTip("Exit Web Focus")
            else:
                self.main_splitter.show()
                self._web_dock.widget().btn_expand.setIcon(icon("maximize-2", size=24))
                self._web_dock.widget().btn_expand.setToolTip("Toggle Web Focus")
        
        # Auto-maximize if no editor tabs are open (ponytail)
        if self.tabs.count() == 0:
            self.editor_splitter.hide()

        p = get_active_palette()
        title_bar = QWidget()
        title_bar.setStyleSheet(f"background: {p['BRAND_PANEL']}; border-bottom: 1px solid {p['BRAND_BORDER']};")
        tb_layout = QHBoxLayout(title_bar)
        tb_layout.setContentsMargins(10, 6, 10, 6)
        
        lbl_title = QLabel("Web Browser")
        lbl_title.setStyleSheet(f"color: {p['BRAND_MUTED_FG']}; font-weight: bold; font-size: 12px; text-transform: uppercase; letter-spacing: 1px;")
        tb_layout.addWidget(lbl_title)
        tb_layout.addStretch()

        from icons import icon
        icon_sz = 26
        icon_qsize = QSize(icon_sz, icon_sz)

        btn_max = QToolButton()
        btn_max.setIcon(icon("maximize", size=icon_sz))
        btn_max.setIconSize(icon_qsize)
        btn_max.setToolTip("Maximize Web Panel")
        btn_max.setStyleSheet(compact_toolbar_stylesheet())
        
        btn_float = QToolButton()
        btn_float.setIcon(icon("external-link", size=icon_sz))
        btn_float.setIconSize(icon_qsize)
        btn_float.setToolTip("Pop Out Web Panel")
        btn_float.setStyleSheet(compact_toolbar_stylesheet())
        
        btn_close = QToolButton()
        btn_close.setIcon(icon("x", size=icon_sz))
        btn_close.setIconSize(icon_qsize)
        btn_close.setToolTip("Close Web Panel")
        btn_close.setStyleSheet(compact_toolbar_stylesheet())

        tb_layout.addWidget(btn_max)
        tb_layout.addWidget(btn_float)
        tb_layout.addWidget(btn_close)

        self._web_dock.setTitleBarWidget(title_bar)

        # Maximize logic: hide the editor splitter so the dock takes full width
        def _toggle_maximize():
            if self.editor_splitter.isVisible():
                self.editor_splitter.hide()
                btn_max.setIcon(icon("minimize", size=icon_sz))
                btn_max.setToolTip("Restore Web Panel")
            else:
                self.editor_splitter.show()
                btn_max.setIcon(icon("maximize", size=icon_sz))
                btn_max.setToolTip("Maximize Web Panel")
                
        btn_max.clicked.connect(_toggle_maximize)
        
        def _toggle_float():
            self._web_dock.setFloating(not self._web_dock.isFloating())
            
        btn_float.clicked.connect(_toggle_float)
        btn_close.clicked.connect(self._web_dock.hide)

    @Slot(QUrl)
    @Slot(str)
    def handle_url(self, url):
        url_str = url.toString() if hasattr(url, "toString") else str(url)
        if url_str.lower().startswith(("http:", "https:")):
            self.open_web_tab_with_url(url_str)
        elif url_str.lower().startswith("file:"):
            self._handle_file_url(url)
        else:
            self.open_web_tab_with_url(url_str)

    def open_web_tab_with_url(self, url, title=None):
        url_str = url.toString() if hasattr(url, "toString") else str(url)
        if not self._web_dock or not self._web_dock.isVisible():
            self.toggle_web_panel()
        if self._web_dock and self._web_dock.widget():
            self._web_dock.widget().open_url_in_new_tab(url_str, title if isinstance(title, str) else url_str)

    def _handle_file_url(self, url):
        url_str = url.toString() if hasattr(url, "toString") else str(url)
        local_path = QUrl(url_str).toLocalFile() if hasattr(url, "toString") and hasattr(url, "toLocalFile") else url_str.replace("file:///", "").replace("file://", "")
        if os.path.exists(local_path):
            self.open_recent_file(local_path)
        else:
            self.show_status_message(f"Linked file not found: {local_path}", 3000)

    def show_find(self):
        editor = self.current_editor()
        if hasattr(editor, "show_find_bar"):
            # Viewer owns its own find UI (e.g. PdfViewer)
            editor.show_find_bar()
        elif hasattr(editor, "find_text"):
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

    def _refresh_tab_icons(self):
        """Update tab icons so the active/focused tab has a vibrant blue icon while inactive tabs are calm gray."""
        current_idx = self.tabs.currentIndex()
        for i in range(self.tabs.count()):
            editor = self.tabs.widget(i)
            path = getattr(editor, "file_path", None) or self.tabs.tabText(i)
            self.tabs.setTabIcon(i, _tab_icon_for(path, active=(i == current_idx)))



    def toggle_tts_bar(self):
        if self.tts_bar.isVisible():
            self.tts_bar.hide()
            self._stop_tts()
        else:
            voices = self.tts_engine.list_voices()
            self.tts_bar.populate_voices(voices)
            self.tts_bar.show()
            self._speak_current_tab()

    def _speak_current_tab(self):
        current = self.tabs.currentWidget()
        if not current:
            return

        filename = "Untitled"
        if hasattr(current, "file_path") and current.file_path:
            filename = os.path.basename(current.file_path)

        voice_id = self.tts_bar.get_selected_voice_id()

        # 1. If the viewer has its own dedicated TTS engine (e.g., PdfViewer or PptxViewer)
        if hasattr(current, "tts") and hasattr(current, "read_current_page"):
            spoken = current.read_current_page(voice_id=voice_id)
            if spoken:
                self.tts_bar.show()
                if hasattr(current, "current_page") and hasattr(current, "total_pages"):
                    self.tts_bar.set_status(filename, f"page {current.current_page + 1} of {current.total_pages}")
                elif hasattr(current, "current_slide") and hasattr(current, "total_slides"):
                    self.tts_bar.set_status(filename, f"slide {current.current_slide + 1} of {current.total_slides}")
            return

        # 2. For all other viewers (DocxViewer, EditorTab, MarkdownViewer, XlsxViewer, etc.)
        text = ""
        if hasattr(current, "read_current_page"):
            try:
                text = current.read_current_page(voice_id=voice_id)
            except Exception:
                pass

        if not text and hasattr(current, "toPlainText"):
            try:
                text = current.toPlainText()
            except Exception:
                pass

        if not text and hasattr(current, "editor") and hasattr(current.editor, "toPlainText"):
            try:
                text = current.editor.toPlainText()
            except Exception:
                pass

        if text and str(text).strip():
            self.tts_bar.show()
            self.tts_engine.speak(str(text).strip(), voice_id)
            self.tts_bar.set_status(filename, "Reading aloud...")
        else:
            self.show_status_message("No text available for TTS in current tab", 2000)

    def _stop_tts(self):
        self.tts_engine.stop()
        current = self.tabs.currentWidget()
        if hasattr(current, "tts"):
            current.tts.stop()
        if hasattr(self, "tts_bar") and self.tts_bar:
            self.tts_bar.set_active_reading(False)

