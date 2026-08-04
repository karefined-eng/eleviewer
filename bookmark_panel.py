"""Sidebar panel listing saved document bookmarks."""

import os

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QMenu, QInputDialog, QToolButton,
)
from PySide6.QtCore import Signal, Qt, QSize

from bookmark_manager import load_bookmarks, remove_bookmark, rename_bookmark
from icons import icon
from theme import compact_toolbar_stylesheet, get_brand_accent


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
        
        from theme import get_active_palette
        p = get_active_palette()
        c_prim = p["BRAND_PRIMARY"]
        c_muted = p["BRAND_MUTED_FG"]
        self.lbl_text = QLabel(f"<span style='color:{c_prim}; font-weight:bold;'>{label}</span><br><span style='color:{c_muted}; font-size:11px;'>{name}{suffix}</span>")
        self.lbl_text.setTextFormat(Qt.RichText)
        
        self.btn_edit = QToolButton()
        self.btn_edit.setIcon(icon("pencil", size=14))
        self.btn_edit.setToolTip("Rename Bookmark")
        self.btn_edit.setStyleSheet(compact_toolbar_stylesheet())
        self.btn_edit.clicked.connect(self._on_edit)
        
        self.btn_del = QToolButton()
        self.btn_del.setIcon(icon("square", size=14))
        self.btn_del.setText("X")
        self.btn_del.setToolTip("Delete Bookmark")
        self.btn_del.setStyleSheet(f"QToolButton {{ color: {p['BRAND_ERROR']}; font-weight: bold; padding: 2px; border:none; }} QToolButton:hover {{ background: {p['BRAND_PANEL_2']}; }}")
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

        self.header = QLabel("BOOKMARKS")
        layout.addWidget(self.header)

        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self._show_context_menu)
        layout.addWidget(self.list_widget)

        self.empty_label = QLabel("No bookmarks yet.\nPress Ctrl+D in a document to add one.")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setWordWrap(True)
        layout.addWidget(self.empty_label)

        self.reload_theme()
        self.refresh()

    def reload_theme(self):
        from theme import get_active_palette, get_brand_accent
        p = get_active_palette()
        accent = get_brand_accent()
        self.setStyleSheet(f"background-color: {p['BRAND_PANEL']}; color: {p['BRAND_PRIMARY']};")
        self.header.setStyleSheet(f"color: {p['BRAND_MUTED_FG']}; font-size: 11px; font-weight: bold; padding: 4px;")
        self.empty_label.setStyleSheet(f"color: {p['BRAND_MUTED_FG']}; font-size: 12px; padding: 10px;")
        self.list_widget.setStyleSheet(f"""
            QListWidget {{
                background: {p['BRAND_PANEL']};
                color: {p['BRAND_PRIMARY']};
                border: none;
                font-size: 13px;
                outline: none;
            }}
            QListWidget::item {{ 
                padding: 6px; 
                margin: 2px 4px; 
                border-radius: 6px; 
                border: 1px solid transparent;
            }}
            QListWidget::item:selected {{ 
                background: {p['BRAND_PANEL_2']}; 
                border: 1px solid {accent}; 
            }}
            QListWidget::item:hover:!selected {{ 
                background: {p['BRAND_BACKGROUND']}; 
            }}
        """)


    def refresh(self):
        self.list_widget.clear()
        bookmarks = load_bookmarks()
        
        if not bookmarks:
            self.list_widget.hide()
            self.empty_label.show()
        else:
            self.list_widget.show()
            self.empty_label.hide()
            
            for bookmark in bookmarks:
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
