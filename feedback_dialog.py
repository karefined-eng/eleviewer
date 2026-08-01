import json
import os
import sys
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QTextEdit, 
    QPushButton, QMessageBox
)
from PySide6.QtCore import QThread, Signal
import urllib.request
from theme import get_brand_accent, get_active_palette
from paths import strip_pii

APP_VERSION = "1.3.0"

# FIX: HTTP POST moved to QThread to prevent 10s GUI freeze on timeout
class FeedbackSubmitThread(QThread):
    finished_signal = Signal(bool, str)
    success = Signal(str)
    error = Signal(str)

    def __init__(self, data):
        super().__init__()
        self.data = data
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True
        self.requestInterruption()

    def run(self):
        if self._is_cancelled:
            return
        try:
            req = urllib.request.Request(
                "https://eleviewer.vercel.app/api/feedback", 
                data=json.dumps(self.data).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                if self._is_cancelled:
                    return
                if response.status == 200:
                    raw_msg = response.read().decode()
                    msg = "Your feedback was sent successfully! Thank you."
                    if raw_msg:
                        try:
                            data = json.loads(raw_msg)
                            if isinstance(data, dict) and data.get("issue_number"):
                                msg = f"Your feedback was sent successfully! (Issue #{data['issue_number']})"
                        except Exception:
                            pass
                            
                    self.finished_signal.emit(True, msg)
                    self.success.emit(msg)
                else:
                    msg = f"Server returned status code {response.status}"
                    self.finished_signal.emit(False, msg)
                    self.error.emit(msg)
        except Exception as e:
            if not self._is_cancelled:
                self.finished_signal.emit(False, str(e))
                self.error.emit(str(e))



FeedbackSubmitWorker = FeedbackSubmitThread  # Alias for backward compatibility


class FeedbackDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Report Issue / Feedback")
        self.resize(500, 400)
        self._submit_thread = None
        
        p = get_active_palette()
        accent = get_brand_accent()
        self.setStyleSheet(f"""
            QDialog {{ background: {p['BRAND_BACKGROUND']}; color: {p['BRAND_PRIMARY']}; }}
            QLabel {{ color: {p['BRAND_PRIMARY']}; }}
            QComboBox, QTextEdit {{ background: {p['BRAND_PANEL']}; color: {p['BRAND_PRIMARY']}; border: 1px solid {p['BRAND_BORDER']}; padding: 6px; selection-background-color: {accent}; }}
            QComboBox QAbstractItemView {{ background: {p['BRAND_PANEL']}; color: {p['BRAND_PRIMARY']}; border: 1px solid {p['BRAND_BORDER']}; selection-background-color: {accent}; selection-color: {p['BRAND_BACKGROUND']}; outline: none; }}
            QComboBox::item {{ color: {p['BRAND_PRIMARY']}; }}
            QComboBox::item:selected {{ color: {p['BRAND_BACKGROUND']}; background-color: {accent}; }}
            QPushButton {{ background: {p['BRAND_PANEL']}; color: {p['BRAND_PRIMARY']}; border: 1px solid {p['BRAND_BORDER']}; padding: 6px 12px; border-radius: 4px; }}
            QPushButton:hover {{ background: {accent}; color: {p['BRAND_BACKGROUND']}; }}
            QPushButton#submitBtn {{ background: {accent}; color: {p['BRAND_BACKGROUND']}; font-weight: bold; }}
            QPushButton#submitBtn:hover {{ opacity: 0.8; }}
        """)
        
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel("Type:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Bug", "Feature Request", "Friction Point"])
        layout.addWidget(self.type_combo)
        
        layout.addWidget(QLabel("Description:"))
        self.desc_edit = QTextEdit()
        self.desc_edit.setPlaceholderText("Please describe the issue or idea...")
        layout.addWidget(self.desc_edit)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        self.submit_btn = QPushButton("Submit")
        self.submit_btn.setObjectName("submitBtn")
        self.submit_btn.clicked.connect(self.submit)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(self.submit_btn)
        
        layout.addLayout(btn_layout)
        
    def submit(self):
        desc = self.desc_edit.toPlainText().strip()
        if not desc:
            QMessageBox.warning(self, "Error", "Description cannot be empty.")
            return
            
        # SECURITY: Strip PII (User's home directory path) from the description
        desc = strip_pii(desc)
            
        self.submit_btn.setText("Submitting...")
        self.submit_btn.setEnabled(False)
        
        data = {
            "type": self.type_combo.currentText(),
            "description": desc,
            "version": APP_VERSION,
            "os_name": os.name,
            "platform": sys.platform
        }
        
        self._submit_thread = FeedbackSubmitThread(data)
        self._submit_thread.finished_signal.connect(self._on_submit_finished)
        self._submit_thread.start()

    def reject(self):
        if self._submit_thread and self._submit_thread.isRunning():
            self._submit_thread.cancel()
            self._submit_thread.wait(500)
        super().reject()

    def _on_submit_finished(self, success, message):
        if success:
            QMessageBox.information(self, "Success", message)
            self.accept()
        else:
            QMessageBox.warning(self, "Network Error", f"Failed to send feedback securely to server.\n\nError: {message}")
            self.submit_btn.setText("Submit Feedback")
            self.submit_btn.setEnabled(True)

