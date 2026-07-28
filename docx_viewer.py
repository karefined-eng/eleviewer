from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextBrowser, QToolButton,
)
from PySide6.QtCore import Signal, QSize

import base64
import io
import os

try:
    import mammoth
    MAMMOTH_AVAILABLE = True
except ImportError:
    MAMMOTH_AVAILABLE = False

from docx import Document

from icons import icon
from theme import (
    editor_stylesheet, compact_toolbar_stylesheet, ICON_SIZE_COMPACT,
    BRAND_BACKGROUND, BRAND_PRIMARY, BRAND_BORDER, BRAND_PANEL,
    BRAND_MUTED_FG, get_brand_accent,
)


class DocxViewer(QWidget):
    """
    DOCX viewer and editor.
    Renders rich HTML with embedded Base64 images via mammoth (in QTextBrowser)
    or fallback to python-docx text+image extraction.
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

        self.editor = QTextBrowser()
        self.editor.setOpenExternalLinks(True)
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
        """Render DOCX to rich HTML with base64 images via mammoth, falling back to python-docx extraction."""
        if not self.file_path and not self.docx_content:
            return

        self.editor.blockSignals(True)

        if MAMMOTH_AVAILABLE and self.file_path and os.path.exists(self.file_path):
            try:
                with open(self.file_path, "rb") as docx_file:
                    # Custom image converter: embed images as Base64 data URIs
                    # so they render inline in QTextBrowser without external files
                    result = mammoth.convert_to_html(
                        docx_file,
                        convert_image=mammoth.images.img_element(
                            self._mammoth_image_converter
                        ),
                    )
                    html_content = result.value
                    # Wrap in styled container matching our dark theme
                    styled_html = self._wrap_html(html_content)
                    self.editor.setHtml(styled_html)
                    self.editor.blockSignals(False)
                    self.is_modified = False
                    return
            except Exception as e:
                print(f"[DOCX Viewer] Mammoth HTML conversion failed: {e}")

        # Fallback: python-docx text + image extraction as HTML
        if self.docx_content:
            html = self._build_html_from_docx(self.docx_content)
            styled_html = self._wrap_html(html)
            self.editor.setHtml(styled_html)

        self.editor.blockSignals(False)
        self.is_modified = False

    @staticmethod
    def _mammoth_image_converter(image):
        """Convert mammoth image to Base64 data URI for inline rendering."""
        with image.open() as image_bytes:
            raw = image_bytes.read()
        content_type = image.content_type or "image/png"
        b64 = base64.b64encode(raw).decode("utf-8")
        return {
            "src": f"data:{content_type};base64,{b64}",
        }

    def _build_html_from_docx(self, doc):
        """Build HTML from python-docx Document with embedded Base64 images."""
        html_parts = []

        # Build a map of relationship IDs to image data for quick lookup
        image_map = {}
        try:
            for rel_id, rel in doc.part.rels.items():
                if "image" in rel.reltype:
                    try:
                        img_bytes = rel.target_part.blob
                        content_type = rel.target_part.content_type or "image/png"
                        b64 = base64.b64encode(img_bytes).decode("utf-8")
                        image_map[rel_id] = (content_type, b64)
                    except Exception:
                        pass
        except Exception:
            pass

        # Namespace shortcuts for XML element search
        ns_drawing = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}drawing"
        ns_blip = "{http://schemas.openxmlformats.org/drawingml/2006/main}blip"
        ns_embed = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed"

        for para in doc.paragraphs:
            # Check paragraph style for heading detection
            style_name = (para.style.name or "").lower() if para.style else ""
            tag = "p"
            if "heading 1" in style_name:
                tag = "h1"
            elif "heading 2" in style_name:
                tag = "h2"
            elif "heading 3" in style_name:
                tag = "h3"
            elif "heading 4" in style_name:
                tag = "h4"

            # Collect text and inline images from runs
            run_html = []
            for run in para.runs:
                # Check if this run contains an embedded image (drawing element)
                drawings = run._element.findall(f".//{ns_drawing}")
                if drawings:
                    for drawing in drawings:
                        blips = drawing.findall(f".//{ns_blip}")
                        for blip in blips:
                            embed_id = blip.get(ns_embed)
                            if embed_id and embed_id in image_map:
                                ct, b64 = image_map[embed_id]
                                run_html.append(
                                    f'<img src="data:{ct};base64,{b64}" '
                                    f'style="max-width:100%; border-radius:4px; '
                                    f'margin:8px 0; display:block;" />'
                                )

                # Add text content
                text = run.text
                if text:
                    # Apply basic formatting
                    if run.bold:
                        text = f"<b>{text}</b>"
                    if run.italic:
                        text = f"<i>{text}</i>"
                    if run.underline:
                        text = f"<u>{text}</u>"
                    run_html.append(text)

            content = "".join(run_html)
            if content.strip():
                html_parts.append(f"<{tag}>{content}</{tag}>")

        # Extract tables
        for table in doc.tables:
            table_html = ['<table style="border-collapse:collapse; width:100%; margin:12px 0;">']
            for row_idx, row in enumerate(table.rows):
                table_html.append("<tr>")
                cell_tag = "th" if row_idx == 0 else "td"
                for cell in row.cells:
                    cell_text = cell.text.strip()
                    table_html.append(
                        f'<{cell_tag} style="border:1px solid {BRAND_BORDER}; '
                        f'padding:6px 10px;">{cell_text}</{cell_tag}>'
                    )
                table_html.append("</tr>")
            table_html.append("</table>")
            html_parts.append("".join(table_html))

        return "\n".join(html_parts)

    def _wrap_html(self, body_html):
        """Wrap raw HTML content in a styled document shell matching our dark theme."""
        accent = get_brand_accent()
        return f"""
        <html><head><style>
            body {{
                background: {BRAND_BACKGROUND};
                color: {BRAND_PRIMARY};
                font-family: 'Segoe UI', sans-serif;
                font-size: 15px;
                line-height: 1.7;
                padding: 16px;
                margin: 0;
            }}
            h1, h2, h3, h4 {{ color: {BRAND_PRIMARY}; margin-top: 1.2em; }}
            h1 {{ font-size: 22px; border-bottom: 1px solid {BRAND_BORDER}; padding-bottom: 8px; }}
            h2 {{ font-size: 18px; }}
            h3 {{ font-size: 16px; }}
            a {{ color: {accent}; }}
            table {{ border-collapse: collapse; width: 100%; margin: 12px 0; }}
            th {{ background: {BRAND_PANEL}; font-weight: bold; }}
            td, th {{ border: 1px solid {BRAND_BORDER}; padding: 6px 10px; }}
            img {{ max-width: 100%; border-radius: 4px; margin: 8px 0; }}
            p {{ margin: 0.5em 0; }}
        </style></head><body>{body_html}</body></html>
        """

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

    def read_current_page(self, voice_id=None):
        """Duck-typed method for TTS engine. Reads selection or full text."""
        cursor = self.editor.textCursor()
        text = cursor.selectedText()
        if not text:
            text = self.editor.toPlainText()
        return text

    def setPlainText(self, text):
        """Compatibility method - set text content (for reopening tabs)."""
        self.editor.blockSignals(True)
        self.editor.setPlainText(text)
        self.editor.blockSignals(False)
        self.is_modified = False
