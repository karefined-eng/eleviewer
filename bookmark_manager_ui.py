from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QHeaderView, QAbstractItemView, QMessageBox,
    QToolButton, QMenu, QInputDialog
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

from bookmark_manager import load_bookmarks, remove_bookmark, rename_bookmark, export_bookmarks_html
from theme import compact_toolbar_stylesheet
from icons import icon
from file_icons import file_type_icon
import os

class BookmarkManagerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Bookmark Manager")
        self.resize(800, 500)
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Toolbar
        toolbar = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search bookmarks...")
        self.search_input.textChanged.connect(self._filter_table)
        
        self.btn_export = QPushButton("Export HTML...")
        self.btn_export.setIcon(icon("download", size=14))
        self.btn_export.clicked.connect(self._export)

        self.btn_del = QPushButton("Delete Selected")
        self.btn_del.setIcon(icon("trash-2", size=14))
        self.btn_del.clicked.connect(self._delete_selected)

        toolbar.addWidget(self.search_input)
        toolbar.addWidget(self.btn_export)
        toolbar.addWidget(self.btn_del)
        layout.addLayout(toolbar)

        # Table
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Name", "URL / Path", "Type", "Added"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSortingEnabled(True)
        self.table.verticalHeader().setVisible(False)
        self.table.doubleClicked.connect(self._edit_selected)
        layout.addWidget(self.table)

    def refresh(self):
        self.table.setSortingEnabled(False)
        self.table.setRowCount(0)
        self.bookmarks = load_bookmarks()
        
        for idx, b in enumerate(self.bookmarks):
            self.table.insertRow(idx)
            
            # Name
            item_name = QTableWidgetItem(b.get("label", "Unnamed"))
            item_name.setData(Qt.UserRole, b)
            
            # URL
            path = b.get("file_path", "")
            item_url = QTableWidgetItem(path)
            
            # Type / Icon
            is_web = path.startswith(("http://", "https://"))
            type_str = "Web" if is_web else "Document"
            item_type = QTableWidgetItem(type_str)
            if is_web:
                item_type.setIcon(icon("globe", size=16))
            else:
                ext = os.path.splitext(path)[1].lower() if path else ".txt"
                item_type.setIcon(file_type_icon(ext or ".txt", size=16))
                
            # Date
            created = b.get("created_at", "")[:10]
            item_date = QTableWidgetItem(created)

            self.table.setItem(idx, 0, item_name)
            self.table.setItem(idx, 1, item_url)
            self.table.setItem(idx, 2, item_type)
            self.table.setItem(idx, 3, item_date)
            
        self.table.setSortingEnabled(True)

    def _filter_table(self, text):
        text = text.lower()
        for i in range(self.table.rowCount()):
            name = self.table.item(i, 0).text().lower()
            url = self.table.item(i, 1).text().lower()
            match = text in name or text in url
            self.table.setRowHidden(i, not match)

    def _delete_selected(self):
        rows = set(item.row() for item in self.table.selectedItems())
        if not rows: return
        reply = QMessageBox.question(self, "Confirm Delete", f"Are you sure you want to delete {len(rows)} bookmarks?")
        if reply == QMessageBox.Yes:
            for row in sorted(rows, reverse=True):
                b = self.table.item(row, 0).data(Qt.UserRole)
                remove_bookmark(b["id"])
            self.refresh()

    def _edit_selected(self):
        items = self.table.selectedItems()
        if not items: return
        row = items[0].row()
        b = self.table.item(row, 0).data(Qt.UserRole)
        
        new_label, ok = QInputDialog.getText(self, "Edit Bookmark", "Name:", text=b.get("label", ""))
        if ok and new_label.strip():
            rename_bookmark(b["id"], new_label.strip())
            self.refresh()

    def _export(self):
        from PySide6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getSaveFileName(self, "Export Bookmarks", "", "HTML Files (*.html)")
        if path:
            try:
                export_bookmarks_html(path)
                QMessageBox.information(self, "Export Successful", f"Bookmarks exported to {path}")
            except Exception as e:
                QMessageBox.warning(self, "Export Failed", str(e))
