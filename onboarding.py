from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from theme import get_brand_accent, get_active_palette
from settings import load_settings, save_settings
from icons import icon

class ChecklistItem(QWidget):
    def __init__(self, title, description, shortcut_text, try_action=None, parent=None):
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
        
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)
        
        if shortcut_text:
            p = get_active_palette()
            self.shortcut_lbl = QLabel(shortcut_text)
            self.shortcut_lbl.setStyleSheet(f"background: {p['BRAND_BACKGROUND']}; padding: 4px 8px; border-radius: 4px; font-family: monospace;")
            controls_layout.addWidget(self.shortcut_lbl, 0, Qt.AlignVCenter)

        if try_action:
            self.try_btn = QPushButton("Try It")
            self.try_btn.setCursor(Qt.PointingHandCursor)
            p = get_active_palette()
            self.try_btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    color: {p['BRAND_PRIMARY']};
                    border: 1px solid {p['BRAND_BORDER']};
                    border-radius: 4px;
                    padding: 4px 10px;
                    font-weight: bold;
                }}
                QPushButton:hover {{ background: {p['BRAND_BORDER']}; }}
            """)
            self.try_btn.clicked.connect(try_action)
            controls_layout.addWidget(self.try_btn, 0, Qt.AlignVCenter)

        if controls_layout.count() > 0:
            layout.addLayout(controls_layout, 0)

    def mark_done(self):
        if not self.is_checked:
            self.is_checked = True
            accent = get_brand_accent()
            self.check_lbl.setPixmap(icon("check-square", size=24, color=accent).pixmap(24, 24))
            self.title_lbl.setStyleSheet("font-size: 16px; text-decoration: line-through; color: #888;")
            if hasattr(self, 'try_btn'):
                self.try_btn.hide()

class InteractiveWelcomeWidget(QWidget):
    close_requested = Signal()
    vault_requested = Signal()
    quick_switch_requested = Signal()
    web_requested = Signal()
    scratchpad_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        
        p = get_active_palette()
        accent = get_brand_accent()
        
        # Rule 2 explicit backgrounds
        self.setStyleSheet(f"""
            QWidget {{ background: {p['BRAND_BACKGROUND']}; color: {p['BRAND_PRIMARY']}; }}
            QFrame#panel {{ background: {p['BRAND_PANEL']}; border: 1px solid {p['BRAND_BORDER']}; border-radius: 8px; }}
            QLabel#title {{ font-size: 28px; font-weight: bold; color: {accent}; margin-bottom: 5px; }}
            QPushButton#primary {{ background: {accent}; color: {p['BRAND_BACKGROUND']}; font-weight: bold; border-radius: 6px; padding: 10px 20px; border: none; }}
            QPushButton#primary:hover {{ opacity: 0.8; color: {p['BRAND_PRIMARY']}; background: {p['BRAND_BORDER']}; }}
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
            "vault": ChecklistItem("Toggle the Vault", "Open the sidebar to see your files.", "Alt+V", self.vault_requested.emit),
            "quick_switch": ChecklistItem("Quick Switcher", "Fuzzy-find and jump to any document.", "Ctrl+Q", self.quick_switch_requested.emit),
            "web": ChecklistItem("Web Browser", "Open the split-view research browser.", "Ctrl+T", self.web_requested.emit)
        }
        
        for k, item in self.items.items():
            panel_layout.addWidget(item)
            
        self.complete_lbl = QLabel("🎉 Mission Accomplished!")
        self.complete_lbl.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {accent};")
        self.complete_lbl.setAlignment(Qt.AlignCenter)
        self.complete_lbl.hide()
        
        self.start_btn = QPushButton(icon("file-plus"), " Create Scratchpad")
        self.start_btn.setObjectName("primary")
        self.start_btn.setCursor(Qt.PointingHandCursor)
        self.start_btn.hide()
        self.start_btn.clicked.connect(self._on_start_clicked)
        
        panel_layout.addWidget(self.complete_lbl)
        panel_layout.addWidget(self.start_btn, 0, Qt.AlignCenter)
        
        main_layout.addWidget(self.panel)
        
    def _on_start_clicked(self):
        self.scratchpad_requested.emit()
        self.close_requested.emit()
        
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
