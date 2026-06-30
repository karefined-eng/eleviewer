from PySide6.QtWidgets import QWidget, QVBoxLayout, QPlainTextEdit, QLabel, QMessageBox
from PySide6.QtCore import Signal
from docx import Document
import io

from theme import viewer_header_stylesheet, editor_stylesheet


class DocxViewer(QWidget):
    """
    DOCX viewer and editor.
    Displays document paragraphs in an editable text area.
    Supports save/load while preserving basic structure.
    """
    
    textChanged = Signal()  # Signal to notify modifications
    
    def __init__(self, file_path=None):
        super().__init__()
        
        self.file_path = file_path
        self.is_modified = False
        self.docx_content = None  # Stores loaded Document object
        
        # UI Setup
        layout = QVBoxLayout()
        
        # Header showing file type
        header = QLabel("📄 DOCX Document Editor")
        header.setStyleSheet(viewer_header_stylesheet())

        self.editor = QPlainTextEdit()
        self.editor.setStyleSheet(editor_stylesheet())
        
        self.editor.textChanged.connect(self._on_text_changed)
        
        layout.addWidget(header)
        layout.addWidget(self.editor)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.setLayout(layout)
        
        # Load file if provided
        if file_path:
            self.load_from_path(file_path)
    
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
        
        # Also extract text from tables
        for table in self.docx_content.tables:
            for row in table.rows:
                row_text = " | ".join(cell.text for cell in row.cells)
                if row_text.strip():
                    text_parts.append(row_text)
        
        combined_text = "\n\n".join(text_parts)
        
        # Load without triggering modification signal
        self.editor.blockSignals(True)
        self.editor.setPlainText(combined_text)
        self.editor.blockSignals(False)
        
        self.is_modified = False
    
    def _on_text_changed(self):
        """Mark as modified when user edits."""
        self.is_modified = True
        self.textChanged.emit()
    
    def to_docx_bytes(self):
        """
        Convert current editor content back to DOCX bytes.
        Creates a new document with the edited text.
        """
        try:
            # Create a new document with edited content
            new_doc = Document()
            
            text = self.editor.toPlainText()
            
            # Split by double newlines (paragraph breaks)
            paragraphs = text.split("\n\n")
            
            for para_text in paragraphs:
                if para_text.strip():
                    new_doc.add_paragraph(para_text)
            
            # Save to bytes
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