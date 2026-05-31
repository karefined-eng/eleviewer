from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QListWidget, QListWidgetItem, QLabel
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon
from pathlib import Path


class QuickSwitcher(QDialog):
    """
    Quick file switcher dialog (Ctrl+P).
    Fuzzy search over recent and pinned files.
    VSCode-style interface.
    """
    
    file_selected = Signal(str)  # Emits file path when selected
    
    def __init__(self, recent_files, pinned_files, parent=None):
        super().__init__(parent)
        
        self.recent_files = recent_files
        self.pinned_files = pinned_files
        self.all_files = list(dict.fromkeys(pinned_files + recent_files))  # Pinned first, deduplicated
        
        self.setWindowTitle("Quick Switcher")
        self.setStyleSheet("""
            QDialog {
                background: #1e1e1e;
                color: #fff;
            }
            QLineEdit {
                background: #2a2a2a;
                color: #fff;
                border: 1px solid #444;
                padding: 8px;
                font-size: 14px;
                selection-background-color: #0e47a1;
            }
            QListWidget {
                background: #2a2a2a;
                color: #fff;
                border: 1px solid #444;
            }
            QListWidget::item:selected {
                background: #0e47a1;
            }
            QListWidget::item:hover {
                background: #333;
            }
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
        help_label.setStyleSheet("color: #888; font-size: 11px; padding: 5px;")
        
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
        
        # Populate initial list
        self.populate_list(self.all_files)
        
        # Focus on search
        self.search_input.setFocus()
    
    def populate_list(self, files):
        """Populate the file list."""
        self.file_list.clear()
        
        for file_path in files:
            item = QListWidgetItem(Path(file_path).name)
            item.setData(Qt.UserRole, file_path)
            
            # Show pinned indicator
            if file_path in self.pinned_files:
                item.setText("📌 " + item.text())
            
            self.file_list.addItem(item)
        
        # Select first item
        if self.file_list.count() > 0:
            self.file_list.setCurrentRow(0)
    
    def filter_files(self):
        """Filter files based on search input (fuzzy match)."""
        search_text = self.search_input.text().lower().strip()
        
        if not search_text:
            # Show all files
            self.populate_list(self.all_files)
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
        if current_item:
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