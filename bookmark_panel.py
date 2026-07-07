"""Sidebar panel listing saved document bookmarks."""

import os

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QMenu, QInputDialog, QToolButton,
)
from PySide6.QtCore import Signal, Qt, QSize

from bookmark_manager import load_bookmarks, remove_bookmark, rename_bookmark
from icons import icon
from theme import compact_toolbar_stylesheet


class BookmarkItemWidget(QWidget):
    def __init__(self, bookmark, parent_panel):
        super().__init__()
        self.bookmark = bookmark
        self.parent_panel = parent_panel

        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        label = bookmark.get("label", "Bookmark")
        path = bookmark.get("file_path", "")
        name = os.path.basename(path) if path else "Unknown"
        page = bookmark.get("page_number", 0)
        suffix = f" · p.{page + 1}" if path.lower().endswith(".pdf") else ""
        
        self.lbl_text = QLabel(f"<b>{label}</b><br><span style='color:#aaa'>{name}{suffix}</span>")
        self.lbl_text.setTextFormat(Qt.RichText)
        
        self.btn_edit = QToolButton()
        self.btn_edit.setIcon(icon("pencil", size=14))
        self.btn_edit.setToolTip("Rename Bookmark")
        self.btn_edit.setStyleSheet(compact_toolbar_stylesheet())
        self.btn_edit.clicked.connect(self._on_edit)
        
        self.btn_del = QToolButton()
        self.btn_del.setIcon(icon("square", size=14)) # fallback, maybe use eraser or trash if we had it, but pencil and square are available. Wait, I can just use a simple text 'x' if no trash icon exists, but wait, do we have a trash icon? Let's check our icon set. I'll just use the eraser icon or text "X". Or I can use 'eraser' icon.
        self.btn_del.setText("X")
        self.btn_del.setToolTip("Delete Bookmark")
        self.btn_del.setStyleSheet("QToolButton { color: #f44336; font-weight: bold; padding: 2px; border:none; } QToolButton:hover { background: #550000; }")
        self.btn_del.clicked.connect(self._on_delete)

        layout.addWidget(self.lbl_text, stretch=1)
        layout.addWidget(self.btn_edit)
        layout.addWidget(self.btn_del)

    def _on_edit(self):
        from PySide6.QtWidgets import (
            QDialog, QFormLayout, QLineEdit, QSpinBox,
            QDialogButtonBox, QVBoxLayout
        )
        dlg = QDialog(self)
        dlg.setWindowTitle("Edit Bookmark")
        dlg.setMinimumWidth(320)
        form = QFormLayout()

        label_edit = QLineEdit(self.bookmark.get("label", ""))
        page_spin = QSpinBox()
        page_spin.setRange(1, 999999)
        page_spin.setValue(self.bookmark.get("page_number", 0) + 1)  # display 1-indexed

        form.addRow("Label:", label_edit)
        form.addRow("Target Page:", page_spin)

        btns = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        btns.accepted.connect(dlg.accept)
        btns.rejected.connect(dlg.reject)

        layout = QVBoxLayout(dlg)
        layout.addLayout(form)
        layout.addWidget(btns)

        if dlg.exec():
            new_label = label_edit.text().strip() or self.bookmark.get("label", "")
            new_page = page_spin.value() - 1  # store 0-indexed
            from bookmark_manager import rename_bookmark, update_bookmark
            rename_bookmark(self.bookmark["id"], new_label)
            update_bookmark(self.bookmark["id"], page_number=new_page)
            self.parent_panel.refresh()

    def _on_delete(self):
        remove_bookmark(self.bookmark["id"])
        self.parent_panel.refresh()


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
            QListWidget::item { padding: 2px; }
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
            item = QListWidgetItem()
            item.setData(Qt.UserRole, bookmark)
            item.setToolTip(bookmark.get("file_path", ""))
            
            widget = BookmarkItemWidget(bookmark, self)
            item.setSizeHint(widget.sizeHint())
            
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, widget)

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
        action = menu.exec(self.list_widget.mapToGlobal(pos))

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
