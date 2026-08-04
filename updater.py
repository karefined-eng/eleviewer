import os
import sys
import json
import urllib.request
import tempfile
import subprocess
import hashlib
import re
from PySide6.QtCore import QThread, Signal, Qt, QUrl
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QTextBrowser, QPushButton, QProgressBar, QMessageBox
)
from PySide6.QtGui import QDesktopServices
import markdown

REPO_OWNER = "karefined-eng"
REPO_NAME = "eleviewer"
CURRENT_VERSION = "1.3.1"  # Fallback current version

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
    update_available = Signal(str, str, str, str)  # tag_name, release_notes, download_url, hash_url
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
                        hash_url = ""
                        for asset in data.get("assets", []):
                            name = asset.get("name", "").lower()
                            if name.endswith(".exe"):
                                download_url = asset.get("browser_download_url", "")
                            elif "sha256" in name or name.endswith(".hash") or name.endswith(".txt"):
                                hash_url = asset.get("browser_download_url", "")

                        if not download_url:
                            download_url = data.get("html_url", f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases")
                        
                        self.update_available.emit(tag_name, body, download_url, hash_url)
                    else:
                        self.no_update.emit()
                else:
                    self.no_update.emit()
        except Exception as e:
            self.error_occurred.emit(str(e))


class DownloadUpdateWorker(QThread):
    progress_changed = Signal(int)
    download_finished = Signal(str, bool, str)  # file_path, success, error_msg

    def __init__(self, download_url, hash_url="", parent=None):
        super().__init__(parent)
        self.download_url = download_url
        self.hash_url = hash_url

    def run(self):
        try:
            temp_dir = tempfile.gettempdir()
            filename = os.path.basename(self.download_url) or "EleViewer_Setup_Update.exe"
            dest_path = os.path.join(temp_dir, filename)

            # 1. Fetch expected hash if available
            expected_hash = None
            if self.hash_url:
                try:
                    req = urllib.request.Request(self.hash_url, headers={"User-Agent": "EleViewer-AutoUpdater"})
                    with urllib.request.urlopen(req, timeout=8) as h_resp:
                        h_content = h_resp.read().decode('utf-8', errors='ignore')
                        match = re.search(r'([a-fA-F0-9]{64})', h_content)
                        if match:
                            expected_hash = match.group(1).lower()
                except Exception as e:
                    print(f"[Updater] Warning: Could not fetch hash file: {e}")

            # 2. Download executable
            req = urllib.request.Request(self.download_url, headers={"User-Agent": "EleViewer-AutoUpdater"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                total_size = int(resp.headers.get('content-length', 0))
                downloaded = 0
                chunk_size = 65536
                sha256 = hashlib.sha256()

                with open(dest_path, "wb") as f:
                    while True:
                        chunk = resp.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        sha256.update(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = int((downloaded / total_size) * 100)
                            self.progress_changed.emit(percent)

            computed_hash = sha256.hexdigest().lower()

            # 3. Cryptographic Verification
            if expected_hash and computed_hash != expected_hash:
                try:
                    os.remove(dest_path)
                except Exception:
                    pass
                self.download_finished.emit(
                    "", False, 
                    f"Cryptographic hash mismatch!\nExpected: {expected_hash}\nComputed: {computed_hash}"
                )
                return

            self.download_finished.emit(dest_path, True, "")

        except Exception as e:
            self.download_finished.emit("", False, str(e))


class UpdateDialog(QDialog):
    def __init__(self, tag_name, release_notes, download_url, hash_url="", parent=None):
        super().__init__(parent)
        self.download_url = download_url
        self.hash_url = hash_url
        self.worker = None

        self.setWindowTitle(f"Update Available - {tag_name}")
        self.resize(500, 380)

        layout = QVBoxLayout(self)

        title = QLabel(f"🎉 A new version of EleViewer ({tag_name}) is available!")
        title.setStyleSheet("font-size: 15px; font-weight: bold; margin-bottom: 5px;")
        layout.addWidget(title)

        notes_label = QLabel("Release Notes:")
        notes_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(notes_label)

        self.notes_area = QTextBrowser()
        self.notes_area.setOpenExternalLinks(True)
        html_notes = markdown.markdown(release_notes)
        self.notes_area.setHtml(html_notes)
        layout.addWidget(self.notes_area)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        from theme import get_active_palette
        p = get_active_palette()
        self.status_label = QLabel("")
        self.status_label.setStyleSheet(f"color: {p['BRAND_MUTED_FG']};")
        self.status_label.setVisible(False)
        layout.addWidget(self.status_label)

        btn_layout = QHBoxLayout()
        from theme import get_brand_accent
        accent = get_brand_accent()
        self.update_btn = QPushButton("🚀 Update Now")
        self.update_btn.setStyleSheet(f"background-color: {accent}; color: white; font-weight: bold; padding: 8px 16px; border-radius: 6px;")
        self.update_btn.clicked.connect(self._start_download)

        self.cancel_btn = QPushButton("Remind Me Later")
        self.cancel_btn.clicked.connect(self.reject)

        btn_layout.addStretch()
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.update_btn)
        layout.addLayout(btn_layout)

    def _start_download(self):
        if not self.download_url.endswith(".exe"):
            # Fallback to browser if link is not a direct binary executable
            QDesktopServices.openUrl(QUrl(self.download_url))
            self.accept()
            return

        self.update_btn.setEnabled(False)
        self.cancel_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.status_label.setText("Downloading update securely...")
        self.status_label.setVisible(True)

        self.worker = DownloadUpdateWorker(self.download_url, self.hash_url, self)
        self.worker.progress_changed.connect(self.progress_bar.setValue)
        self.worker.download_finished.connect(self._on_download_finished)
        self.worker.start()

    def _on_download_finished(self, file_path, success, error_msg):
        if success and os.path.exists(file_path):
            self.status_label.setText("Launching installer...")
            try:
                if os.name == 'nt':
                    os.startfile(file_path)
                else:
                    subprocess.Popen([file_path])
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "Execution Error", f"Failed to launch installer:\n{e}")
                self.reject()
        else:
            QMessageBox.warning(
                self, "Download Failed", 
                f"Could not complete auto-update:\n{error_msg}\n\nOpening release page in browser instead."
            )
            QDesktopServices.openUrl(QUrl(self.download_url))
            self.reject()

    def reject(self):
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
        super().reject()
