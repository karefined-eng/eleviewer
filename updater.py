import os
import sys
import json
import urllib.request
import tempfile
import subprocess
from PySide6.QtCore import QThread, Signal, Qt, QUrl
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QTextEdit, QPushButton, QProgressBar, QMessageBox
)

REPO_OWNER = "karefined-eng"
REPO_NAME = "eleviewer"
CURRENT_VERSION = "1.3.0"  # Fallback current version

def parse_version(v_str: str):
    """Clean version string like 'v1.3.0' -> (1, 3, 0)."""
    v_str = v_str.lstrip("v").strip()
    parts = []
    for p in v_str.split("."):
        try:
            parts.append(int(p))
        except ValueError:
            parts.append(0)
    return tuple(parts)

class CheckUpdateThread(QThread):
    update_available = Signal(str, str, str)  # tag_name, release_notes, download_url
    no_update = Signal()
    error_occurred = Signal(str)

    def __init__(self, current_version=CURRENT_VERSION, parent=None):
        super().__init__(parent)
        self.current_version = current_version

    def run(self):
        url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/latest"
        req = urllib.request.Request(url, headers={"User-Agent": "EleViewer-AutoUpdater"})
        try:
            with urllib.request.urlopen(req, timeout=8) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode('utf-8'))
                    tag_name = data.get("tag_name", "v0.0.0")
                    body = data.get("body", "No release notes provided.")
                    
                    latest_ver = parse_version(tag_name)
                    curr_ver = parse_version(self.current_version)

                    if latest_ver > curr_ver:
                        download_url = ""
                        for asset in data.get("assets", []):
                            if asset.get("name", "").endswith(".exe"):
                                download_url = asset.get("browser_download_url", "")
                                break
                        if not download_url:
                            download_url = data.get("html_url", f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases")
                        
                        self.update_available.emit(tag_name, body, download_url)
                    else:
                        self.no_update.emit()
                else:
                    self.no_update.emit()
        except Exception as e:
            self.error_occurred.emit(str(e))



class UpdateDialog(QDialog):
    def __init__(self, tag_name, release_notes, download_url, parent=None):
        super().__init__(parent)
        self.download_url = download_url
        self.setWindowTitle(f"Update Available - {tag_name}")
        self.resize(500, 380)

        layout = QVBoxLayout(self)

        title = QLabel(f"🎉 A new version of EleViewer ({tag_name}) is available!")
        title.setStyleSheet("font-size: 15px; font-weight: bold; margin-bottom: 5px;")
        layout.addWidget(title)

        notes_label = QLabel("Release Notes:")
        notes_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(notes_label)

        self.notes_area = QTextEdit()
        self.notes_area.setReadOnly(True)
        self.notes_area.setMarkdown(release_notes)
        layout.addWidget(self.notes_area)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #666;")
        self.status_label.setVisible(False)
        layout.addWidget(self.status_label)

        btn_layout = QHBoxLayout()
        self.update_btn = QPushButton("🚀 Update Now")
        self.update_btn.setStyleSheet("background-color: #2563eb; color: white; font-weight: bold; padding: 8px 16px; border-radius: 6px;")
        self.update_btn.clicked.connect(self._start_download)

        self.cancel_btn = QPushButton("Remind Me Later")
        self.cancel_btn.clicked.connect(self.reject)

        btn_layout.addStretch()
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.update_btn)
        layout.addLayout(btn_layout)

    def _start_download(self):
        # SECURITY FIX: Silently downloading and executing .exe files without 
        # cryptographic hash validation or Authenticode signature checking 
        # is vulnerable to MITM attacks or repository asset compromises.
        # Fallback to opening the browser to the release page to let the OS
        # and browser handle secure downloads and SmartScreen validation.
        # ponytail: removed custom downloader -> use browser until hashes/signatures are in place.
        from PySide6.QtGui import QDesktopServices
        QDesktopServices.openUrl(QUrl(self.download_url))
        self.accept()

    def reject(self):
        super().reject()
