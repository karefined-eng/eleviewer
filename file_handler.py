from pathlib import Path

from editor import EditorTab
from docx_viewer import DocxViewer
from xlsx_viewer import XlsxViewer
from pptx_viewer import PptxViewer
from markdown_renderer import MarkdownViewer
from pdf_viewer import PdfViewer
from csv_viewer import CsvViewer
from html_viewer import HtmlViewer

BINARY_FORMATS = {"docx", "xlsx", "pdf", "pptx"}
TEXT_RESTORE_FORMATS = {"txt", "md", "csv", "tsv", "html", "htm", ""}


def get_file_extension(file_path):
    """Extract file extension from path (without dot)."""
    if not file_path:
        return ""
    return Path(file_path).suffix.lstrip(".").lower()


def is_binary_format(file_path):
    return get_file_extension(file_path) in BINARY_FORMATS


# FIX: UTF-8 with latin-1 fallback prevents UnicodeDecodeError crash
def _read_file_safely(file_path: str) -> str:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        with open(file_path, "r", encoding="latin-1", errors="replace") as f:
            return f.read()
    except OSError as e:
        return f"[EleViewer] Could not read file: {e}"


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

    elif ext in ("csv", "tsv"):
        viewer = CsvViewer(file_path, content=content)
        viewer.file_path = file_path
        return viewer

    elif ext == "md":
        viewer = MarkdownViewer(file_path, is_html=False)
        viewer.file_path = file_path
        if content is not None:
            viewer.setPlainText(content)
        return viewer

    elif ext in ("html", "htm"):
        viewer = HtmlViewer(file_path, content=content)
        viewer.file_path = file_path
        return viewer

    elif ext == "pdf":
        viewer = PdfViewer(file_path)
        viewer.file_path = file_path
        return viewer

    elif ext == "pptx":
        viewer = PptxViewer(file_path)
        viewer.file_path = file_path
        return viewer

    else:
        editor = EditorTab()
        editor.file_path = file_path

        if content is None:
            content = _read_file_safely(file_path)

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

    elif ext in ("csv", "tsv"):
        return widget.toPlainText()

    else:
        return widget.toPlainText()
