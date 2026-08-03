"""Minimalist native web launcher replacing the heavy Chromium WebEngine."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QLabel, QPushButton
)
from PySide6.QtCore import Signal, Qt, QUrl
from PySide6.QtGui import QDesktopServices

from theme import get_active_palette, get_brand_accent
from settings import load_settings, save_settings

WEB_AVAILABLE = True

class WebPanel(QWidget):
    tabs_changed = Signal()
    expand_requested = Signal()
    url_changed = Signal(str)
    title_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 40, 20, 20)
        
        p = get_active_palette()
        accent = get_brand_accent()

        title = QLabel("Web Launcher")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {p['BRAND_PRIMARY']};")
        
        desc = QLabel("Enter a URL or search query to open in your system browser.")
        desc.setAlignment(Qt.AlignCenter)
        desc.setStyleSheet(f"color: {p['BRAND_MUTED_FG']}; margin-bottom: 20px;")

        search_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Search or enter web address...")
        self.url_input.setStyleSheet(f"""
            QLineEdit {{
                background: {p['BRAND_PANEL_2']};
                color: {p['BRAND_PRIMARY']};
                border: 1px solid {p['BRAND_BORDER']};
                border-radius: 6px;
                padding: 12px;
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border: 1px solid {accent};
            }}
        """)
        self.url_input.returnPressed.connect(self._on_url_entered)
        
        btn_go = QPushButton("Go")
        btn_go.setCursor(Qt.PointingHandCursor)
        btn_go.setStyleSheet(f"""
            QPushButton {{
                background: {accent};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 20px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                opacity: 0.9;
            }}
        """)
        btn_go.clicked.connect(self._on_url_entered)

        search_layout.addWidget(self.url_input, 1)
        search_layout.addWidget(btn_go)

        layout.addStretch()
        layout.addWidget(title)
        layout.addWidget(desc)
        layout.addLayout(search_layout)
        layout.addStretch()

        # Dummy attributes to prevent AttributeError from ui.py
        self.tabs = _DummyTabs()

    def _on_url_entered(self):
        url = self.url_input.text().strip()
        if not url: return
        self.open_url_in_new_tab(url)
        self.url_input.clear()

    def open_url_in_new_tab(self, url_str, title="Web"):
        if not url_str.startswith(("http://", "https://", "file://")):
            if "." in url_str and " " not in url_str:
                url_str = "https://" + url_str
            else:
                import urllib.parse
                url_str = "https://duckduckgo.com/?q=" + urllib.parse.quote(url_str)
        QDesktopServices.openUrl(QUrl(url_str))
        
        # ponytail: internal history disabled -> native OS browser tracks history.

    def add_tab(self, url=None, title="New Tab"):
        if url:
            self.open_url_in_new_tab(url, title)
        else:
            self.url_input.setFocus()

    def reload_url(self, url_str):
        pass

    def _close_tab(self, index):
        pass

    def persist_tabs(self):
        pass
        
    def _bookmark_current(self):
        pass

class _DummyTabs:
    def count(self): return 0
    def currentIndex(self): return 0
