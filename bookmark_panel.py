"""Sidebar panel listing saved document bookmarks."""

import os

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QMenu, QInputDialog, QMessageBox,
)
from PySide6.QtCore import Signal, Qt

from bookmark_manager import load_bookmarks, remove_bookmark, rename_bookmark


class BookmarkPanel(QWidget):
    bookmark_activated = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        header = QLabel("BOOKMARKS")
        header.setStyleSheet("color: #888; font-size: 11px; font-weight: bold; padding: 4px;")
        layout.addWidget(header)

        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("""
            QListWidget {
                background: #1e1e1e;
                color: #e0e0e0;
                border: none;
                font-size: 13px;
            }
            QListWidget::item { padding: 6px 4px; }
            QListWidget::item:selected { background: #094771; }
            QListWidget::item:hover { background: #2a2d2e; }
        """)
        self.list_widget.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self._show_context_menu)
        layout.addWidget(self.list_widget)

        self.refresh()

    def refresh(self):
        self.list_widget.clear()
        for bookmark in load_bookmarks():
            label = bookmark.get("label", "Bookmark")
            path = bookmark.get("file_path", "")
            name = os.path.basename(path) if path else "Unknown"
            page = bookmark.get("page_number", 0)
            suffix = f" · p.{page + 1}" if path.lower().endswith(".pdf") else ""
            item = QListWidgetItem(f"{label}\n{name}{suffix}")
            item.setData(Qt.UserRole, bookmark)
            item.setToolTip(path)
            self.list_widget.addItem(item)

    def _on_item_double_clicked(self, item):
        bookmark = item.data(Qt.UserRole)
        if bookmark:
            self.bookmark_activated.emit(bookmark)

    def _show_context_menu(self, pos):
        item = self.list_widget.itemAt(pos)
        if not item:
            return
        bookmark = item.data(Qt.UserRole)
        if not bookmark:
            return

        menu = QMenu(self)
        rename_action = menu.addAction("Rename...")
        delete_action = menu.addAction("Delete")
        action = menu.exec_(self.list_widget.mapToGlobal(pos))

        if action == rename_action:
            new_label, ok = QInputDialog.getText(
                self, "Rename Bookmark", "Label:",
                text=bookmark.get("label", ""),
            )
            if ok and new_label.strip():
                rename_bookmark(bookmark["id"], new_label.strip())
                self.refresh()
        elif action == delete_action:
            remove_bookmark(bookmark["id"])
            self.refresh()
