import json
import os
from datetime import datetime
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QListWidget, QListWidgetItem, 
    QPushButton, QLabel, QMenu, QWidget
)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QAction, QDesktopServices

from paths import APP_DATA_DIR
from icons import icon

DOWNLOADS_FILE = APP_DATA_DIR / "downloads.json"
MAX_DOWNLOADS = 1000

def load_downloads():
    if not DOWNLOADS_FILE.exists():
        return []
    try:
        with open(DOWNLOADS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_downloads(data):
    try:
        data = data[:MAX_DOWNLOADS]
        with open(DOWNLOADS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        import logging
        logging.getLogger("eleviewer").error(f"Failed to save downloads: {e}")

def track_download(file_name, file_path, url, status="Completed"):
    downloads = load_downloads()
    
    # Check if we are updating an existing active download by path
    existing = next((d for d in downloads if d.get("path") == str(file_path)), None)
    if existing:
        existing["status"] = status
        existing["timestamp"] = datetime.now().isoformat()
    else:
        downloads.insert(0, {
            "name": file_name,
            "path": str(file_path),
            "url": url,
            "status": status,
            "timestamp": datetime.now().isoformat()
        })
    
    save_downloads(downloads)

def clear_downloads():
    save_downloads([])

class DownloadItemWidget(QWidget):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Icon based on status/type
        icon_lbl = QLabel()
        if data.get("status") == "Failed":
            icon_lbl.setPixmap(icon("alert-circle", size=24).pixmap(24, 24))
        else:
            icon_lbl.setPixmap(icon("file", size=24).pixmap(24, 24))
        layout.addWidget(icon_lbl)
        
        # Text details
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        
        name_lbl = QLabel(f"<b>{data.get('name', 'Unknown')}</b>")
        name_lbl.setStyleSheet("font-size: 13px;")
        
        url_lbl = QLabel(data.get("url", ""))
        url_lbl.setStyleSheet("color: #9b9b96; font-size: 11px;")
        
        dt = datetime.fromisoformat(data.get("timestamp", datetime.now().isoformat()))
        status_lbl = QLabel(f"{dt.strftime('%Y-%m-%d %H:%M')} — {data.get('status', 'Completed')}")
        status_lbl.setStyleSheet("color: #9b9b96; font-size: 11px;")
        
        text_layout.addWidget(name_lbl)
        text_layout.addWidget(url_lbl)
        text_layout.addWidget(status_lbl)
        
        layout.addLayout(text_layout, 1)
        
        # Action button
        self.btn_action = QPushButton()
        if data.get("status") == "Completed" and os.path.exists(data.get("path", "")):
            self.btn_action.setText("Show in folder")
            self.btn_action.setIcon(icon("folder", size=14))
            self.btn_action.clicked.connect(self._show_in_folder)
        else:
            self.btn_action.setText("File missing" if data.get("status") == "Completed" else data.get("status", "Failed"))
            self.btn_action.setEnabled(False)
            
        layout.addWidget(self.btn_action)

    def _show_in_folder(self):
        path = self.data.get("path", "")
        if os.path.exists(path):
            import subprocess
            import sys
            if sys.platform == "win32":
                subprocess.Popen(f'explorer /select,"{path}"')

class DownloadsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Downloads")
        self.resize(600, 450)
        self._all_downloads = load_downloads()

        layout = QVBoxLayout(self)

        top_bar = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search downloads...")
        self.search_input.textChanged.connect(self._filter)
        self.search_input.setClearButtonEnabled(True)
        top_bar.addWidget(self.search_input, 1)

        self.btn_clear = QPushButton(icon("trash-2", size=14), "Clear List")
        self.btn_clear.clicked.connect(self._clear_all)
        top_bar.addWidget(self.btn_clear)
        
        layout.addLayout(top_bar)

        self.list_widget = QListWidget()
        self.list_widget.setAlternatingRowColors(True)
        self.list_widget.setSelectionMode(QListWidget.NoSelection)
        layout.addWidget(self.list_widget)

        self._populate_list(self._all_downloads)

    def _populate_list(self, data_list):
        self.list_widget.clear()
        for item_data in data_list:
            list_item = QListWidgetItem(self.list_widget)
            widget = DownloadItemWidget(item_data, self.list_widget)
            list_item.setSizeHint(widget.sizeHint())
            self.list_widget.addItem(list_item)
            self.list_widget.setItemWidget(list_item, widget)

    def _filter(self, text):
        query = text.lower()
        if not query:
            self._populate_list(self._all_downloads)
            return

        filtered = [
            item for item in self._all_downloads
            if query in item.get("name", "").lower() or query in item.get("url", "").lower()
        ]
        self._populate_list(filtered)

    def _clear_all(self):
        from PySide6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self, "Clear Downloads List", 
            "Are you sure you want to clear the downloads history? This will not delete the actual files.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            clear_downloads()
            self._all_downloads = []
            self._populate_list([])
