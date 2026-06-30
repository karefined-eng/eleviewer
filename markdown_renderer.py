from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QSplitter,
    QPlainTextEdit, QTextBrowser, QLabel,
)
from PySide6.QtCore import Signal, Qt
import markdown

from theme import viewer_header_stylesheet, markdown_editor_stylesheet, MARKDOWN_PREVIEW_CSS


class MarkdownViewer(QWidget):
    """Markdown editor with live HTML preview."""

    textChanged = Signal()

    def __init__(self, file_path=None):
        super().__init__()
        self.file_path = file_path
        self.is_modified = False

        layout = QVBoxLayout(self)

        header = QLabel("📝 Markdown Editor (Live Preview)")
        header.setStyleSheet(viewer_header_stylesheet())

        self.splitter = QSplitter(Qt.Horizontal)

        self.editor = QPlainTextEdit()
        self.editor.setStyleSheet(markdown_editor_stylesheet())
        self.editor.textChanged.connect(self._on_text_changed)

        self.viewer = QTextBrowser()
        self.viewer.setStyleSheet("""
            QTextBrowser {
                background: #252526;
                border: none;
            }
        """)
        self.viewer.setOpenExternalLinks(True)

        self.splitter.addWidget(self.editor)
        self.splitter.addWidget(self.viewer)
        self.splitter.setSizes([400, 400])

        layout.addWidget(header)
        layout.addWidget(self.splitter)
        layout.setContentsMargins(0, 0, 0, 0)

        if file_path:
            self.load_from_path(file_path)

    def _render_markdown(self, text):
        html_body = markdown.markdown(
            text,
            extensions=["tables", "fenced_code", "nl2br", "sane_lists"],
        )
        return f"<html><head><style>{MARKDOWN_PREVIEW_CSS}</style></head><body>{html_body}</body></html>"

    def load_from_path(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.setPlainText(content)
            self.is_modified = False
        except Exception as e:
            raise Exception(f"Failed to load Markdown: {str(e)}")

    def _on_text_changed(self):
        text = self.editor.toPlainText()
        self.viewer.setHtml(self._render_markdown(text))
        self.is_modified = True
        self.textChanged.emit()

    def toPlainText(self):
        return self.editor.toPlainText()

    def setPlainText(self, text):
        self.editor.blockSignals(True)
        self.editor.setPlainText(text)
        self.viewer.setHtml(self._render_markdown(text))
        self.editor.blockSignals(False)
        self.is_modified = False
