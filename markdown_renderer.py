from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QStackedWidget,
    QPlainTextEdit, QTextBrowser, QToolButton, QHBoxLayout, QLabel,
)
from PySide6.QtCore import Signal, Qt, QEvent, QTimer, QSize, QObject
from PySide6.QtGui import QMouseEvent
import markdown

from icons import icon
from markdown_utils import markdown_to_simple, simple_to_markdown
from settings import load_settings
from theme import markdown_editor_stylesheet, MARKDOWN_PREVIEW_CSS, compact_toolbar_stylesheet

MODE_VIEW = 0
MODE_SIMPLE = 1
MODE_SYNTAX = 2


class PreviewEventFilter(QObject):
    """Detect double/triple click on preview to switch edit modes."""

    def __init__(self, viewer):
        super().__init__()
        self._viewer = viewer
        self._click_count = 0
        self._click_timer = QTimer()
        self._click_timer.setSingleShot(True)
        self._click_timer.setInterval(450)
        self._click_timer.timeout.connect(self._reset_clicks)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress and isinstance(event, QMouseEvent):
            if event.button() == Qt.LeftButton:
                self._click_count += 1
                self._click_timer.start()
                if self._click_count >= 3:
                    self._viewer.enter_syntax_mode()
                    self._reset_clicks()
                elif self._click_count == 2:
                    QTimer.singleShot(300, self._check_double_click)
            return False
        return False

    def _check_double_click(self):
        if self._click_count == 2:
            self._viewer.enter_simple_mode()
        self._reset_clicks()

    def _reset_clicks(self):
        self._click_count = 0
        self._click_timer.stop()


class MarkdownViewer(QWidget):
    textChanged = Signal()

    def __init__(self, file_path=None):
        super().__init__()
        self.file_path = file_path
        self.is_modified = False
        self._mode = MODE_VIEW
        self._icon_size = load_settings().get("markdown_icon_size", 32)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(8, 4, 8, 0)

        self.hint = QLabel("Double-click to edit · Triple-click for syntax")
        self.hint.setStyleSheet("color: #666; font-size: 11px;")
        toolbar.addWidget(self.hint)
        toolbar.addStretch()

        self.mode_btn = QToolButton()
        self.mode_btn.setAutoRaise(True)
        self.mode_btn.setIconSize(QSize(self._icon_size, self._icon_size))
        self.mode_btn.setStyleSheet(compact_toolbar_stylesheet())
        self.mode_btn.clicked.connect(self._toggle_syntax_from_view)
        toolbar.addWidget(self.mode_btn)

        self.stack = QStackedWidget()

        self.viewer = QTextBrowser()
        self.viewer.setStyleSheet("QTextBrowser { background: #252526; border: none; }")
        self.viewer.setOpenExternalLinks(True)
        self._preview_filter = PreviewEventFilter(self)
        self.viewer.installEventFilter(self._preview_filter)

        self.simple_editor = QPlainTextEdit()
        self.simple_editor.setStyleSheet("""
            QPlainTextEdit {
                background: #252526;
                color: #e0e0e0;
                font-size: 15px;
                padding: 16px;
                border: none;
                font-family: 'Segoe UI', sans-serif;
                line-height: 1.6;
            }
        """)
        self.simple_editor.textChanged.connect(self._on_simple_changed)

        self.editor = QPlainTextEdit()
        self.editor.setStyleSheet(markdown_editor_stylesheet())
        self.editor.textChanged.connect(self._on_syntax_changed)

        self.stack.addWidget(self.viewer)
        self.stack.addWidget(self.simple_editor)
        self.stack.addWidget(self.editor)

        layout.addLayout(toolbar)
        layout.addWidget(self.stack)

        if file_path:
            self.load_from_path(file_path)
        else:
            self.enter_view_mode()

    def _render_markdown(self, text):
        html_body = markdown.markdown(
            text,
            extensions=["tables", "fenced_code", "nl2br", "sane_lists"],
        )
        return f"<html><head><style>{MARKDOWN_PREVIEW_CSS}</style></head><body>{html_body}</body></html>"

    def _sync_from_syntax(self):
        text = self.editor.toPlainText()
        self.simple_editor.blockSignals(True)
        self.simple_editor.setPlainText(markdown_to_simple(text))
        self.simple_editor.blockSignals(False)
        self.viewer.setHtml(self._render_markdown(text))

    def enter_view_mode(self):
        self._sync_from_syntax()
        self._mode = MODE_VIEW
        self.stack.setCurrentIndex(MODE_VIEW)
        self.hint.setVisible(True)
        self._update_mode_button()

    def enter_simple_mode(self):
        if self._mode == MODE_VIEW:
            self.simple_editor.setPlainText(markdown_to_simple(self.editor.toPlainText()))
        self._mode = MODE_SIMPLE
        self.stack.setCurrentIndex(MODE_SIMPLE)
        self.hint.setVisible(False)
        self._update_mode_button()

    def enter_syntax_mode(self):
        if self._mode == MODE_SIMPLE:
            self.editor.setPlainText(simple_to_markdown(self.simple_editor.toPlainText()))
        self._mode = MODE_SYNTAX
        self.stack.setCurrentIndex(MODE_SYNTAX)
        self.hint.setVisible(False)
        self._update_mode_button()

    def _toggle_syntax_from_view(self):
        if self._mode == MODE_VIEW:
            self.enter_syntax_mode()
        else:
            self.enter_view_mode()

    def _update_mode_button(self):
        size = load_settings().get("markdown_icon_size", 32)
        self.mode_btn.setIconSize(QSize(size, size))
        if self._mode == MODE_VIEW:
            self.mode_btn.setIcon(icon("pencil", size=size))
            self.mode_btn.setToolTip("Switch to syntax edit")
        else:
            self.mode_btn.setIcon(icon("book-open", size=size))
            self.mode_btn.setToolTip("Switch to view mode")

    def load_from_path(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.setPlainText(content)
            default = load_settings().get("markdown_default_mode", "view")
            if default == "syntax":
                self.enter_syntax_mode()
            elif default == "simple":
                self.enter_simple_mode()
            else:
                self.enter_view_mode()
            self.is_modified = False
        except Exception as e:
            raise Exception(f"Failed to load Markdown: {str(e)}")

    def _on_syntax_changed(self):
        self.is_modified = True
        self.textChanged.emit()

    def _on_simple_changed(self):
        self.editor.blockSignals(True)
        self.editor.setPlainText(simple_to_markdown(self.simple_editor.toPlainText()))
        self.editor.blockSignals(False)
        self.is_modified = True
        self.textChanged.emit()

    def toPlainText(self):
        if self._mode == MODE_SIMPLE:
            return simple_to_markdown(self.simple_editor.toPlainText())
        return self.editor.toPlainText()

    def setPlainText(self, text):
        self.editor.blockSignals(True)
        self.simple_editor.blockSignals(True)
        self.editor.setPlainText(text)
        self.simple_editor.setPlainText(markdown_to_simple(text))
        self.viewer.setHtml(self._render_markdown(text))
        self.editor.blockSignals(False)
        self.simple_editor.blockSignals(False)
        self.is_modified = False
