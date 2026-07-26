from PySide6.QtWidgets import (
    QMainWindow, QTabWidget, QFileDialog, QMessageBox,
    QSplitter, QMenu, QToolBar, QToolButton, QVBoxLayout, QWidget,
    QDockWidget, QLabel, QSystemTrayIcon, QApplication, QScrollBar,
)
from PySide6.QtGui import QAction, QKeySequence, QShortcut, QIcon
from PySide6.QtCore import Qt, QSize, QTimer
import os

APP_VERSION = "1.3.0"

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


def _tab_icon_for(path_or_name):
    """Return a small QIcon appropriate for the file extension or filename."""
    from file_icons import file_type_icon
    if not path_or_name:
        return file_type_icon(".txt", size=18)
    if path_or_name.startswith("."):
        ext = path_or_name.lower()
    else:
        ext = os.path.splitext(path_or_name)[1].lower()
    return file_type_icon(ext or ".txt", size=18)


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
        self.restore_session()

        if self.tabs.count() == 0:
            self.new_tab()

        self.tabs.currentChanged.connect(self.update_status_bar)
        self.update_status_bar()
        self._check_for_updates_async()
        
        # Global Esc shortcut for closing popups and sidebars
        self.esc_shortcut = QShortcut(QKeySequence(Qt.Key_Escape), self)
        self.esc_shortcut.activated.connect(self.handle_escape)

        # IMPROVEMENT: system tray minimization with restore on double-click
        self.tray_icon = QSystemTrayIcon(create_eleviewer_icon(32), self)
        tray_menu = QMenu()
        tray_menu.addAction("Open EleViewer", self.show_and_raise)
        tray_menu.addAction("Quit", QApplication.quit)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self._on_tray_activated)
        self.tray_icon.show()

    def show_and_raise(self):
        self.show()
        self.raise_()
        self.activateWindow()

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_and_raise()

    # FIX: guard prevents ESC double-fire when modal dialog is active
    def handle_escape(self):
        if QApplication.activeModalWidget() is not None:
            return

        # Hide Find/Replace if open in current editor
        current_widget = self.tabs.currentWidget()
        if isinstance(current_widget, EditorTab):
            if current_widget.find_replace_widget.isVisible():
                current_widget.find_replace_widget.hide_panel()
                return

        # Hide Vault Sidebar if open
        if self.vault_panel and self.vault_panel.isVisible():
            self.vault_panel.hide()
            return
            
        # Hide Bookmarks Sidebar if open
        if self.bookmarks_panel and self.bookmarks_panel.isVisible():
            self.bookmarks_panel.hide()
            return

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


    def _setup_status_bar(self):
        status_bar = self.statusBar()
        status_bar.setSizeGripEnabled(False)
        
        from theme import BRAND_MUTED_FG

        self.status_left = QLabel("0 tabs · session saved")
        self.status_left.setStyleSheet(f"color: {BRAND_MUTED_FG}; font-family: monospace; font-size: 11px; padding-left: 8px;")

        self.status_center = QLabel("Ctrl+Q quick switch · Alt+V vault")
        self.status_center.setStyleSheet(f"color: {BRAND_MUTED_FG}; font-family: monospace; font-size: 11px;")
        self.status_center.setAlignment(Qt.AlignCenter)

        self.status_right = QLabel("md · UTF-8")
        self.status_right.setStyleSheet(f"color: {BRAND_MUTED_FG}; font-family: monospace; font-size: 11px; padding-right: 12px;")

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
        self.status_center.setText(f"{self.shortcut_hints[self.shortcut_index]}  ·  {self.shortcut_hints[next_idx]}")

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

        self.tts_bar = TtsReaderBar()
        self.tts_bar.hide()
        self.tts_bar.populate_voices(self.tts_engine.list_voices())
        self.tts_bar.speak_requested.connect(self._speak_current_tab)
        self.tts_bar.stop_requested.connect(self._stop_tts)
        self.tts_bar.voice_changed.connect(lambda vid: self._speak_current_tab())

        editor_layout = QVBoxLayout()
        editor_layout.setContentsMargins(0, 0, 0, 0)
        editor_layout.setSpacing(0)
        editor_layout.addWidget(self.tabs)
        editor_layout.addWidget(self.find_replace_panel)
        editor_layout.addWidget(self.tts_bar)
        
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
        self.vault_panel.search_requested.connect(self.open_vault_search)

        self.setCentralWidget(self.main_splitter)

        for i in range(1, 10):
            QShortcut(QKeySequence(f"Ctrl+{i}"), self).activated.connect(
                lambda idx=i-1: self.tabs.setCurrentIndex(min(idx, self.tabs.count()-1)) if self.tabs.count() > 0 else None
            )

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
        vault_btn.setShortcutContext(Qt.WidgetShortcut)
        vault_btn.triggered.connect(self.toggle_vault_panel)
        self.toolbar.addAction(vault_btn)

        open_btn = QAction(icon("folder-open", size=ICON_SIZE_TOOLBAR), "Open", self)
        open_btn.setToolTip("Open File (Ctrl+O)")
        open_btn.setShortcut("Ctrl+O")
        open_btn.setShortcutContext(Qt.WidgetShortcut)
        open_btn.triggered.connect(self.open_file)
        self.toolbar.addAction(open_btn)

        save_btn = QAction(icon("save", size=ICON_SIZE_TOOLBAR), "Save", self)
        save_btn.setToolTip("Save File (Ctrl+S)")
        save_btn.setShortcut("Ctrl+S")
        save_btn.setShortcutContext(Qt.WidgetShortcut)
        save_btn.triggered.connect(self.save_file)
        self.toolbar.addAction(save_btn)
        
        tts_btn = QAction(icon("volume-2", size=ICON_SIZE_TOOLBAR), "Read Aloud", self)
        tts_btn.setToolTip("Read Aloud / Toggle TTS (F9)")
        tts_btn.setShortcut("F9")
        tts_btn.setShortcutContext(Qt.WidgetShortcut)
        tts_btn.triggered.connect(self.toggle_tts_bar)
        self.toolbar.addAction(tts_btn)

        if WEB_AVAILABLE:
            web_btn = QAction(icon("globe", size=ICON_SIZE_TOOLBAR), "Web Panel", self)
            web_btn.setToolTip("Open Web Browser Panel / New Web Tab (Ctrl+T)")
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
        # so they trigger reliably regardless of which child widget has focus and without ambiguous shortcut conflicts.
        shortcuts = [
            ("Alt+V", self.toggle_vault_panel),
            ("Ctrl+Q", self.open_quick_switcher),
            ("Ctrl+T", self.open_web_tab),
            ("Ctrl+Shift+T", self.reopen_closed_tab),
            ("F9", self.toggle_tts_bar),
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

    def bookmark_current_tab(self):
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
        from pathlib import Path
        welcome_file = Path("getting_started/Welcome to EleViewer.md").absolute()
        if welcome_file.exists():
            self._open_vault_file(str(welcome_file))
        else:
            self.show_status_message("Getting Started guide not found", 3000)

    def show_status_message(self, message, timeout_ms=0):
        self.statusBar().showMessage(message, timeout_ms)

    def update_status_bar(self):
        editor = self.current_editor()
        if not editor:
            self.setWindowTitle(f"EleViewer v{APP_VERSION}")
            self.status_left.setText("Ready")
            self.status_right.setText("")
            return
        path = getattr(editor, "file_path", None)
        name = os.path.basename(path) if path else "Untitled"
        modified = " • Modified" if getattr(editor, "is_modified", False) else ""

        self.setWindowTitle(f"EleViewer v{APP_VERSION} — {name}")

        tab_count = self.tabs.count()
        ext = get_file_extension(path) if path else ""
        ext_label = ext.upper() if ext else "TXT"
        
        parts = [f"{tab_count} tab{'s' if tab_count != 1 else ''}"]
        parts.append("Modified" if modified else "session saved")
        
        self.status_left.setText(" · ".join(parts))
        self.status_right.setText(f"{ext_label} · UTF-8")

    def _connect_editor_signals(self, editor):
        if hasattr(editor, "textChanged"):
            editor.textChanged.connect(lambda ed=editor: self._on_editor_changed(ed))

    def _on_editor_changed(self, editor):
        self.update_tab_title(editor)
        self.update_status_bar()

    def _add_editor_tab(self, editor, name):
        self._connect_editor_signals(editor)
        path = getattr(editor, "file_path", None) or name
        tab_icon = _tab_icon_for(path)
        index = self.tabs.addTab(editor, tab_icon, name)
        self.tabs.setCurrentIndex(index)
        self.update_status_bar()
        
        self._check_file_load_milestone()
        
        return index

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
        help_menu.addSeparator()
        self._add_menu_action(help_menu, "Submit Feedback...", self.open_feedback_dialog)
        self._add_menu_action(help_menu, "Tell us what you think 💭", self.open_review_page)

        self.update_menus()

    # FIX: WA_DeleteOnClose=True ensures dialog is freed on close
    def open_settings(self):
        if getattr(self, '_settings_dialog', None) is None:
            from settings_dialog import SettingsDialog
            self._settings_dialog = SettingsDialog(self)
            self._settings_dialog.finished.connect(
                lambda: setattr(self, '_settings_dialog', None)
            )
            self._settings_dialog.accepted.connect(self._on_settings_saved)
        self._settings_dialog.show()
        self._settings_dialog.raise_()

    def _on_settings_saved(self):
        if hasattr(self, 'autosaver') and self.autosaver:
            self.autosaver.apply_settings()
        from settings import load_settings
        settings = load_settings()
        if hasattr(self, 'vault_panel') and self.vault_panel:
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
        from pptx_viewer import PptxViewer
        
        _add("Plain Text (.txt)", ".txt", EditorTab)
        _add("Markdown (.md)", ".md", MarkdownViewer)
        _add("HTML (.html)", ".html", MarkdownViewer, is_html=True)
        _add("Word Document (.docx)", ".docx", DocxViewer)
        _add("Excel Spreadsheet (.xlsx)", ".xlsx", XlsxViewer)
        _add("PowerPoint Presentation (.pptx)", ".pptx", PptxViewer)
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
            elif reply == QMessageBox.No:
                if hasattr(self, "draft_manager"):
                    self.draft_manager.cleanup(path=getattr(editor, "file_path", None), editor_id=id(editor))

        self.closed_tabs.append({
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
        open_tabs = []
        for i in range(self.tabs.count()):
            editor = self.tabs.widget(i)
            path = getattr(editor, "file_path", None)
            if path: open_tabs.append(path)
            
        switcher = QuickSwitcher(recent, pinned, open_tabs, self)
        switcher.file_selected.connect(self.open_recent_file)
        switcher.exec()

    def open_vault_search(self, active_vault=None):
        if not active_vault or not isinstance(active_vault, str):
            if hasattr(self, 'vault_panel') and self.vault_panel.vault_selector.currentData():
                active_vault = self.vault_panel.vault_selector.currentData()
            else:
                active_vault = None
                
        all_vaults = load_settings().get("vaults", [])
        if not all_vaults and not active_vault:
            QMessageBox.information(self, "No Vaults", "You don't have any vaults opened.")
            return
            
        from vault_search import VaultSearchDialog
        dlg = VaultSearchDialog(active_vault, all_vaults, self)
        dlg.file_selected.connect(self.open_file)
        dlg.exec()

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
            if hasattr(self, "draft_manager"):
                self.draft_manager.cleanup(path=path, editor_id=id(editor))
            self.update_tab_title(editor)
            self.show_status_message(f"Saved {os.path.basename(path)}", 3000)
            self.update_status_bar()
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

    def update_status_bar(self):
        count = self.tabs.count()
        self.status_left.setText(f"{count} tab{'s' if count != 1 else ''} · session saved")
        
        current_widget = self.tabs.currentWidget()
        if current_widget:
            file_path = getattr(current_widget, "file_path", None)
            if file_path:
                filename = os.path.basename(file_path)
                self.setWindowTitle(f"EleViewer — {filename}")
                ext = os.path.splitext(file_path)[1].lstrip(".").lower() or "txt"
                self.status_right.setText(f"{ext} · UTF-8")
            else:
                self.setWindowTitle(f"EleViewer — Untitled")
                self.status_right.setText("txt · UTF-8")
        else:
            self.setWindowTitle(f"EleViewer v{APP_VERSION}")
            self.status_right.setText("UTF-8")

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

