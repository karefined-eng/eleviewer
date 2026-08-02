from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QSpacerItem, QSizePolicy, QGridLayout
)
from PySide6.QtCore import Qt, Signal
from theme import get_brand_accent, get_active_palette
from icons import icon

class EmptyStateWidget(QWidget):
    # Signals to communicate with MainWindow
    open_vault_requested = Signal()
    new_file_requested = Signal()
    quick_switch_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("empty_state_root")
        self.setup_ui()
        self.reload_theme()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)
        
        self.panel = QFrame()
        self.panel.setObjectName("panel")
        self.panel.setFixedWidth(600)
        panel_layout = QVBoxLayout(self.panel)
        panel_layout.setContentsMargins(40, 40, 40, 40)
        panel_layout.setSpacing(25)
        
        # Header
        self.icon_lbl = QLabel()
        self.icon_lbl.setAlignment(Qt.AlignCenter)
        self.icon_lbl.setPixmap(icon("compass", size=48).pixmap(48, 48))
        
        self.title_lbl = QLabel("Welcome Home")
        self.title_lbl.setObjectName("title")
        self.title_lbl.setAlignment(Qt.AlignCenter)
        
        self.subtitle_lbl = QLabel("Your workspace is empty. Open a vault or start a new document to begin.")
        self.subtitle_lbl.setObjectName("subtitle")
        self.subtitle_lbl.setAlignment(Qt.AlignCenter)
        self.subtitle_lbl.setWordWrap(True)
        
        panel_layout.addWidget(self.icon_lbl)
        panel_layout.addWidget(self.title_lbl)
        panel_layout.addWidget(self.subtitle_lbl)
        
        # Primary Action Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        
        self.btn_vault = QPushButton(icon("folder"), " Open Vault")
        self.btn_vault.setObjectName("btn_primary")
        self.btn_vault.setCursor(Qt.PointingHandCursor)
        self.btn_vault.clicked.connect(self.open_vault_requested.emit)
        
        self.btn_new = QPushButton(icon("file-plus"), " New Document")
        self.btn_new.setObjectName("btn_secondary")
        self.btn_new.setCursor(Qt.PointingHandCursor)
        self.btn_new.clicked.connect(self.new_file_requested.emit)
        
        btn_layout.addWidget(self.btn_vault)
        btn_layout.addWidget(self.btn_new)
        
        panel_layout.addLayout(btn_layout)
        
        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setFrameShadow(QFrame.Sunken)
        divider.setObjectName("divider")
        panel_layout.addWidget(divider)
        
        # Shortcuts Grid
        shortcuts_lbl = QLabel("<b>Essential Shortcuts</b>")
        shortcuts_lbl.setObjectName("shortcuts_title")
        shortcuts_lbl.setAlignment(Qt.AlignCenter)
        panel_layout.addWidget(shortcuts_lbl)
        
        grid = QGridLayout()
        grid.setSpacing(10)
        
        shortcuts = [
            ("Ctrl + Q", "Quick Switcher"),
            ("Alt + V", "Toggle Vault Sidebar"),
            ("Ctrl + T", "Open Web Panel"),
            ("Ctrl + Shift + F", "Search Vault")
        ]
        
        self.shortcut_labels = []
        for i, (keys, desc) in enumerate(shortcuts):
            row = i // 2
            col = i % 2
            
            item_layout = QHBoxLayout()
            key_lbl = QLabel(keys)
            key_lbl.setObjectName("key_badge")
            key_lbl.setAlignment(Qt.AlignCenter)
            
            desc_lbl = QLabel(desc)
            desc_lbl.setObjectName("shortcut_desc")
            
            item_layout.addWidget(key_lbl)
            item_layout.addWidget(desc_lbl)
            item_layout.addStretch()
            
            grid.addLayout(item_layout, row, col)
            self.shortcut_labels.extend([key_lbl, desc_lbl])
            
        panel_layout.addLayout(grid)
        main_layout.addWidget(self.panel)

    def reload_theme(self):
        p = get_active_palette()
        accent = get_brand_accent()
        
        # Rule 2: Dynamic theme styling, explicit color for backgrounds to avoid invisible text bugs
        self.setStyleSheet(f"""
            QWidget#empty_state_root {{ 
                background: {p['BRAND_BACKGROUND']}; 
                color: {p['BRAND_PRIMARY']}; 
            }}
            QFrame#panel {{ 
                background: {p['BRAND_PANEL']}; 
                border: 1px solid {p['BRAND_BORDER']}; 
                border-radius: 12px; 
            }}
            QLabel#title {{ 
                font-size: 28px; 
                font-weight: bold; 
                color: {p['BRAND_PRIMARY']}; 
            }}
            QLabel#subtitle {{ 
                font-size: 14px; 
                color: {p['BRAND_MUTED_FG']}; 
                margin-bottom: 10px;
            }}
            QPushButton#btn_primary {{ 
                background: {accent}; 
                color: {p['BRAND_BACKGROUND']}; 
                font-weight: bold; 
                font-size: 14px;
                border-radius: 6px; 
                padding: 10px 20px; 
                border: none;
            }}
            QPushButton#btn_primary:hover {{ 
                opacity: 0.9; 
                background: {p['BRAND_BORDER']};
                color: {p['BRAND_PRIMARY']};
            }}
            QPushButton#btn_primary:pressed {{ 
                background: {p['BRAND_MUTED_FG']}; 
            }}
            QPushButton#btn_secondary {{ 
                background: transparent; 
                color: {p['BRAND_PRIMARY']}; 
                font-weight: bold; 
                font-size: 14px;
                border-radius: 6px; 
                padding: 10px 20px; 
                border: 1px solid {p['BRAND_BORDER']};
            }}
            QPushButton#btn_secondary:hover {{ 
                background: {p['BRAND_BORDER']}; 
            }}
            QPushButton#btn_secondary:pressed {{ 
                background: {p['BRAND_MUTED_FG']}; 
            }}
            QFrame#divider {{
                background: {p['BRAND_BORDER']};
                max-height: 1px;
            }}
            QLabel#shortcuts_title {{
                color: {p['BRAND_MUTED_FG']};
                font-size: 13px;
                text-transform: uppercase;
                margin-top: 10px;
            }}
            QLabel#key_badge {{
                background: {p['BRAND_BACKGROUND']};
                color: {p['BRAND_PRIMARY']};
                border: 1px solid {p['BRAND_BORDER']};
                border-radius: 4px;
                padding: 4px 8px;
                font-family: monospace;
                font-weight: bold;
                font-size: 12px;
            }}
            QLabel#shortcut_desc {{
                color: {p['BRAND_MUTED_FG']};
                font-size: 13px;
                padding-left: 5px;
            }}
        """)
        
        # Update Icon Color
        self.icon_lbl.setPixmap(icon("compass", size=48, color=accent).pixmap(48, 48))
