from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPlainTextEdit, QToolButton,
)
from PySide6.QtCore import Signal, QSize

from docx import Document
import io
import os

from icons import icon
from theme import editor_stylesheet, compact_toolbar_stylesheet, ICON_SIZE_COMPACT


class DocxViewer(QWidget):
    """
    DOCX viewer and editor.
    Displays document paragraphs in an editable text area.
    Supports save/load while preserving basic structure.
    """

    textChanged = Signal()

    def __init__(self, file_path=None):
        super().__init__()

        self.file_path = file_path
        self.is_modified = False
        self.docx_content = None
        self._bookmark_callback = None

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(4, 4, 4, 4)
        toolbar.addStretch()

        icon_sz = ICON_SIZE_COMPACT
        icon_qsize = QSize(icon_sz, icon_sz)
        self.btn_bookmark = QToolButton()
        self.btn_bookmark.setIconSize(icon_qsize)
        self.btn_bookmark.setIcon(icon("book-open", size=icon_sz))
        self.btn_bookmark.setToolTip("Bookmark this position")
        self.btn_bookmark.setStyleSheet(compact_toolbar_stylesheet())
        self.btn_bookmark.setAutoRaise(True)
        self.btn_bookmark.clicked.connect(self._add_bookmark_here)
        toolbar.addWidget(self.btn_bookmark)

        self.editor = QPlainTextEdit()
        self.editor.setStyleSheet(editor_stylesheet())
        self.editor.textChanged.connect(self._on_text_changed)

        layout.addLayout(toolbar)
        layout.addWidget(self.editor)
        self.setLayout(layout)

        if file_path:
            self.load_from_path(file_path)

    def set_bookmark_callback(self, callback):
        self._bookmark_callback = callback

    def load_from_path(self, file_path):
        """Load DOCX file from disk."""
        try:
            self.docx_content = Document(file_path)
            self._display_content()
            self.is_modified = False
        except Exception as e:
            raise Exception(f"Failed to load DOCX: {str(e)}")

    def _display_content(self):
        """Extract and display all paragraphs from DOCX."""
        if not self.docx_content:
            return

        text_parts = []

        for para in self.docx_content.paragraphs:
            if para.text.strip():
                text_parts.append(para.text)

        for table in self.docx_content.tables:
            for row in table.rows:
                row_text = " | ".join(cell.text for cell in row.cells)
                if row_text.strip():
                    text_parts.append(row_text)

        combined_text = "\n\n".join(text_parts)

        self.editor.blockSignals(True)
        self.editor.setPlainText(combined_text)
        self.editor.blockSignals(False)

        self.is_modified = False

    def _on_text_changed(self):
        """Mark as modified when user edits."""
        self.is_modified = True
        self.textChanged.emit()

    def _bookmark_payload(self):
        name = os.path.basename(self.file_path) if self.file_path else "document"
        return {
            "page_number": 0,
            "scroll_position_y": float(self.editor.verticalScrollBar().value()),
            "label": f"Position in {name}",
        }

    def _add_bookmark_here(self):
        if self._bookmark_callback:
            self._bookmark_callback(self._bookmark_payload())

    def go_to_bookmark(self, page_number=0, scroll_position_y=0.0):
        self.editor.verticalScrollBar().setValue(int(scroll_position_y))

    def to_docx_bytes(self):
        """
        Convert current editor content back to DOCX bytes.
        Creates a new document with the edited text.
        """
        try:
            new_doc = Document()
            text = self.editor.toPlainText()
            paragraphs = text.split("\n\n")

            for para_text in paragraphs:
                if para_text.strip():
                    new_doc.add_paragraph(para_text)

            byte_stream = io.BytesIO()
            new_doc.save(byte_stream)
            byte_stream.seek(0)

            return byte_stream.getvalue()

        except Exception as e:
            raise Exception(f"Failed to save DOCX: {str(e)}")

    def toPlainText(self):
        """Compatibility method - returns text content."""
        return self.editor.toPlainText()

    def setPlainText(self, text):
        """Compatibility method - set text content (for reopening tabs)."""
        self.editor.blockSignals(True)
        self.editor.setPlainText(text)
        self.editor.blockSignals(False)
        self.is_modified = False
