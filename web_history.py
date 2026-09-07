import json
import os
from datetime import datetime
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QListWidget, QListWidgetItem, 
    QPushButton, QLabel, QMenu
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction

from paths import APP_DATA_DIR
from icons import icon

HISTORY_FILE = APP_DATA_DIR / "web_history.json"
MAX_HISTORY_ITEMS = 2000

def load_history():
    if not HISTORY_FILE.exists():
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_history(history_data):
    try:
        # Keep only the latest MAX_HISTORY_ITEMS
        history_data = history_data[:MAX_HISTORY_ITEMS]
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        import logging
        logging.getLogger("eleviewer").error(f"Failed to save history: {e}")

def track_visit(url, title):
    # Don't track internal pages or empty urls
    if not url or url.startswith("about:") or url.startswith("chrome:") or url.startswith("devtools:"):
        return

    history = load_history()
    
    # If the exact same URL was visited last, just update its timestamp/title instead of duplicating
    if history and history[0].get("url") == url:
        history[0]["title"] = title or history[0].get("title", url)
        history[0]["timestamp"] = datetime.now().isoformat()
    else:
        history.insert(0, {
            "url": url,
            "title": title or url,
            "timestamp": datetime.now().isoformat()
        })
    
    save_history(history)

def clear_history():
    save_history([])

class HistoryDialog(QDialog):
    url_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Browser History")
        self.resize(700, 500)
        self._all_history = load_history()

        layout = QVBoxLayout(self)

        # Top bar
        top_bar = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search history...")
        self.search_input.textChanged.connect(self._filter_history)
        self.search_input.setClearButtonEnabled(True)
        top_bar.addWidget(self.search_input, 1)

        self.btn_clear = QPushButton(icon("trash-2", size=14), "Clear Browsing Data")
        self.btn_clear.clicked.connect(self._clear_all)
        top_bar.addWidget(self.btn_clear)

        layout.addLayout(top_bar)

        # List widget
        self.list_widget = QListWidget()
        self.list_widget.setAlternatingRowColors(True)
        self.list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self._show_context_menu)
        self.list_widget.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.list_widget.setStyleSheet(
            "QListWidget { font-size: 13px; }"
            "QListWidget::item { padding: 8px; }"
        )
        layout.addWidget(self.list_widget)

        self._populate_list(self._all_history)

    def _populate_list(self, history_data):
        self.list_widget.clear()
        for item in history_data:
            dt = datetime.fromisoformat(item["timestamp"])
            date_str = dt.strftime("%Y-%m-%d %H:%M")
            title = item.get("title", item.get("url", ""))
            
            # Format: [Date] Title (URL)
            display_text = f"{date_str}   {title}\n{item['url']}"
            
            list_item = QListWidgetItem(display_text)
            list_item.setData(Qt.UserRole, item["url"])
            list_item.setIcon(icon("globe", size=16))
            self.list_widget.addItem(list_item)

    def _filter_history(self, text):
        query = text.lower()
        if not query:
            self._populate_list(self._all_history)
            return

        filtered = [
            item for item in self._all_history
            if query in item.get("title", "").lower() or query in item.get("url", "").lower()
        ]
        self._populate_list(filtered)

    def _clear_all(self):
        from PySide6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self, "Clear History", 
            "Are you sure you want to delete all browser history?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            clear_history()
            self._all_history = []
            self._populate_list([])

    def _on_item_double_clicked(self, item):
        url = item.data(Qt.UserRole)
        if url:
            self.url_requested.emit(url)
            self.accept()

    def _show_context_menu(self, pos):
        item = self.list_widget.itemAt(pos)
        if not item:
            return
            
        url = item.data(Qt.UserRole)
        if not url:
            return

        menu = QMenu(self)
        
        act_open = QAction(icon("external-link", size=14), "Open in New Tab", self)
        act_open.triggered.connect(lambda: self._open_url(url))
        menu.addAction(act_open)
        
        act_copy = QAction(icon("copy", size=14), "Copy Link", self)
        act_copy.triggered.connect(lambda: self._copy_url(url))
        menu.addAction(act_copy)

        menu.exec(self.list_widget.mapToGlobal(pos))

    def _open_url(self, url):
        self.url_requested.emit(url)
        self.accept()
        
    def _copy_url(self, url):
        from PySide6.QtWidgets import QApplication
        QApplication.clipboard().setText(url)
