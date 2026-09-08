from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QGraphicsOpacityEffect
)
from PySide6.QtCore import Qt, QRect, QPropertyAnimation, QPoint, QEvent
from PySide6.QtGui import QPainter, QColor, QPainterPath

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
        self.card.setFixedSize(340, 185)
        self.card.setStyleSheet(f"""
            QWidget#TourCard {{
                background-color: {self.p['BRAND_PANEL']};
                border: 1px solid {self.p['BRAND_BORDER']};
                border-radius: 12px;
            }}
        """)
        self.card.setObjectName("TourCard")
        
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(18, 16, 18, 16)
        card_layout.setSpacing(8)
        
        # Header Row (Step counter badge + Close 'X' button)
        header_row = QHBoxLayout()
        header_row.setContentsMargins(0, 0, 0, 0)
        
        self.step_badge = QLabel()
        self.step_badge.setStyleSheet(f"color: {self.accent}; font-size: 11px; font-weight: bold; border: none;")
        header_row.addWidget(self.step_badge)
        header_row.addStretch()
        
        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(20, 20)
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.setToolTip("Close tour (Esc)")
        self.close_btn.setStyleSheet(f"""
            QPushButton {{
                color: {self.p['BRAND_MUTED_FG']};
                background: transparent;
                border: none;
                font-size: 13px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                color: {self.p['BRAND_PRIMARY']};
            }}
        """)
        self.close_btn.clicked.connect(self.close)
        header_row.addWidget(self.close_btn)
        card_layout.addLayout(header_row)
        
        # Title
        self.title_lbl = QLabel()
        self.title_lbl.setStyleSheet(f"color: {self.p['BRAND_PRIMARY']}; font-size: 15px; font-weight: bold; border: none;")
        card_layout.addWidget(self.title_lbl)
        
        # Description
        self.desc_lbl = QLabel()
        self.desc_lbl.setWordWrap(True)
        self.desc_lbl.setStyleSheet(f"color: {self.p['BRAND_MUTED_FG']}; font-size: 12px; border: none; line-height: 1.4;")
        card_layout.addWidget(self.desc_lbl, 1)
        
        # Button Row
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(0, 4, 0, 0)
        
        self.skip_btn = QPushButton("Skip Tour")
        self.skip_btn.setCursor(Qt.PointingHandCursor)
        self.skip_btn.setStyleSheet(f"""
            QPushButton {{
                color: {self.p['BRAND_MUTED_FG']};
                background: transparent;
                border: none;
                font-size: 12px;
            }}
            QPushButton:hover {{
                color: {self.p['BRAND_PRIMARY']};
            }}
        """)
        self.skip_btn.clicked.connect(self.close)
        
        self.next_btn = QPushButton("Next →")
        self.next_btn.setCursor(Qt.PointingHandCursor)
        self.next_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.accent};
                color: white;
                border-radius: 6px;
                padding: 6px 16px;
                font-size: 12px;
                font-weight: bold;
                border: none;
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
        self.anim.setDuration(300)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.start()
        
        if self.main_window:
            self.main_window.installEventFilter(self)
            
        self.update_geometry()
        self.show_step()

    def update_geometry(self):
        if self.main_window:
            top_left = self.main_window.mapToGlobal(QPoint(0, 0))
            self.setGeometry(top_left.x(), top_left.y(), self.main_window.width(), self.main_window.height())

    def eventFilter(self, watched, event):
        if watched == self.main_window and event.type() in (QEvent.Resize, QEvent.Move):
            self.update_geometry()
            self._position_card()
            self.update()
        return super().eventFilter(watched, event)

    def closeEvent(self, event):
        if self.main_window:
            try:
                self.main_window.removeEventFilter(self)
            except Exception:
                pass
        super().closeEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        elif event.key() in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space, Qt.Key_Right):
            self.next_step()
        elif event.key() == Qt.Key_Left:
            self.prev_step()
        else:
            super().keyPressEvent(event)
            
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

    def _position_card(self):
        card_w = self.card.width()
        card_h = self.card.height()
        win_w = max(400, self.width())
        win_h = max(300, self.height())

        if self.target_rect.isEmpty():
            card_x = (win_w - card_w) // 2
            card_y = (win_h - card_h) // 2
        else:
            tr = self.target_rect
            is_wide = tr.width() > (win_w * 0.45)
            
            if is_wide:
                # Wide widget like toolbar or tab bar -> place below or above
                if tr.bottom() + 16 + card_h <= win_h - 20:
                    card_y = tr.bottom() + 16
                elif tr.top() - 16 - card_h >= 20:
                    card_y = tr.top() - 16 - card_h
                else:
                    card_y = (win_h - card_h) // 2
                card_x = tr.center().x() - card_w // 2
            else:
                # Narrow target (like a toolbar button)
                if tr.top() < win_h * 0.4 and (tr.bottom() + 16 + card_h <= win_h - 20):
                    card_y = tr.bottom() + 16
                    card_x = tr.center().x() - card_w // 2
                elif tr.right() + 16 + card_w <= win_w - 20:
                    card_x = tr.right() + 16
                    card_y = tr.top()
                elif tr.left() - 16 - card_w >= 20:
                    card_x = tr.left() - 16 - card_w
                    card_y = tr.top()
                elif tr.top() - 16 - card_h >= 20:
                    card_y = tr.top() - 16 - card_h
                    card_x = tr.center().x() - card_w // 2
                else:
                    card_x = (win_w - card_w) // 2
                    card_y = (win_h - card_h) // 2

        # GUARANTEED SAFETY BOUNDS: Clamp strictly inside visible window!
        margin = 16
        card_x = max(margin, min(win_w - card_w - margin, card_x))
        card_y = max(margin, min(win_h - card_h - margin, card_y))

        self.card.move(card_x, card_y)

    def show_step(self):
        if self.current_step >= len(self.steps):
            self.close()
            return
            
        step = self.steps[self.current_step]
        self.step_badge.setText(f"STEP {self.current_step + 1} OF {len(self.steps)}")
        self.title_lbl.setText(step["title"])
        self.desc_lbl.setText(step["desc"])
        
        if self.current_step == len(self.steps) - 1:
            self.next_btn.setText("Finish ✓")
        else:
            self.next_btn.setText("Next →")
            
        target_widget = step.get("widget")
        if target_widget and target_widget.isVisible():
            # Get geometry of target widget relative to main window
            pos = target_widget.mapTo(self.main_window, QPoint(0, 0))
            self.target_rect = QRect(pos.x() - 4, pos.y() - 4, target_widget.width() + 8, target_widget.height() + 8)
        else:
            self.target_rect = QRect()
            
        self._position_card()
            
        # Trigger any step actions
        action = step.get("action")
        if action:
            try:
                action()
            except Exception:
                pass
            
        self.update()
        
    def next_step(self):
        self.current_step += 1
        self.show_step()

    def prev_step(self):
        if self.current_step > 0:
            self.current_step -= 1
            self.show_step()


def start_tutorial(main_window):
    """
    Initializes and starts the interactive tutorial overlay.
    """
    if main_window.toolbar.isHidden():
        main_window.toggle_main_toolbar()
        
    def get_tool_btn(action_id):
        for act in main_window.toolbar.actions():
            if hasattr(main_window.toolbar, "_id_actions"):
                for aid, a in main_window.toolbar._id_actions.items():
                    if a == act and aid == action_id:
                        return main_window.toolbar.widgetForAction(act)
        return None
        
    def ensure_web_panel_open():
        dock = getattr(main_window, "_web_dock", None)
        if not dock or not dock.isVisible():
            main_window.toggle_web_panel()

    tab_target = getattr(main_window.tabs, "tabBar", None)
    if callable(tab_target):
        tab_widget = tab_target()
    else:
        tab_widget = getattr(main_window, "tabs", None)

    steps = [
        {
            "title": "Welcome to the Playground!",
            "desc": "This quick interactive tour will show you the hidden power-user moves in EleViewer. Press Esc anytime to exit.",
            "widget": None,
            "action": None
        },
        {
            "title": "Customizing the Toolbar",
            "desc": "Did you know the toolbar is fully customizable? Just click and drag any icon to rearrange it, or drag it completely off the bar to remove it!",
            "widget": main_window.toolbar if hasattr(main_window, 'toolbar') else None,
            "action": None
        },
        {
            "title": "Split Screen Mode",
            "desc": "Need to view two documents at once? Right-click any tab at the top and select 'Split screen with this tab'.",
            "widget": tab_widget,
            "action": None
        },
        {
            "title": "Web Panel Fullscreen",
            "desc": "When researching in the Web Panel, click the 'Expand to Full Window' button on its top-right corner to pop it into full screen mode.",
            "widget": get_tool_btn("web"),
            "action": ensure_web_panel_open
        },
        {
            "title": "Say Hello!",
            "desc": "Have an idea or just want to say thank you? Open the Help menu and click 'Submit Feedback...'. We read everything!",
            "widget": main_window.menuBar() if hasattr(main_window, 'menuBar') else None,
            "action": None
        }
    ]
    
    overlay = TutorialOverlay(main_window, steps)
    overlay.show()
    return overlay
