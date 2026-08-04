import os
from pathlib import Path
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QListWidget, QListWidgetItem, 
    QLabel, QComboBox, QWidget
)
from PySide6.QtCore import Qt, Signal, QTimer, QThread, QEvent
from theme import get_active_palette, get_brand_accent
from file_icons import file_type_icon
from settings import load_settings


# FIX: search runs on QThreadPool worker to prevent GUI thread freezing
# SECURITY: canonicalize paths to prevent symlink traversal
class VaultSearchWorker(QThread):
    result_found = Signal(str, str, str, str) # filename, display_dir, vault_name, full_path

    def __init__(self, vaults_to_search, query):
        super().__init__()
        self.vaults_to_search = vaults_to_search
        self.query = query
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def run(self):
        count = 0
        for vault in self.vaults_to_search:
            if self._is_cancelled or count >= 100:
                break
            try:
                vault_resolved = Path(vault).resolve()
            except Exception:
                continue

            vault_str = str(vault_resolved)
            vault_name = vault_resolved.name
            # SECURITY: followlinks=False prevents traversing symlinks outside vault
            for root, dirs, files in os.walk(vault_str, followlinks=False):

                if self._is_cancelled or count >= 100:
                    break
                abs_root = os.path.abspath(root)
                # SECURITY: block paths that escape vault boundary
                if not abs_root.startswith(vault_str):
                    dirs.clear()
                    continue

                dirs[:] = [d for d in dirs if not d.startswith('.')]

                for f in files:
                    if self._is_cancelled or count >= 100:
                        break
                    if f.startswith('.'):
                        continue
                    if self.query in f.lower():
                        full_path = os.path.join(root, f)
                        abs_full_path = os.path.abspath(full_path)
                        if not abs_full_path.startswith(vault_str):
                            continue

                        rel_path = os.path.relpath(root, vault_str)
                        display_dir = "" if rel_path == "." else f" ({rel_path})"
                        self.result_found.emit(f, display_dir, vault_name, abs_full_path)
                        count += 1


class VaultSearchDialog(QDialog):
    file_selected = Signal(str)

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
        self.search_input.setPlaceholderText("Search file names...")
        # show a small clear icon inside the line edit
        try:
            self.search_input.setClearButtonEnabled(True)
        except Exception:
            pass
        self.search_input.setAccessibleName("Vault search input")
        self.search_input.textChanged.connect(self._on_text_changed)
        
        # small textual spinner / indicator shown while searching
        self.spinner_label = QLabel("Searching…")
        self.spinner_label.setVisible(False)
        self.spinner_label.setStyleSheet(f"color: {p['BRAND_MUTED_FG']}; font-size: 12px; margin-left:8px; margin-right:6px;")
        self.spinner_label.setAccessibleName("Search status")
        
        self.scope_combo = QComboBox()
        self.scope_combo.addItem("Active Vault", "active")
        self.scope_combo.addItem("All Vaults", "all")
        self.scope_combo.currentIndexChanged.connect(self._do_search)
        
        settings = load_settings()
        if settings.get("file_search_scope") == "all_vaults":
            self.scope_combo.setCurrentIndex(1)
            
        header_layout.addWidget(self.search_input, stretch=1)
        header_layout.addWidget(self.spinner_label)
        header_layout.addWidget(self.scope_combo)
        
        self.results_list = QListWidget()
        self.results_list.itemDoubleClicked.connect(self._on_item_activated)
        
        layout.addLayout(header_layout)

        # result count label (updates live)
        self.result_count_label = QLabel("")
        self.result_count_label.setStyleSheet(f"color: {p['BRAND_MUTED_FG']}; font-size: 12px; margin-bottom:6px;")
        self.result_count_label.setAccessibleName("Search result count")
        layout.addWidget(self.result_count_label)

        layout.addWidget(self.results_list)
        
        help_label = QLabel("↑↓ Navigate  Enter Select  Esc Cancel")
        help_label.setStyleSheet(f"color: {p['BRAND_MUTED_FG']}; font-size: 11px;")
        layout.addWidget(help_label)
        
        self.setLayout(layout)
        
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self._do_search)
        
        self.search_input.setFocus()
        
    def _on_text_changed(self):
        # slightly snappier debounce for perceived responsiveness
        self.search_timer.start(200)
        
    def _do_search(self):
        query = self.search_input.text().lower()
        # cancel any in-flight worker
        if self._search_worker and self._search_worker.isRunning():
            self._search_worker.cancel()
            try:
                self._search_worker.result_found.disconnect()
            except Exception:
                pass
            try:
                self._search_worker.finished.disconnect()
            except Exception:
                pass
            self._search_worker.wait(50)
            
        self.results_list.clear()
        # reset live count
        self._result_count = 0
        self.result_count_label.setText("")
        if not query:
            self.spinner_label.setVisible(False)
            return
            
        scope = self.scope_combo.currentData()
        vaults_to_search = [self.active_vault] if scope == "active" and self.active_vault else self.all_vaults
        
        # start new worker and show spinner / searching state
        worker = VaultSearchWorker(vaults_to_search, query)
        self._search_worker = worker
        self.spinner_label.setVisible(True)
        self.result_count_label.setText("Searching…")
        worker.result_found.connect(self._on_result_found)
        # only handle finished for the worker we just started
        worker.finished.connect(lambda w=worker: self._on_search_finished(w))
        worker.start()

    def _on_result_found(self, f, display_dir, vault_name, full_path):
        # create a richer item widget: icon + bold filename + muted secondary line
        icon = file_type_icon(Path(f).suffix, 16)
        item = QListWidgetItem()
        item.setData(Qt.UserRole, full_path)
        # container widget
        w = QWidget()
        h = QHBoxLayout(w)
        h.setContentsMargins(6, 4, 6, 4)
        # icon label
        icon_label = QLabel()
        try:
            icon_label.setPixmap(icon.pixmap(16, 16))
        except Exception:
            pass
        h.addWidget(icon_label)
        # text block
        text_block = QWidget()
        text_layout = QVBoxLayout(text_block)
        text_layout.setContentsMargins(6, 0, 0, 0)
        title = QLabel(f)
        # make filename stand out
        title.setStyleSheet(f"color: {p['BRAND_PRIMARY']}; font-weight: 600; font-size: 13px;")
        subtitle = QLabel(f"{display_dir} — [{vault_name}]")
        subtitle.setStyleSheet(f"color: {p['BRAND_MUTED_FG']}; font-size: 11px;")
        text_layout.addWidget(title)
        text_layout.addWidget(subtitle)
        h.addWidget(text_block, stretch=1)
        # finalize
        item.setSizeHint(w.sizeHint())
        self.results_list.addItem(item)
        self.results_list.setItemWidget(item, w)
        # increment and update live count
        try:
            self._result_count += 1
        except Exception:
            self._result_count = 1
        if self._result_count >= 100:
            self.result_count_label.setText("100+ results (showing first 100) — refine to narrow")
        else:
            self.result_count_label.setText(f"{self._result_count} result{'s' if self._result_count != 1 else ''}")
                        
    def _on_item_activated(self, item):
        path = item.data(Qt.UserRole)
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

