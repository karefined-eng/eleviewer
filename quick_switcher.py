from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QListWidget, QListWidgetItem, QLabel
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QColor
from pathlib import Path
from theme import BRAND_BACKGROUND, BRAND_PANEL, BRAND_BORDER, BRAND_PRIMARY, BRAND_MUTED, BRAND_MUTED_FG, get_brand_accent
from file_icons import file_type_icon


class QuickSwitcher(QDialog):
    """
    Quick file switcher dialog (Ctrl+P).
    Fuzzy search over recent and pinned files.
    VSCode-style interface.
    """
    
    file_selected = Signal(str)  # Emits file path when selected
    
    def __init__(self, recent_files, pinned_files, open_tabs=None, parent=None):
        super().__init__(parent)
        
        self.recent_files = recent_files
        self.pinned_files = pinned_files
        self.open_tabs = open_tabs or []
        
        self.all_files = []
        seen = set()
        for lst in [self.open_tabs, self.pinned_files, self.recent_files]:
            for f in lst:
                if f not in seen:
                    self.all_files.append(f)
                    seen.add(f)
        
        self.setWindowTitle("Quick Switcher")
        accent = get_brand_accent()
        self.setStyleSheet(f"""
            QDialog {{
                background: {BRAND_BACKGROUND};
                color: {BRAND_PRIMARY};
            }}
            QLineEdit {{
                background: {BRAND_PANEL};
                color: {BRAND_PRIMARY};
                border: 1px solid {BRAND_BORDER};
                padding: 8px;
                font-size: 14px;
                selection-background-color: {accent};
            }}
            QListWidget {{
                background: {BRAND_PANEL};
                color: {BRAND_PRIMARY};
                border: 1px solid {BRAND_BORDER};
            }}
            QListWidget::item:selected {{
                background: {accent};
                color: {BRAND_BACKGROUND};
            }}
            QListWidget::item:hover {{
                background: {BRAND_MUTED};
            }}
        """)
        
        self.resize(600, 400)
        
        layout = QVBoxLayout()
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search files (type to filter)...")
        self.search_input.textChanged.connect(self.filter_files)
        self.search_input.returnPressed.connect(self.select_current)
        
        # Help text
        help_label = QLabel("↑↓ Navigate  Enter Select  Esc Cancel")
        help_label.setStyleSheet(f"color: {BRAND_MUTED_FG}; font-size: 11px; padding: 5px;")
        
        # File list
        self.file_list = QListWidget()
        self.file_list.itemDoubleClicked.connect(self.on_item_selected)
        self.file_list.keyPressEvent = self.list_key_press
        
        layout.addWidget(self.search_input)
        layout.addWidget(self.file_list)
        layout.addWidget(help_label)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.setLayout(layout)
        
        # Populate initial list with sections
        self.populate_list(self.all_files, show_sections=True)
        
        # Focus on search
        self.search_input.setFocus()
    
    def populate_list(self, files, show_sections=False):
        """Populate the file list."""
        self.file_list.clear()
        
        if show_sections:
            groups = [
                ("📂 Open Tabs", [f for f in files if f in self.open_tabs]),
                ("📌 Pinned", [f for f in files if f in self.pinned_files and f not in self.open_tabs]),
                ("🕐 Recent", [f for f in files if f in self.recent_files and f not in self.open_tabs and f not in self.pinned_files])
            ]
            
            for header, group_files in groups:
                if not group_files: continue
                h_item = QListWidgetItem(header)
                h_item.setFlags(h_item.flags() & ~Qt.ItemIsSelectable)
                h_item.setForeground(QColor(BRAND_MUTED_FG))
                self.file_list.addItem(h_item)
                
                for f in group_files:
                    item = QListWidgetItem("   " + Path(f).name)
                    item.setData(Qt.UserRole, f)
                    ext = Path(f).suffix
                    item.setIcon(file_type_icon(ext, 16))
                    self.file_list.addItem(item)
        else:
            for file_path in files:
                item = QListWidgetItem(Path(file_path).name)
                item.setData(Qt.UserRole, file_path)
                ext = Path(file_path).suffix
                item.setIcon(file_type_icon(ext, 16))
                if file_path in self.open_tabs:
                    item.setText("📂 " + item.text())
                elif file_path in self.pinned_files:
                    item.setText("📌 " + item.text())
                self.file_list.addItem(item)
        
        # Select first selectable item
        for i in range(self.file_list.count()):
            if self.file_list.item(i).flags() & Qt.ItemIsSelectable:
                self.file_list.setCurrentRow(i)
                break
    
    def filter_files(self):
        """Filter files based on search input (fuzzy match)."""
        search_text = self.search_input.text().lower().strip()
        
        if not search_text:
            # Show all files with sections
            self.populate_list(self.all_files, show_sections=True)
            return
        
        # Fuzzy filter
        filtered = []
        for file_path in self.all_files:
            file_name = Path(file_path).name.lower()
            # Simple fuzzy: all search chars appear in filename in order
            search_idx = 0
            for char in file_name:
                if search_idx < len(search_text) and char == search_text[search_idx]:
                    search_idx += 1
            
            if search_idx == len(search_text):
                filtered.append(file_path)
        
        self.populate_list(filtered)
    
    def select_current(self):
        """Select the currently highlighted item."""
        current_item = self.file_list.currentItem()
        if current_item and (current_item.flags() & Qt.ItemIsSelectable):
            self.on_item_selected(current_item)
    
    def on_item_selected(self, item):
        """Handle file selection."""
        file_path = item.data(Qt.UserRole)
        self.file_selected.emit(file_path)
        self.accept()
    
    def list_key_press(self, event):
        """Handle key presses in file list."""
        if event.key() == Qt.Key_Escape:
            self.reject()
        elif event.key() == Qt.Key_Return:
            self.select_current()
        else:
            # Delegate to original
            QListWidget.keyPressEvent(self.file_list, event)
    
    def keyPressEvent(self, event):
        """Handle top-level key presses."""
        if event.key() == Qt.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)