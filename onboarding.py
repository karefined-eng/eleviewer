from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QStackedWidget, QWidget
)
from PySide6.QtCore import Qt
from theme import BRAND_BACKGROUND, BRAND_PANEL, BRAND_BORDER, BRAND_PRIMARY, get_brand_accent

class OnboardingDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Welcome to EleViewer")
        self.resize(600, 400)
        
        accent = get_brand_accent()
        self.setStyleSheet(f"""
            QDialog {{ background: {BRAND_BACKGROUND}; color: {BRAND_PRIMARY}; }}
            QLabel {{ color: {BRAND_PRIMARY}; font-size: 16px; }}
            QLabel#title {{ font-size: 28px; font-weight: bold; color: {accent}; margin-bottom: 20px; }}
            QPushButton {{ background: {BRAND_PANEL}; color: {BRAND_PRIMARY}; border: 1px solid {BRAND_BORDER}; padding: 8px 16px; border-radius: 4px; font-size: 14px; }}
            QPushButton:hover {{ background: {accent}; color: {BRAND_BACKGROUND}; }}
            QPushButton#primary {{ background: {accent}; color: {BRAND_BACKGROUND}; font-weight: bold; }}
            QPushButton#primary:hover {{ opacity: 0.8; }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        
        self.stack = QStackedWidget()
        self.stack.addWidget(self._create_slide(
            "Welcome to EleViewer 🐘",
            "Your Zero-Friction, Offline-First Sovereignty Workstation.\n\n"
            "EleViewer is designed to stay out of your way. Everything is saved locally. "
            "There's no telemetry, no forced cloud accounts, and no loading screens."
        ))
        self.stack.addWidget(self._create_slide(
            "Survival Shortcuts ⚡",
            "Master these three shortcuts to fly through your workflow:\n\n"
            "• Alt+V : Toggle Vault Sidebar\n"
            "• Ctrl+Q : Quick Switcher (fuzzy find files)\n"
            "• Ctrl+T : Split View Web Browser"
        ))
        self.stack.addWidget(self._create_slide(
            "Safety Net Active 🛡️",
            "We've got your back.\n\n"
            "Draft Auto-Save silently backs up your unsaved text every 60 seconds "
            "so you never lose a fleeting thought to a crash or an accidental 'Don't Save'."
        ))
        
        layout.addWidget(self.stack)
        
        btn_layout = QHBoxLayout()
        self.prev_btn = QPushButton("Back")
        self.prev_btn.clicked.connect(self._prev)
        self.prev_btn.setEnabled(False)
        
        self.next_btn = QPushButton("Next")
        self.next_btn.setObjectName("primary")
        self.next_btn.clicked.connect(self._next)
        
        btn_layout.addWidget(self.prev_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.next_btn)
        
        layout.addLayout(btn_layout)
        
    def _create_slide(self, title, text):
        w = QWidget()
        l = QVBoxLayout(w)
        l.setAlignment(Qt.AlignCenter)
        
        title_lbl = QLabel(title)
        title_lbl.setObjectName("title")
        title_lbl.setAlignment(Qt.AlignCenter)
        
        text_lbl = QLabel(text)
        text_lbl.setAlignment(Qt.AlignCenter)
        text_lbl.setWordWrap(True)
        text_lbl.setStyleSheet("line-height: 1.5;")
        
        l.addStretch()
        l.addWidget(title_lbl)
        l.addWidget(text_lbl)
        l.addStretch()
        return w
        
    def _prev(self):
        idx = self.stack.currentIndex()
        if idx > 0:
            self.stack.setCurrentIndex(idx - 1)
        self._update_buttons()
        
    def _next(self):
        idx = self.stack.currentIndex()
        if idx < self.stack.count() - 1:
            self.stack.setCurrentIndex(idx + 1)
            self._update_buttons()
        else:
            self.accept()
            
    def _update_buttons(self):
        idx = self.stack.currentIndex()
        self.prev_btn.setEnabled(idx > 0)
        if idx == self.stack.count() - 1:
            self.next_btn.setText("Get Started")
        else:
            self.next_btn.setText("Next")
