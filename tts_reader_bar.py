"""Floating / Docked TTS Reader Bar component matching the website mockup layout.

Design:
- Rounded container (#1c1c1c panel background, #2c2c2c border, 8px border-radius)
- Speaker icon (volume-2 SVG in accent color #6cb6ff)
- Status text: "Reading aloud: {filename} — page {X} of {Y}" (or row/document progress)
- Controls: Play / Pause / Stop, Voice Dropdown, Close (X) button
"""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QToolButton, QComboBox, QFrame
)
from PySide6.QtCore import Qt, Signal, QSize
from icons import icon
from theme import get_active_palette, get_active_accent, ICON_SIZE_COMPACT

class TtsReaderBar(QFrame):
    """Floating / Docked TTS Reader Bar matching the website mockup style."""

    speak_requested = Signal()
    stop_requested = Signal()
    voice_changed = Signal(str)
    closed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("TtsReaderBar")
        self.setFixedHeight(42)

        p = get_active_palette()
        accent = get_active_accent()["accent"]
        self.setStyleSheet(f"""
            QFrame#TtsReaderBar {{
                background-color: {p['BRAND_PANEL']};
                border: 1px solid {p['BRAND_BORDER']};
                border-radius: 8px;
                padding: 2px 8px;
            }}
            QLabel {{
                color: {p['BRAND_PRIMARY']};
                font-size: 12px;
            }}
            QComboBox {{
                background: {p['BRAND_PANEL']};
                color: {p['BRAND_PRIMARY']};
                border: 1px solid {p['BRAND_BORDER']};
                padding: 2px 4px;
                border-radius: 4px;
            }}
            QComboBox QAbstractItemView {{
                background: {p['BRAND_PANEL']};
                color: {p['BRAND_PRIMARY']};
                border: 1px solid {p['BRAND_BORDER']};
                selection-background-color: {accent};
                selection-color: {p['BRAND_BACKGROUND']};
            }}
            QToolButton {{
                background: transparent;
                border: none;
                border-radius: 4px;
                padding: 3px;
                color: {p['BRAND_PRIMARY']};
            }}
            QToolButton:hover {{
                background-color: {p['BRAND_PANEL_2']};
            }}
            QToolButton#TtsStopBtn:hover {{
                background-color: rgba(239, 68, 68, 0.25);
            }}
            QToolButton#TtsStopBtn:pressed {{
                background-color: rgba(239, 68, 68, 0.6);
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 4, 10, 4)
        layout.setSpacing(10)

        # Speaker icon (blue accent color)
        self.speaker_label = QLabel()
        self.speaker_label.setPixmap(icon("volume-2", size=16, color=accent).pixmap(16, 16))
        layout.addWidget(self.speaker_label)

        # Status message text
        self.status_label = QLabel("Reading aloud: ready")
        layout.addWidget(self.status_label, 1)

        # Play / Speak button
        self.btn_play = QToolButton()
        self.btn_play.setIcon(icon("play", size=18, color=accent))
        self.btn_play.setToolTip("Read aloud (Play)")
        self.btn_play.clicked.connect(self.speak_requested.emit)
        layout.addWidget(self.btn_play)

        # Stop button
        self.btn_stop = QToolButton()
        self.btn_stop.setObjectName("TtsStopBtn")
        self.btn_stop.setIcon(icon("square", size=18, color="#ef4444"))
        self.btn_stop.setToolTip("Stop reading")
        self.btn_stop.clicked.connect(self.stop_requested.emit)
        layout.addWidget(self.btn_stop)

        # Voice dropdown
        self.voice_combo = QComboBox()
        self.voice_combo.setToolTip("Select TTS Voice")
        self.voice_combo.currentIndexChanged.connect(self._on_voice_changed)
        layout.addWidget(self.voice_combo)

        # Close button
        self.btn_close = QToolButton()
        p = get_active_palette()
        self.btn_close.setIcon(icon("x", size=14, color=p['BRAND_MUTED_FG']))
        self.btn_close.setToolTip("Hide reader bar")
        self.btn_close.clicked.connect(self._on_close)
        layout.addWidget(self.btn_close)

    def apply_style(self, active=False):
        p = get_active_palette()
        accent = get_active_accent()["accent"]
        bg = "#121e2b" if active else p['BRAND_PANEL']
        border = f"1.5px solid {accent}" if active else f"1px solid {p['BRAND_BORDER']}"
        self.setStyleSheet(f"""
            QFrame#TtsReaderBar {{
                background-color: {bg};
                border: {border};
                border-radius: 8px;
                padding: 2px 8px;
            }}
            QLabel {{
                color: {p['BRAND_PRIMARY']};
                font-size: 12px;
            }}
            QComboBox {{
                background-color: {p['BRAND_PANEL_2']};
                color: {p['BRAND_PRIMARY']};
                border: 1px solid {p['BRAND_BORDER']};
                border-radius: 4px;
                padding: 2px 6px;
                font-size: 11px;
                min-width: 130px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {p['BRAND_PANEL']};
                color: {p['BRAND_PRIMARY']};
                border: 1px solid {p['BRAND_BORDER']};
                selection-background-color: {accent};
                selection-color: {p['BRAND_BACKGROUND']};
            }}
            QToolButton {{
                background: transparent;
                border: none;
                border-radius: 4px;
                padding: 3px;
            }}
            QToolButton:hover {{
                background-color: #2a2a2a;
            }}
            QToolButton#TtsStopBtn:hover {{
                background-color: rgba(239, 68, 68, 0.25);
            }}
            QToolButton#TtsStopBtn:pressed {{
                background-color: rgba(239, 68, 68, 0.6);
            }}
        """)

    def set_active_reading(self, is_reading=True):
        self.apply_style(active=is_reading)

    def populate_voices(self, voices):
        """Populate the voice combo box with (voice_id, name) tuples."""
        self.voice_combo.blockSignals(True)
        self.voice_combo.clear()
        for vid, name in voices:
            self.voice_combo.addItem(name, vid)
        self.voice_combo.blockSignals(False)

    def set_status(self, filename: str, page_info: str = "", is_reading: bool = True):
        """Update status label, e.g. 'Reading aloud: lecture-04.pdf — page 12 of 38'."""
        accent = get_active_accent()["accent"]
        prefix = "Reading aloud:" if is_reading else "Text-To-Speech:"
        if page_info:
            msg = f"<span style='color:{accent}; font-weight:bold;'>{prefix}</span> <span style='color:#ffffff; font-weight:bold;'>{filename}</span> — <span style='color:#a0a0a0;'>{page_info}</span>"
        else:
            msg = f"<span style='color:{accent}; font-weight:bold;'>{prefix}</span> <span style='color:#ffffff; font-weight:bold;'>{filename}</span>"
        self.status_label.setText(msg)
        self.set_active_reading(is_reading)

    def get_selected_voice_id(self):
        return self.voice_combo.currentData()

    def _on_voice_changed(self, index):
        vid = self.voice_combo.itemData(index)
        if vid:
            self.voice_changed.emit(vid)

    def _on_close(self):
        self.stop_requested.emit()
        self.set_active_reading(False)
        self.hide()
        self.closed.emit()
