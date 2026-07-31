from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, 
    QCheckBox, QLabel, QToolButton
)
from PySide6.QtCore import Signal, Qt
from icons import icon
from theme import BRAND_PANEL_2, BRAND_BORDER, BRAND_PRIMARY, BRAND_PANEL, BRAND_MUTED

class FindReplaceWidget(QWidget):
    find_next_requested = Signal(str, bool, bool, bool)  # text, match_case, whole_word, forward
    replace_requested = Signal(str, str, bool, bool)     # find_text, replace_text, match_case, whole_word
    replace_all_requested = Signal(str, str, bool, bool) # find_text, replace_text, match_case, whole_word
    close_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QWidget {{
                background: {BRAND_PANEL_2};
                color: {BRAND_PRIMARY};
                border-top: 1px solid {BRAND_BORDER};
            }}
            QLineEdit {{
                background: {BRAND_PANEL};
                border: 1px solid {BRAND_BORDER};
                padding: 4px;
                color: {BRAND_PRIMARY};
            }}
            QPushButton, QToolButton {{
                background: {BRAND_PANEL_2};
                border: 1px solid {BRAND_BORDER};
                padding: 4px 8px;
                border-radius: 4px;
            }}
            QPushButton:hover, QToolButton:hover {{
                background: {BRAND_MUTED};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        # Find row
        find_layout = QHBoxLayout()
        find_layout.setContentsMargins(0, 0, 0, 0)
        
        self.find_input = QLineEdit()
        self.find_input.setPlaceholderText("Find...")
        self.find_input.returnPressed.connect(self._on_find_next)
        
        self.btn_prev = QToolButton()
        self.btn_prev.setIcon(icon("arrow-up", size=16))
        self.btn_prev.setToolTip("Find Previous (Shift+Enter)")
        self.btn_prev.clicked.connect(self._on_find_prev)
        
        self.btn_next = QToolButton()
        self.btn_next.setIcon(icon("arrow-down", size=16))
        self.btn_next.setToolTip("Find Next (Enter)")
        self.btn_next.clicked.connect(self._on_find_next)

        self.btn_close = QToolButton()
        self.btn_close.setIcon(icon("x", size=16))
        self.btn_close.clicked.connect(self.hide_panel)

        find_layout.addWidget(QLabel("Find:"))
        find_layout.addWidget(self.find_input)
        find_layout.addWidget(self.btn_prev)
        find_layout.addWidget(self.btn_next)
        find_layout.addWidget(self.btn_close)

        # Replace row
        replace_layout = QHBoxLayout()
        replace_layout.setContentsMargins(0, 0, 0, 0)

        self.replace_input = QLineEdit()
        self.replace_input.setPlaceholderText("Replace with...")
        self.replace_input.returnPressed.connect(self._on_replace)

        self.btn_replace = QPushButton("Replace")
        self.btn_replace.clicked.connect(self._on_replace)

        self.btn_replace_all = QPushButton("Replace All")
        self.btn_replace_all.clicked.connect(self._on_replace_all)

        replace_layout.addWidget(QLabel("Replace:"))
        replace_layout.addWidget(self.replace_input)
        replace_layout.addWidget(self.btn_replace)
        replace_layout.addWidget(self.btn_replace_all)

        # Options row
        options_layout = QHBoxLayout()
        options_layout.setContentsMargins(0, 0, 0, 0)
        
        self.chk_case = QCheckBox("Match Case")
        self.chk_word = QCheckBox("Whole Word")
        
        options_layout.addWidget(self.chk_case)
        options_layout.addWidget(self.chk_word)
        options_layout.addStretch()

        layout.addLayout(find_layout)
        layout.addLayout(replace_layout)
        layout.addLayout(options_layout)

    def focus_find(self):
        self.find_input.setFocus()
        self.find_input.selectAll()

    def focus_replace(self):
        self.replace_input.setFocus()
        self.replace_input.selectAll()

    def hide_panel(self):
        self.hide()
        self.close_requested.emit()

    def _on_find_next(self):
        self.find_next_requested.emit(
            self.find_input.text(),
            self.chk_case.isChecked(),
            self.chk_word.isChecked(),
            True
        )

    def _on_find_prev(self):
        self.find_next_requested.emit(
            self.find_input.text(),
            self.chk_case.isChecked(),
            self.chk_word.isChecked(),
            False
        )

    def _on_replace(self):
        self.replace_requested.emit(
            self.find_input.text(),
            self.replace_input.text(),
            self.chk_case.isChecked(),
            self.chk_word.isChecked()
        )

    def _on_replace_all(self):
        self.replace_all_requested.emit(
            self.find_input.text(),
            self.replace_input.text(),
            self.chk_case.isChecked(),
            self.chk_word.isChecked()
        )

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.hide_panel()
        else:
            super().keyPressEvent(event)
