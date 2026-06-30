from PySide6.QtWidgets import (
    QMainWindow,
    QTabWidget,
    QFileDialog,
    QMessageBox
)

from PySide6.QtGui import QAction

from file_handler import create_viewer_widget, get_file_content, get_file_extension
from recent_files import load_recent_files, save_recent_file, remove_recent_file
from pinned_files import load_pinned_files, save_pinned_file, remove_pinned_file, is_pinned
from session_manager import load_session, save_session, clear_session
from quick_switcher import QuickSwitcher
import os


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("EleViewer")
        self.resize(1200, 800)

        # CLOSED TAB HISTORY
        self.closed_tabs = []

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)

        self.setCentralWidget(self.tabs)

        self.create_menu()

        # RESTORE SESSION
        self.restore_session()

        # If no tabs were restored, create a blank one
        if self.tabs.count() == 0:
            self.new_tab()

    def closeEvent(self, event):
        """Handle app close — save session."""
        self.save_current_session()
        event.accept()

    def save_current_session(self):
        """Save all open tabs to session file."""
        tabs_info = []
        
        for i in range(self.tabs.count()):
            editor = self.tabs.widget(i)
            
            tabs_info.append({
                "file_path": editor.file_path,
                "content": editor.toPlainText() if hasattr(editor, 'toPlainText') else "",
                "is_active": (i == self.tabs.currentIndex()),
                "is_modified": editor.is_modified
            })
        
        save_session(tabs_info)

    def restore_session(self):
        """Restore tabs from previous session."""
        session = load_session()
        
        active_index = 0
        
        for i, tab_info in enumerate(session):
            file_path = tab_info.get("file_path")
            content = tab_info.get("content", "")
            is_active = tab_info.get("is_active", False)
            
            try:
                if file_path and os.path.exists(file_path):
                    # File exists on disk, load it
                    editor = create_viewer_widget(file_path)
                else:
                    # Recreate unsaved content
                    from editor import EditorTab
                    editor = EditorTab()
                    editor.file_path = file_path
                    if content:
                        editor.setPlainText(content)
                
                editor.textChanged.connect(
                    lambda: self.update_tab_title(editor)
                )
                
                name = os.path.basename(file_path) if file_path else "Untitled"
                if editor.is_modified:
                    name += "*"
                
                self.tabs.addTab(editor, name)
                
                if is_active:
                    active_index = self.tabs.count() - 1
            
            except Exception as e:
                print(f"Failed to restore tab: {e}")
        
        # Set active tab
        if self.tabs.count() > 0:
            self.tabs.setCurrentIndex(active_index)

    def create_menu(self):
        
        menu = self.menuBar()

        file_menu = menu.addMenu("File")

        # NEW
        new_action = QAction("New", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_tab)

        # OPEN
        open_action = QAction("Open", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)

        # SAVE
        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)

        # SAVE AS
        save_as_action = QAction("Save As", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.save_file_as)

        # CLOSE TAB
        close_action = QAction("Close Tab", self)
        close_action.setShortcut("Ctrl+W")
        close_action.triggered.connect(
            lambda: self.close_tab(self.tabs.currentIndex())
        )

        # REOPEN CLOSED TAB
        reopen_action = QAction("Reopen Closed Tab", self)
        reopen_action.setShortcut("Ctrl+Shift+T")
        reopen_action.triggered.connect(self.reopen_closed_tab)

        # QUICK SWITCHER
        switcher_action = QAction("Quick Switcher", self)
        switcher_action.setShortcut("Ctrl+P")
        switcher_action.triggered.connect(self.open_quick_switcher)

        # ADD ACTIONS
        file_menu.addAction(new_action)
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        file_menu.addAction(close_action)
        file_menu.addAction(reopen_action)
        file_menu.addAction(switcher_action)

        file_menu.addSeparator()

        # PINNED FILES
        self.pinned_menu = file_menu.addMenu("Pinned Files")

        # RECENT FILES
        self.recent_menu = file_menu.addMenu("Recent Files")

        # LOAD MENUS
        self.update_menus()

    def update_menus(self):
        """Update recent and pinned file menus."""
        self.update_recent_files_menu()
        self.update_pinned_files_menu()

    def update_tab_title(self, editor):
        index = self.tabs.indexOf(editor)

        if index == -1:
            return

        if editor.file_path:
            name = editor.file_path.split("/")[-1]
        else:
            name = "Untitled"

        if editor.is_modified:
            name += "*"

        self.tabs.setTabText(index, name)

    def new_tab(self):
        from editor import EditorTab
        
        editor = EditorTab()

        editor.textChanged.connect(
            lambda: self.update_tab_title(editor)
        )

        index = self.tabs.addTab(editor, "Untitled")

        self.tabs.setCurrentIndex(index)

    def close_tab(self, index):
        editor = self.tabs.widget(index)

        if not editor:
            return

        # STORE CLOSED TAB STATE
        self.closed_tabs.append({
            "content": editor.toPlainText() if hasattr(editor, 'toPlainText') else "",
            "file_path": editor.file_path,
            "modified": editor.is_modified
        })

        if editor.is_modified:
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "This file has unsaved changes. Save before closing?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )

            if reply == QMessageBox.Yes:
                self.tabs.setCurrentIndex(index)
                self.save_file()

            elif reply == QMessageBox.Cancel:
                return

        self.tabs.removeTab(index)

        if self.tabs.count() == 0:
            self.new_tab()

    def reopen_closed_tab(self):
        if not self.closed_tabs:
            return

        tab_data = self.closed_tabs.pop()

        # Create the appropriate widget based on file type
        if tab_data["file_path"]:
            editor = create_viewer_widget(
                tab_data["file_path"],
                content=tab_data["content"]
            )
        else:
            from editor import EditorTab
            editor = EditorTab()

        editor.file_path = tab_data["file_path"]
        editor.is_modified = tab_data["modified"]

        if hasattr(editor, 'textChanged'):
            editor.textChanged.connect(
                lambda: self.update_tab_title(editor)
            )

        if editor.file_path:
            name = editor.file_path.split("/")[-1]
        else:
            name = "Untitled"

        if editor.is_modified:
            name += "*"

        index = self.tabs.addTab(editor, name)
        self.tabs.setCurrentIndex(index)

    def open_quick_switcher(self):
        """Open Ctrl+P quick switcher dialog."""
        recent = load_recent_files()
        pinned = load_pinned_files()
        
        switcher = QuickSwitcher(recent, pinned, self)
        switcher.file_selected.connect(self.open_recent_file)
        switcher.exec()

    def current_editor(self):
        return self.tabs.currentWidget()

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open File",
            "",
            "All Supported (*.md *.txt *.docx *.xlsx);;Word Documents (*.docx);;Excel Spreadsheets (*.xlsx);;Markdown (*.md);;Text Files (*.txt);;All Files (*.*)"
        )

        if not path:
            return

        try:
            # Create the appropriate viewer widget
            editor = create_viewer_widget(path)

            editor.textChanged.connect(
                lambda: self.update_tab_title(editor)
            )

            save_recent_file(path)
            self.update_menus()

            name = path.split("/")[-1]

            index = self.tabs.addTab(editor, name)

            self.tabs.setCurrentIndex(index)

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to open file: {str(e)}"
            )

    def open_recent_file(self, path):
        try:
            # Create the appropriate viewer widget
            editor = create_viewer_widget(path)

            editor.textChanged.connect(
                lambda: self.update_tab_title(editor)
            )

            name = path.split("/")[-1]

            index = self.tabs.addTab(editor, name)

            self.tabs.setCurrentIndex(index)

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to open file: {str(e)}"
            )

    def save_file(self):
        editor = self.current_editor()

        if not editor:
            return

        path = getattr(editor, "file_path", None)

        if not path:
            self.save_file_as()
            return

        try:
            # Get content using the appropriate method
            content = get_file_content(editor, path)

            # Write file based on type
            if isinstance(content, bytes):
                # Binary files (DOCX, XLSX)
                with open(path, "wb") as file:
                    file.write(content)
            else:
                # Text files
                with open(path, "w", encoding="utf-8") as file:
                    file.write(content)

            editor.is_modified = False
            self.update_tab_title(editor)

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to save file: {str(e)}"
            )

    def save_file_as(self):
        editor = self.current_editor()

        if not editor:
            return

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save File As",
            "",
            "Word Documents (*.docx);;Excel Spreadsheets (*.xlsx);;Markdown (*.md);;Text Files (*.txt);;All Files (*.*)"
        )

        if not path:
            return

        try:
            # Get content using the appropriate method
            content = get_file_content(editor, path)

            # Write file based on type
            if isinstance(content, bytes):
                # Binary files (DOCX, XLSX)
                with open(path, "wb") as file:
                    file.write(content)
            else:
                # Text files
                with open(path, "w", encoding="utf-8") as file:
                    file.write(content)

            editor.file_path = path
            editor.is_modified = False

            save_recent_file(path)
            self.update_menus()

            self.update_tab_title(editor)

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to save file: {str(e)}"
            )

    def update_recent_files_menu(self):
        self.recent_menu.clear()

        recent_files = load_recent_files(validate=True)

        if not recent_files:
            self.recent_menu.addAction("(no recent files)")
            return

        for path in recent_files:
            action = QAction(os.path.basename(path), self)
            action.setToolTip(path)
            action.triggered.connect(
                lambda checked=False, p=path:
                self.open_recent_file(p)
            )

            self.recent_menu.addAction(action)

    def update_pinned_files_menu(self):
        self.pinned_menu.clear()

        pinned_files = load_pinned_files()

        if not pinned_files:
            self.pinned_menu.addAction("(no pinned files)")
            return

        for path in pinned_files:
            action = QAction(os.path.basename(path), self)
            action.setToolTip(path)
            
            action.triggered.connect(
                lambda checked=False, p=path:
                self.open_recent_file(p)
            )

            self.pinned_menu.addAction(action)