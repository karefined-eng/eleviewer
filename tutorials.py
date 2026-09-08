import math
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QGraphicsOpacityEffect
from PySide6.QtCore import Qt, QRect, QPropertyAnimation, QPoint, QEasingCurve
from PySide6.QtGui import QPainter, QColor, QRegion, QPainterPath

from theme import get_active_palette, get_brand_accent

class TutorialOverlay(QWidget):
    """
    A full-window overlay that creates a 'spotlight' effect by darkening the background
    and cutting out a transparent hole over a target widget. It displays a guiding card next to it.
    """
    def __init__(self, main_window, steps):
        super().__init__(main_window)
        self.main_window = main_window
        self.steps = steps
        self.current_step = 0
        self.target_rect = QRect()
        
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_DeleteOnClose)
        
        self.p = get_active_palette()
        self.accent = get_brand_accent()
        
        # Guide Card Widget
        self.card = QWidget(self)
        self.card.setFixedSize(300, 160)
        self.card.setStyleSheet(f"""
            QWidget {{
                background-color: {self.p['BRAND_PANEL']};
                border: 1px solid {self.p['BRAND_BORDER']};
                border-radius: 12px;
            }}
        """)
        
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        
        self.title_lbl = QLabel()
        self.title_lbl.setStyleSheet(f"color: {self.p['BRAND_PRIMARY']}; font-size: 16px; font-weight: bold; border: none;")
        card_layout.addWidget(self.title_lbl)
        
        self.desc_lbl = QLabel()
        self.desc_lbl.setWordWrap(True)
        self.desc_lbl.setStyleSheet(f"color: {self.p['BRAND_MUTED_FG']}; font-size: 13px; border: none;")
        card_layout.addWidget(self.desc_lbl)
        
        card_layout.addStretch()
        
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(0, 0, 0, 0)
        
        self.skip_btn = QPushButton("Skip Tour")
        self.skip_btn.setCursor(Qt.PointingHandCursor)
        self.skip_btn.setStyleSheet(f"color: {self.p['BRAND_MUTED_FG']}; background: transparent; border: none;")
        self.skip_btn.clicked.connect(self.close)
        
        self.next_btn = QPushButton("Next")
        self.next_btn.setCursor(Qt.PointingHandCursor)
        self.next_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.accent};
                color: white;
                border-radius: 6px;
                padding: 6px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {self.accent}dd; }}
        """)
        self.next_btn.clicked.connect(self.next_step)
        
        btn_layout.addWidget(self.skip_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.next_btn)
        
        card_layout.addLayout(btn_layout)
        
        # Entrance Animation
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim.setDuration(400)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.start()
        
        self.update_geometry()
        self.show_step()

    def update_geometry(self):
        if self.main_window:
            self.setGeometry(0, 0, self.main_window.width(), self.main_window.height())
            
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Darken entire window
        path = QPainterPath()
        path.addRect(self.rect())
        
        # Cutout the spotlight
        if not self.target_rect.isEmpty():
            spotlight_path = QPainterPath()
            spotlight_path.addRoundedRect(self.target_rect, 8, 8)
            path = path.subtracted(spotlight_path)
            
        painter.fillPath(path, QColor(0, 0, 0, 180))
        
        # Draw a glowing border around the spotlight
        if not self.target_rect.isEmpty():
            painter.setPen(QColor(self.accent))
            painter.setBrush(Qt.NoBrush)
            painter.drawRoundedRect(self.target_rect, 8, 8)

    def show_step(self):
        if self.current_step >= len(self.steps):
            self.close()
            return
            
        step = self.steps[self.current_step]
        self.title_lbl.setText(step["title"])
        self.desc_lbl.setText(step["desc"])
        
        if self.current_step == len(self.steps) - 1:
            self.next_btn.setText("Finish")
            
        target_widget = step.get("widget")
        if target_widget and target_widget.isVisible():
            # Get the geometry of the target widget relative to the main window
            pos = target_widget.mapTo(self.main_window, QPoint(0, 0))
            self.target_rect = QRect(pos.x() - 4, pos.y() - 4, target_widget.width() + 8, target_widget.height() + 8)
            
            # Position the card intelligently
            card_x = self.target_rect.right() + 20
            card_y = self.target_rect.top()
            
            # If it goes off-screen to the right, put it on the left
            if card_x + self.card.width() > self.width():
                card_x = self.target_rect.left() - self.card.width() - 20
                
            # If it goes off-screen to the bottom
            if card_y + self.card.height() > self.height():
                card_y = self.height() - self.card.height() - 20
                
            self.card.move(card_x, card_y)
        else:
            self.target_rect = QRect()
            # Center the card
            self.card.move((self.width() - self.card.width()) // 2, (self.height() - self.card.height()) // 2)
            
        # Trigger any simulated actions
        action = step.get("action")
        if action:
            action()
            
        self.update()
        
    def next_step(self):
        self.current_step += 1
        self.show_step()


def start_tutorial(main_window):
    """
    Initializes and starts the interactive tutorial overlay.
    """
    if main_window.toolbar.isHidden():
        main_window.toggle_main_toolbar()
        
    def get_tool_btn(action_id):
        from PySide6.QtWidgets import QToolButton
        for act in main_window.toolbar.actions():
            if hasattr(main_window.toolbar, "_id_actions"):
                for aid, a in main_window.toolbar._id_actions.items():
                    if a == act and aid == action_id:
                        return main_window.toolbar.widgetForAction(act)
        return None
        
    steps = [
        {
            "title": "Welcome to EleViewer!",
            "desc": "This quick tutorial will show you the key features to turbo-charge your study workflow.",
            "widget": None,
            "action": None
        },
        {
            "title": "Global Search",
            "desc": "Press Ctrl+Q anywhere to search across all your course vaults instantly.",
            "widget": main_window.quick_menu.parentWidget() if hasattr(main_window, 'quick_menu') else None,
            "action": None
        },
        {
            "title": "The Web Panel",
            "desc": "Research alongside your documents without leaving the app. Let's open it now!",
            "widget": get_tool_btn("web"),
            "action": lambda: main_window.open_web_tab_with_url("https://google.com") if not getattr(main_window, 'web_panel', None) or not main_window.web_panel.isVisible() else None
        },
        {
            "title": "Vaults",
            "desc": "Keep all your local course folders organized here.",
            "widget": get_tool_btn("vault"),
            "action": lambda: main_window.toggle_vault_panel() if getattr(main_window, 'vault_panel', None) and not main_window.vault_panel.isVisible() else None
        },
        {
            "title": "You're all set!",
            "desc": "Explore the settings (Alt+S) to customize EleViewer. Happy studying!",
            "widget": get_tool_btn("settings"),
            "action": None
        }
    ]
    
    overlay = TutorialOverlay(main_window, steps)
    overlay.show()
