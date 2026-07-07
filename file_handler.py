from pathlib import Path

from editor import EditorTab
from docx_viewer import DocxViewer
from xlsx_viewer import XlsxViewer
from markdown_renderer import MarkdownViewer
from pdf_viewer import PdfViewer

BINARY_FORMATS = {"docx", "xlsx", "pdf"}
TEXT_RESTORE_FORMATS = {"txt", "md", ""}


def get_file_extension(file_path):
    """Extract file extension from path (without dot)."""
    if not file_path:
        return ""
    return Path(file_path).suffix.lstrip(".").lower()


def is_binary_format(file_path):
    return get_file_extension(file_path) in BINARY_FORMATS


def create_viewer_widget(file_path, content=None):
    """
    Factory function: returns the correct viewer widget based on file type.
    """
    ext = get_file_extension(file_path)

    if ext == "docx":
        viewer = DocxViewer(file_path)
        viewer.file_path = file_path
        return viewer

    elif ext == "xlsx":
        viewer = XlsxViewer(file_path)
        viewer.file_path = file_path
        return viewer

    elif ext in ("md", "html", "htm"):
        viewer = MarkdownViewer(file_path, is_html=(ext in ("html", "htm")))
        viewer.file_path = file_path
        if content is not None:
            viewer.setPlainText(content)
        return viewer

    elif ext == "pdf":
        viewer = PdfViewer(file_path)
        viewer.file_path = file_path
        return viewer

    else:
        editor = EditorTab()
        editor.file_path = file_path

        if content is None:
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()
            except Exception as e:
                raise Exception(f"Failed to read file: {str(e)}")

        editor.setPlainText(content)
        editor.is_modified = False
        return editor


def get_file_content(widget, file_path):
    """Extract content from any widget type."""
    ext = get_file_extension(file_path)

    if ext == "docx":
        return widget.to_docx_bytes()

    elif ext == "xlsx":
        return widget.to_xlsx_bytes()

    else:
        return widget.toPlainText()
