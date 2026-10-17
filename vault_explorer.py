"""Toggleable vault-style folder explorer with multi-vault support."""

import ctypes
import os
import shutil
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QLabel, QComboBox, QToolButton, QMenu, QInputDialog, QMessageBox,
)
from PySide6.QtCore import Signal, Qt, QSize
from PySide6.QtGui import QShortcut, QKeySequence

from icons import icon
from settings import (
    get_vault_paths, add_vault_path, remove_vault_path,
    set_active_vault_index, load_settings,
)
from theme import (
    compact_toolbar_stylesheet, ICON_SIZE_COMPACT, ICON_SIZE_VAULT_TREE,
    get_active_palette, get_brand_accent
)

SUPPORTED_EXTENSIONS = {".md", ".txt", ".pdf", ".docx", ".xlsx", ".csv"}

_INVALID_NAME_CHARS = set('<>:"/\\|?*')


def _send_to_recycle_bin(path):
    """Move a file or folder to the Windows Recycle Bin. Returns True on success."""
    if os.name != "nt":
        return False

    from ctypes import wintypes

    class SHFILEOPSTRUCTW(ctypes.Structure):
        _fields_ = [
            ("hwnd", wintypes.HWND),
            ("wFunc", ctypes.c_uint),
            ("pFrom", ctypes.c_wchar_p),
            ("pTo", ctypes.c_wchar_p),
            ("fFlags", ctypes.c_ushort),
            ("fAnyOperationsAborted", wintypes.BOOL),
            ("hNameMappings", ctypes.c_void_p),
            ("lpszProgressTitle", ctypes.c_wchar_p),
        ]

    FO_DELETE = 3
    FOF_ALLOWUNDO = 0x40
    FOF_NOCONFIRMATION = 0x10
    FOF_SILENT = 0x4
    FOF_NOERRORUI = 0x400

    op = SHFILEOPSTRUCTW()
    op.hwnd = None
    op.wFunc = FO_DELETE
    # pFrom must be double-null terminated; the struct marshaling adds one.
    op.pFrom = str(path) + "\0"
    op.pTo = None
    op.fFlags = FOF_ALLOWUNDO | FOF_NOCONFIRMATION | FOF_SILENT | FOF_NOERRORUI
    result = ctypes.windll.shell32.SHFileOperationW(ctypes.byref(op))
    return result == 0


class VaultExplorer(QWidget):
    file_opened = Signal(str)
    file_activated = Signal(str)
    search_requested = Signal(str)
    vaults_changed = Signal()
    # Emitted after a rename/copy/cut/delete with a {old_path: new_path or
    # None} map (None = deleted) so open tabs can be remapped or closed.
    files_changed = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._vault_paths = []
        self._active_index = 0
        self._show_all_files = False
        # Internal clipboard for copy/cut/paste: ("copy"|"cut", path)
        self._clip = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header_row = QHBoxLayout()
        header_row.setContentsMargins(4, 4, 4, 0)
        icon_sz = ICON_SIZE_COMPACT
        icon_qsize = QSize(icon_sz, icon_sz)

        self.vault_selector = QComboBox()
        self.vault_selector.currentIndexChanged.connect(self._on_vault_selected)

        self.btn_add = QToolButton()
        self.btn_add.setIconSize(icon_qsize)
        self.btn_add.setIcon(icon("plus", size=icon_sz))
        self.btn_add.setToolTip("Add vault")
        self.btn_add.setAutoRaise(True)

        self.btn_refresh = QToolButton()
        self.btn_refresh.setIconSize(icon_qsize)
        self.btn_refresh.setIcon(icon("rotate-cw", size=icon_sz))
        self.btn_refresh.setToolTip("Refresh vault")
        self.btn_refresh.setAutoRaise(True)
        self.btn_refresh.clicked.connect(self.refresh_active_vault)

        self.btn_search = QToolButton()
        self.btn_search.setIconSize(icon_qsize)
        self.btn_search.setIcon(icon("search", size=icon_sz))
        self.btn_search.setToolTip("Search vault")
        self.btn_search.setAutoRaise(True)
        self.btn_search.clicked.connect(self._emit_search)

        header_row.addWidget(self.vault_selector, stretch=1)
        header_row.addWidget(self.btn_search)
        header_row.addWidget(self.btn_refresh)
        header_row.addWidget(self.btn_add)

        self.tree = QTreeWidget()
        self.tree.setIconSize(QSize(ICON_SIZE_VAULT_TREE, ICON_SIZE_VAULT_TREE))
        self.tree.setHeaderHidden(True)
        self.tree.setAnimated(True)
        self.tree.setIndentation(16)
        self.tree.itemExpanded.connect(self._on_item_expanded)
        self.tree.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.tree.itemSelectionChanged.connect(self._on_tree_selection_changed)

        # Right-click and keyboard file operations (issue #101)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self._show_context_menu)
        for seq, handler in (
            ("F2", self._rename_selected),
            ("Delete", self._delete_selected),
            ("Ctrl+C", self._copy_selected),
            ("Ctrl+X", self._cut_selected),
            ("Ctrl+V", self._paste_selected),
        ):
            shortcut = QShortcut(QKeySequence(seq), self.tree)
            shortcut.setContext(Qt.WidgetWithChildrenShortcut)
            shortcut.activated.connect(handler)

        layout.addLayout(header_row)
        layout.addWidget(self.tree)
        self.apply_theme()

    def apply_theme(self):
        p = get_active_palette()
        accent = get_brand_accent()
        self.vault_selector.setStyleSheet(
            f"QComboBox {{ background: {p['BRAND_PANEL_2']}; color: {p['BRAND_PRIMARY']}; border: 1px solid {p['BRAND_BORDER']}; padding: 4px; }} "
            f"QComboBox QAbstractItemView {{ background: {p['BRAND_PANEL']}; color: {p['BRAND_PRIMARY']}; border: 1px solid {p['BRAND_BORDER']}; selection-background-color: {accent}; selection-color: {p['BRAND_BACKGROUND']}; }}"
        )
        ct_sheet = compact_toolbar_stylesheet()
        self.btn_add.setStyleSheet(ct_sheet)
        self.btn_refresh.setStyleSheet(ct_sheet)
        self.btn_search.setStyleSheet(ct_sheet)
        self.tree.setStyleSheet(f"""
            QTreeWidget {{
                background: {p['BRAND_PANEL']};
                color: {p['BRAND_PRIMARY']};
                border: none;
                font-size: 13px;
                outline: none;
            }}
            QTreeWidget::item {{ padding: 5px 6px; border-left: 2px solid transparent; }}
            QTreeWidget::item:selected {{ background: {p['BRAND_PANEL_2']}; border-left: 2px solid {accent}; color: {p['TAB_SELECTED_FG']}; font-weight: bold; }}
            QTreeWidget::item:hover:!selected {{ background: {p['BRAND_PANEL_2']}; }}
        """)

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

    def refresh_active_vault(self):
        idx = self.vault_selector.currentIndex()
        if idx >= 0:
            self._on_vault_selected(idx)

    def _emit_search(self):
        vault_path = self.vault_selector.currentData()
        if vault_path:
            self.search_requested.emit(vault_path)

    def _load_vault_tree(self, path):
        self.tree.clear()
        root = Path(path)
        root_item = QTreeWidgetItem([root.name or str(root)])
        root_item.setData(0, Qt.UserRole, str(root))
        root_item.setData(0, Qt.UserRole + 1, "dir")
        from icons import icon
        from theme import ICON_SIZE_COMPACT
        root_item.setIcon(0, icon("folder", size=ICON_SIZE_COMPACT, color="#888888"))
        self.tree.addTopLevelItem(root_item)
        self._populate_dir(root_item, str(root))
        root_item.setExpanded(True)

    def _should_show_file(self, name):
        if self._show_all_files:
            return True
        return Path(name).suffix.lower() in SUPPORTED_EXTENSIONS

    # SECURITY: canonicalize paths to prevent symlink traversal
    def _populate_dir(self, parent_item, dir_path):
        try:
            entries = sorted(os.scandir(dir_path), key=lambda e: (not e.is_dir(), e.name.lower()))
        except PermissionError:
            return

        vault_root_resolved = None
        if self._vault_paths and 0 <= self._active_index < len(self._vault_paths):
            try:
                vault_root_resolved = Path(self._vault_paths[self._active_index]).resolve()
            except Exception:
                vault_root_resolved = None

        from icons import icon
        from file_icons import file_type_icon
        from theme import ICON_SIZE_COMPACT
        
        SYSTEM_IGNORED_FILES = {"desktop.ini", "_desktop.ini", "thumbs.db", ".ds_store", "$recycle.bin"}
        for entry in entries:
            name_lower = entry.name.lower()
            if entry.name.startswith(".") or name_lower in SYSTEM_IGNORED_FILES or name_lower.startswith("_desktop.ini"):
                continue
            if vault_root_resolved:
                try:
                    resolved_entry = Path(entry.path).resolve()
                    if not str(resolved_entry).startswith(str(vault_root_resolved)):
                        continue
                except Exception:
                    continue

            if entry.is_dir():
                child = QTreeWidgetItem([entry.name])
                child.setData(0, Qt.UserRole, entry.path)
                child.setData(0, Qt.UserRole + 1, "dir")
                child.setIcon(0, icon("folder", size=ICON_SIZE_COMPACT, color="#888888"))
                parent_item.addChild(child)
                placeholder = QTreeWidgetItem(["…"])
                placeholder.setData(0, Qt.UserRole + 1, "placeholder")
                child.addChild(placeholder)
            elif self._should_show_file(entry.name):
                child = QTreeWidgetItem([entry.name])
                child.setData(0, Qt.UserRole, entry.path)
                child.setData(0, Qt.UserRole + 1, "file")
                ext = Path(entry.name).suffix
                child.setIcon(0, file_type_icon(ext, size=ICON_SIZE_COMPACT))
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

    def _on_tree_selection_changed(self):
        from file_icons import file_type_icon
        from icons import icon
        from theme import ICON_SIZE_COMPACT
        if getattr(self, "_last_selected_tree_item", None):
            old = self._last_selected_tree_item
            try:
                if old.data(0, Qt.UserRole + 1) == "file":
                    ext = Path(old.text(0)).suffix
                    old.setIcon(0, file_type_icon(ext, size=ICON_SIZE_COMPACT, active=False))
                elif old.data(0, Qt.UserRole + 1) == "dir":
                    old.setIcon(0, icon("folder", size=ICON_SIZE_COMPACT, color="#888888"))
            except RuntimeError:
                pass

        selected = self.tree.selectedItems()
        if selected:
            new_item = selected[0]
            self._last_selected_tree_item = new_item
            if new_item.data(0, Qt.UserRole + 1) == "file":
                ext = Path(new_item.text(0)).suffix
                new_item.setIcon(0, file_type_icon(ext, size=ICON_SIZE_COMPACT, active=True))
            elif new_item.data(0, Qt.UserRole + 1) == "dir":
                new_item.setIcon(0, icon("folder", size=ICON_SIZE_COMPACT, color="#6cb6ff"))
        else:
            self._last_selected_tree_item = None

    # ── File operations (rename / copy / cut / paste / delete / new folder) ──

    def _active_vault_root(self):
        if self._vault_paths and 0 <= self._active_index < len(self._vault_paths):
            try:
                return Path(self._vault_paths[self._active_index]).resolve()
            except Exception:
                return None
        return None

    def _is_inside_vault(self, path):
        """Containment check that blocks operations on paths outside the vault
        (mirrors the symlink-traversal guard used when listing files)."""
        root = self._active_vault_root()
        if root is None or not path:
            return False
        try:
            target = Path(path).resolve()
        except Exception:
            return False
        return root == target or root in target.parents

    def _is_vault_root(self, path):
        root = self._active_vault_root()
        try:
            return root is not None and Path(path).resolve() == root
        except Exception:
            return False

    def _selected_item_info(self):
        """Return (path, kind) for the current tree selection, or (None, None)."""
        item = self.tree.currentItem()
        if item is None:
            return None, None
        kind = item.data(0, Qt.UserRole + 1)
        path = item.data(0, Qt.UserRole)
        if kind not in ("file", "dir") or not path:
            return None, None
        return path, kind

    def _show_context_menu(self, pos):
        item = self.tree.itemAt(pos)
        if item is None:
            return
        path = item.data(0, Qt.UserRole)
        kind = item.data(0, Qt.UserRole + 1)
        if kind not in ("file", "dir") or not path:
            return

        menu = QMenu(self)
        if kind == "dir":
            menu.addAction("New Folder", lambda: self._new_folder(path))
            menu.addSeparator()
        menu.addAction("Rename", lambda: self._rename_item(path))
        menu.addAction("Copy", lambda: self._clip_item("copy", path))
        menu.addAction("Cut", lambda: self._clip_item("cut", path))
        if kind == "dir" and self._clip:
            menu.addAction("Paste", lambda: self._paste_into(path))
        menu.addSeparator()
        menu.addAction("Delete", lambda: self._delete_item(path))
        menu.exec(self.tree.viewport().mapToGlobal(pos))

    # Keyboard handlers operate on the current selection.
    def _rename_selected(self):
        path, kind = self._selected_item_info()
        if path and kind:
            self._rename_item(path)

    def _delete_selected(self):
        path, kind = self._selected_item_info()
        if path and kind:
            self._delete_item(path)

    def _copy_selected(self):
        path, _kind = self._selected_item_info()
        if path:
            self._clip_item("copy", path)

    def _cut_selected(self):
        path, _kind = self._selected_item_info()
        if path:
            self._clip_item("cut", path)

    def _paste_selected(self):
        path, kind = self._selected_item_info()
        if not path:
            return
        # Pasting with a file selected drops it next to the file.
        dest_dir = path if kind == "dir" else str(Path(path).parent)
        self._paste_into(dest_dir)

    def _ask_valid_name(self, title, label, current=""):
        """Ask for a file/folder name; returns None unless valid and unique-checked later."""
        name, ok = QInputDialog.getText(self, title, label, text=current)
        if not ok:
            return None
        name = name.strip()
        if not name or name in (".", ".."):
            QMessageBox.warning(self, "Invalid Name", "Please enter a name.")
            return None
        if any(ch in _INVALID_NAME_CHARS for ch in name):
            QMessageBox.warning(
                self, "Invalid Name",
                "Names can't contain any of these characters:\n< > : \" / \\ | ? *",
            )
            return None
        return name

    def _new_folder(self, dir_path):
        if not self._is_inside_vault(dir_path):
            return
        name = self._ask_valid_name("New Folder", "Folder name:")
        if name is None:
            return
        new_path = Path(dir_path) / name
        if new_path.exists():
            QMessageBox.warning(self, "Folder Exists", "A folder with that name already exists here.")
            return
        try:
            new_path.mkdir()
        except OSError as error:
            QMessageBox.warning(self, "Folder Not Created", f"Couldn't create the folder:\n{error}")
            return
        self._refresh_and_notify({})

    def _rename_item(self, path):
        if not self._is_inside_vault(path) or self._is_vault_root(path):
            return
        old_path = Path(path)
        new_name = self._ask_valid_name("Rename", "New name:", current=old_path.name)
        if new_name is None or new_name == old_path.name:
            return
        new_path = old_path.with_name(new_name)
        if new_path.exists():
            QMessageBox.warning(self, "Name Already Used", "Something with that name already exists here.")
            return
        try:
            os.rename(old_path, new_path)
        except OSError as error:
            QMessageBox.warning(self, "Rename Failed", f"Couldn't rename:\n{error}")
            return
        self._refresh_and_notify({str(old_path): str(new_path)})

    def _clip_item(self, op, path):
        if self._is_inside_vault(path) and not self._is_vault_root(path):
            self._clip = (op, path)

    def _unique_destination(self, dest_dir, name):
        """Return dest_dir/name, or 'name (2)', 'name (3)'… if taken."""
        stem = Path(name).stem
        suffix = Path(name).suffix
        candidate = Path(dest_dir) / name
        counter = 2
        while candidate.exists():
            candidate = Path(dest_dir) / f"{stem} ({counter}){suffix}"
            counter += 1
        return candidate

    def _paste_into(self, dir_path):
        if not self._clip or not self._is_inside_vault(dir_path):
            return
        op, src = self._clip
        src_path = Path(src)
        if not src_path.exists():
            self._clip = None
            return
        dest_dir = Path(dir_path)
        if src_path == dest_dir or dest_dir in src_path.parents:
            QMessageBox.warning(self, "Can't Paste Here", "A folder can't be pasted into itself.")
            return
        target = self._unique_destination(dest_dir, src_path.name)
        try:
            if op == "copy":
                if src_path.is_dir():
                    shutil.copytree(src_path, target)
                else:
                    shutil.copy2(src_path, target)
            else:
                shutil.move(str(src_path), str(target))
                self._clip = None
        except OSError as error:
            QMessageBox.warning(self, "Paste Failed", f"Couldn't paste the item:\n{error}")
            return
        changes = {str(src_path): str(target)} if op == "cut" else {}
        self._refresh_and_notify(changes)

    def _delete_item(self, path):
        if not self._is_inside_vault(path) or self._is_vault_root(path):
            return
        name = Path(path).name
        confirm = QMessageBox.question(
            self, "Delete",
            f"Send '{name}' to the Recycle Bin?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
        )
        if confirm != QMessageBox.Yes:
            return
        if not _send_to_recycle_bin(path):
            QMessageBox.warning(
                self, "Delete Failed",
                "Couldn't delete it. The file may be open in another program.",
            )
            return
        self._refresh_and_notify({path: None})

    def _refresh_and_notify(self, changes):
        """Reload the tree, then tell the main window which paths moved (None = deleted)."""
        self.refresh_active_vault()
        self.files_changed.emit(changes)
