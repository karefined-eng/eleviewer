from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from theme import BRAND_BACKGROUND, BRAND_PANEL, BRAND_BORDER, BRAND_PRIMARY, get_brand_accent
from settings import load_settings, save_settings
from icons import icon

class ChecklistItem(QWidget):
    def __init__(self, title, description, shortcut_text, parent=None):
        super().__init__(parent)
        self.is_checked = False
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        self.check_lbl = QLabel()
        self.check_lbl.setPixmap(icon("square", size=24).pixmap(24, 24))
        layout.addWidget(self.check_lbl, 0, Qt.AlignTop)
        
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        
        self.title_lbl = QLabel(f"<b>{title}</b>")
        self.title_lbl.setStyleSheet("font-size: 16px;")
        
        self.desc_lbl = QLabel(description)
        self.desc_lbl.setStyleSheet("color: #888; font-size: 13px;")
        self.desc_lbl.setWordWrap(True)
        
        text_layout.addWidget(self.title_lbl)
        text_layout.addWidget(self.desc_lbl)
        layout.addLayout(text_layout, 1)
        
        if shortcut_text:
            self.shortcut_lbl = QLabel(shortcut_text)
            self.shortcut_lbl.setStyleSheet(f"background: {BRAND_BACKGROUND}; padding: 4px 8px; border-radius: 4px; font-family: monospace;")
            layout.addWidget(self.shortcut_lbl, 0, Qt.AlignVCenter)

    def mark_done(self):
        if not self.is_checked:
            self.is_checked = True
            accent = get_brand_accent()
            self.check_lbl.setPixmap(icon("check-square", size=24, color=accent).pixmap(24, 24))
            self.title_lbl.setStyleSheet("font-size: 16px; text-decoration: line-through; color: #888;")

class InteractiveWelcomeWidget(QWidget):
    close_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        
        accent = get_brand_accent()
        self.setStyleSheet(f"""
            QWidget {{ background: {BRAND_BACKGROUND}; color: {BRAND_PRIMARY}; }}
            QFrame#panel {{ background: {BRAND_PANEL}; border: 1px solid {BRAND_BORDER}; border-radius: 8px; }}
            QLabel#title {{ font-size: 28px; font-weight: bold; color: {accent}; margin-bottom: 5px; }}
            QPushButton#primary {{ background: {accent}; color: {BRAND_BACKGROUND}; font-weight: bold; border-radius: 6px; padding: 10px 20px; }}
            QPushButton#primary:hover {{ opacity: 0.8; }}
        """)
        
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)
        
        self.panel = QFrame()
        self.panel.setObjectName("panel")
        self.panel.setFixedWidth(550)
        panel_layout = QVBoxLayout(self.panel)
        panel_layout.setContentsMargins(30, 30, 30, 30)
        panel_layout.setSpacing(20)
        
        title = QLabel("Welcome to EleViewer 🐘")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        
        subtitle = QLabel("Complete your pre-flight checklist to unlock your workspace. Try these three survival skills right now:")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setWordWrap(True)
        
        panel_layout.addWidget(title)
        panel_layout.addWidget(subtitle)
        
        self.items = {
            "vault": ChecklistItem("Toggle the Vault", "Open the sidebar to see your files.", "Alt+V"),
            "quick_switch": ChecklistItem("Quick Switcher", "Fuzzy-find and jump to any document.", "Ctrl+Q"),
            "web": ChecklistItem("Web Browser", "Open the split-view research browser.", "Ctrl+T")
        }
        
        for k, item in self.items.items():
            panel_layout.addWidget(item)
            
        self.complete_lbl = QLabel("🎉 Mission Accomplished!")
        self.complete_lbl.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {accent};")
        self.complete_lbl.setAlignment(Qt.AlignCenter)
        self.complete_lbl.hide()
        
        self.start_btn = QPushButton("Start Studying")
        self.start_btn.setObjectName("primary")
        self.start_btn.hide()
        self.start_btn.clicked.connect(self.close_requested.emit)
        
        panel_layout.addWidget(self.complete_lbl)
        panel_layout.addWidget(self.start_btn, 0, Qt.AlignCenter)
        
        main_layout.addWidget(self.panel)
        
    def check_off(self, item_id):
        if item_id in self.items and not self.items[item_id].is_checked:
            self.items[item_id].mark_done()
            self._check_all_done()
            
    def _check_all_done(self):
        if all(item.is_checked for item in self.items.values()):
            self.complete_lbl.show()
            self.start_btn.show()
            s = load_settings()
            s["onboarding_completed"] = True
            save_settings(s)
