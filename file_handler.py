from editor import EditorTab
from docx_viewer import DocxViewer
from xlsx_viewer import XlsxViewer


def get_file_extension(file_path):
    """Extract file extension from path."""
    return file_path.split(".")[-1].lower()


def create_viewer_widget(file_path, content=None):
    """
    Factory function: returns the correct viewer widget based on file type.
    
    Args:
        file_path: Path to the file being opened
        content: Optional pre-loaded content (for reopening closed tabs)
    
    Returns:
        A widget that supports: 
        - .file_path attribute
        - .is_modified attribute
        - .textChanged or equivalent signal
        - save() method or toPlainText() / toDocxBytes() / toXlsxBytes() for getting content
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
    
    else:
        # Plain text editor for .txt, .md, and unknown types
        editor = EditorTab()
        editor.file_path = file_path
        
        # Load file content if not provided
        if content is None:
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()
            except Exception as e:
                raise Exception(f"Failed to read file: {str(e)}")
        
        # Set the content
        editor.setPlainText(content)
        editor.is_modified = False
        
        return editor


def get_file_content(widget, file_path):
    """
    Extract content from any widget type.
    Returns content as the appropriate type (str for text, bytes for DOCX/XLSX).
    """
    
    ext = get_file_extension(file_path)
    
    if ext == "docx":
        return widget.to_docx_bytes()
    
    elif ext == "xlsx":
        return widget.to_xlsx_bytes()
    
    else:
        # Plain text
        return widget.toPlainText()