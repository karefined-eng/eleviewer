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
            "Open your course files in one place",
            "EleViewer is a lightweight Windows study workspace for PDFs, Word files, slides, spreadsheets, Markdown, and notes.\n\n"
            "Your files stay on your computer. No account, cloud upload, or subscription is required."
        ))
        self.stack.addWidget(self._create_slide(
            "Start with a real reading",
            "Use the sample note to see the workflow immediately.\n\n"
            "Open a document, select text, and press F9 to hear it aloud. Then add your course folder so your files are one click away."
        ))
        self.stack.addWidget(self._create_slide(
            "Keep your place automatically",
            "Bookmarks, session restore, and draft recovery help you return to the same study session.\n\n"
            "The shortcuts are here when you are ready: Alt+V for your folder, Ctrl+Q to find a file, and F9 to read aloud."
        ))
        self.stack.addWidget(self._create_slide(
            "You are ready to study",
            "Open the sample note now, or close this guide and use the welcome screen to open your own files."
        ))
        
        layout.addWidget(self.stack)
        
        btn_layout = QHBoxLayout()
        self.prev_btn = QPushButton("Back")
        self.prev_btn.clicked.connect(self._prev)
        self.prev_btn.setEnabled(False)
        
        self.sample_btn = QPushButton("Open Sample Note")
        self.sample_btn.clicked.connect(self._open_sample)
        self.sample_btn.setVisible(False)

        self.next_btn = QPushButton("Next")
        self.next_btn.setObjectName("primary")
        self.next_btn.clicked.connect(self._next)
        
        btn_layout.addWidget(self.prev_btn)
        btn_layout.addWidget(self.sample_btn)
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
            
    def _open_sample(self):
        parent = self.parent()
        if parent is not None and hasattr(parent, "open_sample_note"):
            parent.open_sample_note()
            self.accept()

    def _update_buttons(self):
        idx = self.stack.currentIndex()
        self.prev_btn.setEnabled(idx > 0)
        self.sample_btn.setVisible(idx == self.stack.count() - 1)
        if idx == self.stack.count() - 1:
            self.next_btn.setText("Finish")
        else:
            self.next_btn.setText("Next")
