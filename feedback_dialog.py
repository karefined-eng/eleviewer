import json
import os
import sys
from datetime import datetime
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QTextEdit, 
    QPushButton, QMessageBox
)
from PySide6.QtGui import QDesktopServices
from PySide6.QtCore import Qt, QUrl
import urllib.parse
from theme import BRAND_BACKGROUND, BRAND_PANEL, BRAND_BORDER, BRAND_PRIMARY, get_brand_accent
from paths import APP_DATA_DIR
from main import APP_VERSION

class FeedbackDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Report Issue / Feedback")
        self.resize(500, 400)
        
        accent = get_brand_accent()
        self.setStyleSheet(f"""
            QDialog {{ background: {BRAND_BACKGROUND}; color: {BRAND_PRIMARY}; }}
            QLabel {{ color: {BRAND_PRIMARY}; }}
            QComboBox, QTextEdit {{ background: {BRAND_PANEL}; color: {BRAND_PRIMARY}; border: 1px solid {BRAND_BORDER}; padding: 6px; selection-background-color: {accent}; }}
            QPushButton {{ background: {BRAND_PANEL}; color: {BRAND_PRIMARY}; border: 1px solid {BRAND_BORDER}; padding: 6px 12px; border-radius: 4px; }}
            QPushButton:hover {{ background: {accent}; color: {BRAND_BACKGROUND}; }}
            QPushButton#submitBtn {{ background: {accent}; color: {BRAND_BACKGROUND}; font-weight: bold; }}
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
        
        submit_btn = QPushButton("Submit")
        submit_btn.setObjectName("submitBtn")
        submit_btn.clicked.connect(self.submit)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(submit_btn)
        
        layout.addLayout(btn_layout)
        
    def submit(self):
        desc = self.desc_edit.toPlainText().strip()
        if not desc:
            QMessageBox.warning(self, "Error", "Description cannot be empty.")
            return
            
        type_str = self.type_combo.currentText()
        title = urllib.parse.quote(f"[{type_str}] Feedback from App")
        body = urllib.parse.quote(f"**Version**: {APP_VERSION}\n**OS**: {sys.platform}\n\n**Description**:\n{desc}")
        
        url = f"https://github.com/karefined-eng/eleviewer/issues/new?title={title}&body={body}"
        QDesktopServices.openUrl(QUrl(url))
        
        QMessageBox.information(self, "Success", "Opened your browser to submit the issue on GitHub. Thank you!")
        self.accept()
