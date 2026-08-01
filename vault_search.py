import os
from pathlib import Path
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QListWidget, QListWidgetItem, 
    QLabel, QComboBox
)
from PySide6.QtCore import Qt, Signal, QTimer, QThread, QEvent
from theme import get_active_palette, get_brand_accent
from file_icons import file_type_icon
from settings import load_settings
from vault_indexer import search_index, schedule_vault_index


# FIX: search runs on QThread worker to prevent GUI thread freezing
# SECURITY: canonicalize paths to prevent symlink traversal
class VaultSearchWorker(QThread):
    result_found = Signal(str, str, str, str, str)  # filename, display_dir, vault_name, full_path, snippet

    def __init__(self, vaults_to_search, query):
        super().__init__()
        self.vaults_to_search = vaults_to_search
        self.query = query
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def run(self):
        query = self.query.strip().lower()
        if not query or self._is_cancelled:
            return

        seen_paths: set[str] = set()
        count = 0

        try:
            for filename, display_dir, vault_name, full_path, snippet in search_index(
                self.vaults_to_search, query, limit=100
            ):
                if self._is_cancelled or count >= 100:
                    break
                if full_path in seen_paths:
                    continue
                seen_paths.add(full_path)
                self.result_found.emit(filename, display_dir, vault_name, full_path, snippet)
                count += 1
        except Exception:
            pass

        if self._is_cancelled:
            return

        # Filename fallback for files not yet indexed
        for vault in self.vaults_to_search:
            if self._is_cancelled or count >= 100:
                break
            try:
                vault_resolved = Path(vault).resolve()
            except Exception:
                continue

            vault_str = str(vault_resolved)
            vault_name = vault_resolved.name
            for root, dirs, files in os.walk(vault_str, followlinks=False):
                if self._is_cancelled or count >= 100:
                    break
                abs_root = os.path.abspath(root)
                if not abs_root.startswith(vault_str):
                    dirs.clear()
                    continue

                dirs[:] = [d for d in dirs if not d.startswith(".")]

                for f in files:
                    if self._is_cancelled or count >= 100:
                        break
                    if f.startswith("."):
                        continue
                    if query not in f.lower():
                        continue
                    full_path = os.path.join(root, f)
                    abs_full_path = os.path.abspath(full_path)
                    if not abs_full_path.startswith(vault_str):
                        continue
                    if abs_full_path in seen_paths:
                        continue
                    seen_paths.add(abs_full_path)

                    rel_path = os.path.relpath(root, vault_str)
                    display_dir = "" if rel_path == "." else f" ({rel_path})"
                    self.result_found.emit(f, display_dir, vault_name, abs_full_path, "")
                    count += 1


class VaultSearchDialog(QDialog):
    file_selected = Signal(str)
    url_selected = Signal(str)

    def __init__(self, active_vault, all_vaults, parent=None):
        super().__init__(parent)
        self.active_vault = active_vault
        self.all_vaults = all_vaults
        self._search_worker = None
        
        self.setWindowTitle("Search in Vault")
        self.resize(600, 450)
        
        accent = get_brand_accent()
        p = get_active_palette()
        self.setStyleSheet(f"""
            QDialog {{ background: {p['BRAND_BACKGROUND']}; color: {p['BRAND_PRIMARY']}; }}
            QLineEdit {{ background: {p['BRAND_PANEL']}; color: {p['BRAND_PRIMARY']}; border: 1px solid {p['BRAND_BORDER']}; padding: 8px; font-size: 14px; selection-background-color: {accent}; }}
            QListWidget {{ background: {p['BRAND_PANEL']}; color: {p['BRAND_PRIMARY']}; border: 1px solid {p['BRAND_BORDER']}; outline: none; }}
            QListWidget::item {{ padding: 6px; border-bottom: 1px solid {p['BRAND_BORDER']}; }}
            QListWidget::item:selected {{ background: {accent}; color: {p['BRAND_BACKGROUND']}; }}
            QComboBox {{ background: {p['BRAND_PANEL']}; color: {p['BRAND_PRIMARY']}; border: 1px solid {p['BRAND_BORDER']}; padding: 4px; }}
            QComboBox QAbstractItemView {{ background: {p['BRAND_PANEL']}; color: {p['BRAND_PRIMARY']}; border: 1px solid {p['BRAND_BORDER']}; selection-background-color: {accent}; selection-color: {p['BRAND_BACKGROUND']}; }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        header_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search file names and content...")
        self.search_input.textChanged.connect(self._on_text_changed)
        
        self.scope_combo = QComboBox()
        self.scope_combo.addItem("Active Vault", "active")
        self.scope_combo.addItem("All Vaults", "all")
        self.scope_combo.currentIndexChanged.connect(self._do_search)
        
        settings = load_settings()
        if settings.get("file_search_scope") == "all_vaults":
            self.scope_combo.setCurrentIndex(1)
            
        header_layout.addWidget(self.search_input, stretch=1)
        header_layout.addWidget(self.scope_combo)
        
        self.results_list = QListWidget()
        self.results_list.itemDoubleClicked.connect(self._on_item_activated)
        
        layout.addLayout(header_layout)
        layout.addWidget(self.results_list)
        
        help_label = QLabel("↑↓ Navigate  Enter Select  Esc Cancel")
        help_label.setStyleSheet(f"color: {p['BRAND_MUTED_FG']}; font-size: 11px;")
        layout.addWidget(help_label)
        
        self.setLayout(layout)
        
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self._do_search)
        
        self.search_input.setFocus()

        vaults = [active_vault] if active_vault else all_vaults
        schedule_vault_index(vaults if vaults else all_vaults)
        
        # Pre-load for Omnibar
        self.all_files = []
        try:
            for v in (self.all_vaults if self.all_vaults else []):
                for root, dirs, files in os.walk(v):
                    dirs[:] = [d for d in dirs if not d.startswith(".")]
                    for f in files:
                        if not f.startswith("."):
                            self.all_files.append(os.path.join(root, f))
        except Exception:
            pass

        from bookmark_manager import load_bookmarks
        self.bookmarks = load_bookmarks(validate=False)
        
    def _on_text_changed(self):
        self.search_timer.start(300)
        
    def _do_search(self):
        query = self.search_input.text().lower()
        if self._search_worker and self._search_worker.isRunning():
            self._search_worker.cancel()
            try:
                self._search_worker.result_found.disconnect()
            except Exception:
                pass
            self._search_worker.wait(50)
            
        self.results_list.clear()
        if not query:
            return
            
        # 1. URL Detection
        if query.startswith("http://") or query.startswith("https://") or query.startswith("www."):
            item = QListWidgetItem(f"🌐 Open URL: {query}")
            url = query if query.startswith("http") else f"https://{query}"
            item.setData(Qt.UserRole, f"URL:{url}")
            self.results_list.addItem(item)
            
        # 2. Bookmarks Filter
        for b in self.bookmarks:
            label = b.get("label", "").lower()
            if query in label or query in b.get("file_path", "").lower():
                b_label = f"🔖 Bookmark: {b.get('label')} - {os.path.basename(b.get('file_path', ''))}"
                item = QListWidgetItem(b_label)
                item.setData(Qt.UserRole, f"BOOKMARK:{b.get('id')}:{b.get('file_path')}")
                self.results_list.addItem(item)
                
        # 3. Fuzzy File Title Search
        fuzzy_count = 0
        for path in self.all_files:
            if fuzzy_count > 20:
                break
            name = os.path.basename(path).lower()
            idx = 0
            for char in name:
                if idx < len(query) and char == query[idx]:
                    idx += 1
            if idx == len(query):
                item = QListWidgetItem(f"📄 {os.path.basename(path)} — {os.path.dirname(path)}")
                item.setData(Qt.UserRole, path)
                self.results_list.addItem(item)
                fuzzy_count += 1
            
        # 4. Background Full Text Search
        scope = self.scope_combo.currentData()
        vaults_to_search = [self.active_vault] if scope == "active" and self.active_vault else self.all_vaults
        
        self._search_worker = VaultSearchWorker(vaults_to_search, query)
        self._search_worker.result_found.connect(self._on_result_found)
        self._search_worker.start()

    def _on_result_found(self, f, display_dir, vault_name, full_path, snippet):
        label = f"{f}{display_dir} — [{vault_name}]"
        if snippet:
            label = f"{label}\n  {snippet}"
        item = QListWidgetItem(label)
        item.setData(Qt.UserRole, full_path)
        item.setIcon(file_type_icon(Path(f).suffix, 16))
        self.results_list.addItem(item)
                        
    def _on_item_activated(self, item):
        path = item.data(Qt.UserRole)
        if path.startswith("URL:"):
            self.url_selected.emit(path[4:])
        elif path.startswith("BOOKMARK:"):
            _, _, file_path = path.split(":", 2)
            self.file_selected.emit(file_path)
        else:
            self.file_selected.emit(path)
        self.accept()
        
    def _cleanup_worker(self):
        if self._search_worker and self._search_worker.isRunning():
            self._search_worker.cancel()
            self._search_worker.wait(500)

    def accept(self):
        self._cleanup_worker()
        super().accept()

    def reject(self):
        self._cleanup_worker()
        super().reject()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.reject()
        elif event.key() == Qt.Key_Return:
            if self.results_list.count() > 0:
                if not self.results_list.currentItem():
                    self.results_list.setCurrentRow(0)
                self._on_item_activated(self.results_list.currentItem())
        elif event.key() in (Qt.Key_Up, Qt.Key_Down):
            # Pass up/down to list widget if search has focus
            if self.search_input.hasFocus() and self.results_list.count() > 0:
                self.results_list.setFocus()
                if self.results_list.currentRow() == -1:
                    self.results_list.setCurrentRow(0)
                else:
                    self.results_list.keyPressEvent(event)
        else:
            super().keyPressEvent(event)

    def event(self, ev):
        if ev.type() == QEvent.WindowDeactivate:
            self.reject()
            return True
        return super().event(ev)
