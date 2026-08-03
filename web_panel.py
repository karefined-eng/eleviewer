"""Minimalist native web launcher replacing the heavy Chromium WebEngine."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QLabel, QPushButton, QFrame
)
from PySide6.QtCore import Signal, Qt, QUrl, QTimer, QRect
from PySide6.QtGui import QDesktopServices

import os
import sys
import subprocess
import ctypes
import uuid

user32 = ctypes.windll.user32

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
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        p = get_active_palette()
        accent = get_brand_accent()

        # Header containing the URL bar
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(10, 10, 10, 10)
        header.setStyleSheet(f"background: {p['BRAND_PANEL_2']}; border-bottom: 1px solid {p['BRAND_BORDER']};")
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Search or enter web address...")
        self.url_input.setStyleSheet(f"""
            QLineEdit {{
                background: {p['BRAND_PANEL']};
                color: {p['BRAND_PRIMARY']};
                border: 1px solid {p['BRAND_BORDER']};
                border-radius: 4px;
                padding: 8px;
                font-size: 13px;
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
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {p['BRAND_ACCENT_HOVER'] if 'BRAND_ACCENT_HOVER' in p else accent};
            }}
        """)
        btn_go.clicked.connect(self._on_url_entered)

        header_layout.addWidget(self.url_input, 1)
        header_layout.addWidget(btn_go)

        # The container for the embedded webview
        self.container = QFrame()
        self.container.setStyleSheet(f"background: {p['BRAND_PANEL']};")
        self.container.setFocusPolicy(Qt.StrongFocus)
        self.container_hwnd = int(self.container.winId())

        layout.addWidget(header)
        layout.addWidget(self.container, 1)

        self._webview_proc = None
        self._webview_hwnd = 0
        self._poll_timer = QTimer(self)
        self._poll_timer.timeout.connect(self._poll_for_window)
        self._target_window_title = ""

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
        
        self.url_input.setText(url_str)
        
        # Kill previous instance if exists
        if self._webview_proc:
            try:
                self._webview_proc.terminate()
                self._webview_proc.wait(timeout=1)
            except Exception:
                pass
            self._webview_proc = None
            self._webview_hwnd = 0

        # Spawn new webview worker
        self._target_window_title = f"EleViewer-Web-{uuid.uuid4().hex}"
        worker_path = os.path.join(os.path.dirname(__file__), "webview_worker.py")
        
        self._webview_proc = subprocess.Popen(
            [sys.executable, "--webview-worker", self._target_window_title, url_str],
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        # Start polling to capture the window
        self._poll_timer.start(50)

    def _poll_for_window(self):
        if not self._target_window_title:
            self._poll_timer.stop()
            return
            
        hwnd = user32.FindWindowW(None, self._target_window_title)
        if hwnd:
            self._poll_timer.stop()
            self._webview_hwnd = hwnd
            
            # Reparent the window into our QFrame
            user32.SetParent(hwnd, self.container_hwnd)
            
            # Strip window styles to make it a seamless child widget
            GWL_STYLE = -16
            WS_CAPTION = 0x00C00000
            WS_THICKFRAME = 0x00040000
            WS_POPUP = 0x80000000
            WS_CHILD = 0x40000000
            
            style = user32.GetWindowLongW(hwnd, GWL_STYLE)
            style = (style & ~WS_CAPTION & ~WS_THICKFRAME & ~WS_POPUP) | WS_CHILD
            user32.SetWindowLongW(hwnd, GWL_STYLE, style)
            
            # Force initial resize
            self._resize_embedded_window()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._resize_embedded_window()

    def _resize_embedded_window(self):
        if self._webview_hwnd:
            rect = self.container.rect()
            # MoveWindow handles positioning and resizing relative to the parent QFrame
            user32.MoveWindow(self._webview_hwnd, 0, 0, rect.width(), rect.height(), True)

    def closeEvent(self, event):
        if self._webview_proc:
            try:
                self._webview_proc.terminate()
            except Exception:
                pass
        super().closeEvent(event)

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
