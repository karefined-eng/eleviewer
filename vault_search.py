import os
from pathlib import Path
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QListWidget, QListWidgetItem, 
    QLabel, QComboBox
)
from PySide6.QtCore import Qt, Signal, QTimer
from theme import BRAND_BACKGROUND, BRAND_PANEL, BRAND_BORDER, BRAND_PRIMARY, BRAND_MUTED, BRAND_MUTED_FG, get_brand_accent
from file_icons import file_type_icon
from settings import load_settings

class VaultSearchDialog(QDialog):
    file_selected = Signal(str)

    def __init__(self, active_vault, all_vaults, parent=None):
        super().__init__(parent)
        self.active_vault = active_vault
        self.all_vaults = all_vaults
        
        self.setWindowTitle("Search in Vault")
        self.resize(600, 450)
        
        accent = get_brand_accent()
        self.setStyleSheet(f"""
            QDialog {{ background: {BRAND_BACKGROUND}; color: {BRAND_PRIMARY}; }}
            QLineEdit {{ background: {BRAND_PANEL}; color: {BRAND_PRIMARY}; border: 1px solid {BRAND_BORDER}; padding: 8px; font-size: 14px; selection-background-color: {accent}; }}
            QListWidget {{ background: {BRAND_PANEL}; color: {BRAND_PRIMARY}; border: 1px solid {BRAND_BORDER}; outline: none; }}
            QListWidget::item {{ padding: 4px; }}
            QListWidget::item:selected {{ background: {accent}; color: {BRAND_BACKGROUND}; }}
            QComboBox {{ background: {BRAND_PANEL}; color: {BRAND_PRIMARY}; border: 1px solid {BRAND_BORDER}; padding: 4px; }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        header_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search file names...")
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
        help_label.setStyleSheet(f"color: {BRAND_MUTED_FG}; font-size: 11px;")
        layout.addWidget(help_label)
        
        self.setLayout(layout)
        
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self._do_search)
        
        self.search_input.setFocus()
        
    def _on_text_changed(self):
        self.search_timer.start(300)
        
    def _do_search(self):
        query = self.search_input.text().lower()
        if not query:
            self.results_list.clear()
            return
            
        scope = self.scope_combo.currentData()
        vaults_to_search = [self.active_vault] if scope == "active" and self.active_vault else self.all_vaults
        
        self.results_list.clear()
        
        # Debounced fast filename search (FTS5 full content search deferred to v1.4.0)
        for vault in vaults_to_search:
            vault_name = Path(vault).name
            for root, dirs, files in os.walk(vault):
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                for f in files:
                    if f.startswith('.'): continue
                    if query in f.lower():
                        full_path = os.path.join(root, f)
                        rel_path = os.path.relpath(root, vault)
                        display_dir = "" if rel_path == "." else f" ({rel_path})"
                        
                        item = QListWidgetItem(f"{f}{display_dir} — [{vault_name}]")
                        item.setData(Qt.UserRole, full_path)
                        item.setIcon(file_type_icon(Path(f).suffix, 16))
                        self.results_list.addItem(item)
                        
                        if self.results_list.count() > 100:
                            break # Limit to 100 results for UI responsiveness
                
                if self.results_list.count() > 100:
                    break
                        
    def _on_item_activated(self, item):
        path = item.data(Qt.UserRole)
        self.file_selected.emit(path)
        self.accept()
        
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
