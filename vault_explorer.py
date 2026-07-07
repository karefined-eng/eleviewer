"""Toggleable vault-style folder explorer with multi-vault support."""

import os
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QLabel, QComboBox, QToolButton,
)
from PySide6.QtCore import Signal, Qt, QSize

from icons import icon
from settings import (
    get_vault_paths, add_vault_path, remove_vault_path,
    set_active_vault_index, load_settings,
)
from theme import compact_toolbar_stylesheet, ICON_SIZE_COMPACT, ICON_SIZE_VAULT_TREE

SUPPORTED_EXTENSIONS = {".md", ".txt", ".pdf", ".docx", ".xlsx", ".csv"}


class VaultExplorer(QWidget):
    file_opened = Signal(str)
    vaults_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._vault_paths = []
        self._active_index = 0
        self._show_all_files = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header_row = QHBoxLayout()
        header_row.setContentsMargins(4, 4, 4, 0)
        icon_sz = ICON_SIZE_COMPACT
        icon_qsize = QSize(icon_sz, icon_sz)

        self.vault_selector = QComboBox()
        self.vault_selector.setStyleSheet(
            "QComboBox { background: #2a2a2a; color: #fff; border: 1px solid #444; padding: 4px; }"
        )
        self.vault_selector.currentIndexChanged.connect(self._on_vault_selected)

        self.btn_add = QToolButton()
        self.btn_add.setIconSize(icon_qsize)
        self.btn_add.setIcon(icon("plus", size=icon_sz))
        self.btn_add.setToolTip("Add vault")
        self.btn_add.setStyleSheet(compact_toolbar_stylesheet())
        self.btn_add.setAutoRaise(True)

        header_row.addWidget(self.vault_selector, stretch=1)
        header_row.addWidget(self.btn_add)

        self.tree = QTreeWidget()
        self.tree.setIconSize(QSize(ICON_SIZE_VAULT_TREE, ICON_SIZE_VAULT_TREE))
        self.tree.setHeaderHidden(True)
        self.tree.setAnimated(True)
        self.tree.setIndentation(16)
        self.tree.setStyleSheet("""
            QTreeWidget {
                background: #1e1e1e;
                color: #e0e0e0;
                border: none;
                font-size: 13px;
            }
            QTreeWidget::item { padding: 4px 2px; }
            QTreeWidget::item:selected { background: #094771; }
            QTreeWidget::item:hover { background: #2a2d2e; }
        """)
        self.tree.itemExpanded.connect(self._on_item_expanded)
        self.tree.itemDoubleClicked.connect(self._on_item_double_clicked)

        layout.addLayout(header_row)
        layout.addWidget(self.tree)

    def set_show_all_files(self, show_all):
        self._show_all_files = show_all
        if self._vault_paths:
            self._load_vault_tree(self._vault_paths[self._active_index])

    def restore_from_settings(self):
        settings = load_settings()
        self._show_all_files = settings.get("vault_show_all_files", False)
        self._vault_paths = get_vault_paths()
        self._active_index = min(
            settings.get("active_vault_index", 0),
            max(len(self._vault_paths) - 1, 0),
        )
        self._refresh_selector()
        if self._vault_paths:
            self._load_vault_tree(self._vault_paths[self._active_index])

    def add_vault(self, path):
        if not path or not os.path.isdir(path):
            return
        add_vault_path(path)
        self._vault_paths = get_vault_paths()
        self._active_index = 0
        self._refresh_selector()
        self._load_vault_tree(path)
        self.vaults_changed.emit()

    def remove_current_vault(self):
        if not self._vault_paths:
            return
        path = self._vault_paths[self._active_index]
        remove_vault_path(path)
        self._vault_paths = get_vault_paths()
        self._active_index = min(self._active_index, max(len(self._vault_paths) - 1, 0))
        self._refresh_selector()
        if self._vault_paths:
            self._load_vault_tree(self._vault_paths[self._active_index])
        else:
            self.tree.clear()
        self.vaults_changed.emit()

    def _refresh_selector(self):
        self.vault_selector.blockSignals(True)
        self.vault_selector.clear()
        for p in self._vault_paths:
            self.vault_selector.addItem(Path(p).name or p, p)
        if self._vault_paths:
            self.vault_selector.setCurrentIndex(self._active_index)
        self.vault_selector.blockSignals(False)

    def _on_vault_selected(self, index):
        if index < 0 or index >= len(self._vault_paths):
            return
        self._active_index = index
        set_active_vault_index(index)
        self._load_vault_tree(self._vault_paths[index])

    def _load_vault_tree(self, path):
        self.tree.clear()
        root = Path(path)
        root_item = QTreeWidgetItem([root.name or str(root)])
        root_item.setData(0, Qt.UserRole, str(root))
        root_item.setData(0, Qt.UserRole + 1, "dir")
        self.tree.addTopLevelItem(root_item)
        self._populate_dir(root_item, str(root))
        root_item.setExpanded(True)

    def _should_show_file(self, name):
        if self._show_all_files:
            return True
        return Path(name).suffix.lower() in SUPPORTED_EXTENSIONS

    def _populate_dir(self, parent_item, dir_path):
        try:
            entries = sorted(os.scandir(dir_path), key=lambda e: (not e.is_dir(), e.name.lower()))
        except PermissionError:
            return

        for entry in entries:
            if entry.name.startswith("."):
                continue
            if entry.is_dir():
                child = QTreeWidgetItem([entry.name])
                child.setData(0, Qt.UserRole, entry.path)
                child.setData(0, Qt.UserRole + 1, "dir")
                parent_item.addChild(child)
                placeholder = QTreeWidgetItem(["…"])
                placeholder.setData(0, Qt.UserRole + 1, "placeholder")
                child.addChild(placeholder)
            elif self._should_show_file(entry.name):
                child = QTreeWidgetItem([entry.name])
                child.setData(0, Qt.UserRole, entry.path)
                child.setData(0, Qt.UserRole + 1, "file")
                parent_item.addChild(child)

    def _on_item_expanded(self, item):
        if item.data(0, Qt.UserRole + 1) != "dir":
            return
        path = item.data(0, Qt.UserRole)
        if not path:
            return
        if item.childCount() == 1 and item.child(0).data(0, Qt.UserRole + 1) == "placeholder":
            item.removeChild(item.child(0))
            self._populate_dir(item, path)

    def _on_item_double_clicked(self, item, column):
        if item is None:
            return
        if item.data(0, Qt.UserRole + 1) == "file":
            path = item.data(0, Qt.UserRole)
            if path:
                self.file_opened.emit(path)
