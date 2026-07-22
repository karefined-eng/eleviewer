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
CURRENT_VERSION = "1.0.0"  # Fallback current version

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

class DownloadThread(QThread):
    progress = Signal(int)
    finished = Signal(str)
    failed = Signal(str)

    def __init__(self, download_url, parent=None):
        super().__init__(parent)
        self.download_url = download_url

    def run(self):
        try:
            req = urllib.request.Request(self.download_url, headers={"User-Agent": "EleViewer-AutoUpdater"})
            temp_dir = tempfile.gettempdir()
            dest_path = os.path.join(temp_dir, "EleViewer_Setup_Update.exe")

            with urllib.request.urlopen(req, timeout=30) as resp:
                total_size = int(resp.headers.get('Content-Length', 0))
                downloaded = 0
                block_size = 8192

                with open(dest_path, 'wb') as f:
                    while True:
                        buffer = resp.read(block_size)
                        if not buffer:
                            break
                        downloaded += len(buffer)
                        f.write(buffer)
                        if total_size > 0:
                            percent = int((downloaded / total_size) * 100)
                            self.progress.emit(percent)
            
            self.finished.emit(dest_path)
        except Exception as e:
            self.failed.emit(str(e))

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
        self.notes_area.setPlainText(release_notes)
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
        if self.download_url.endswith(".exe"):
            self.update_btn.setEnabled(False)
            self.cancel_btn.setEnabled(False)
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.status_label.setText("Downloading installer update...")
            self.status_label.setVisible(True)

            self.downloader = DownloadThread(self.download_url, self)
            self.downloader.progress.connect(self.progress_bar.setValue)
            self.downloader.finished.connect(self._on_download_finished)
            self.downloader.failed.connect(self._on_download_failed)
            self.downloader.start()
        else:
            # Fallback to browser download
            from PySide6.QtGui import QDesktopServices
            QDesktopServices.openUrl(QUrl(self.download_url))
            self.accept()

    def _on_download_finished(self, exe_path):
        self.status_label.setText("Starting installer...")
        try:
            subprocess.Popen([exe_path])
            sys.exit(0)
        except Exception as e:
            QMessageBox.critical(self, "Update Error", f"Failed to launch installer: {e}")
            self.reject()

    def _on_download_failed(self, reason):
        QMessageBox.warning(self, "Download Failed", f"Could not download update: {reason}\nOpening release page instead.")
        from PySide6.QtGui import QDesktopServices
        QDesktopServices.openUrl(QUrl(self.download_url))
        self.reject()
