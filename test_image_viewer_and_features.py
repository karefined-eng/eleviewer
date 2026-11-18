"""Tests for newly added core study workspace features:
- PDF in-document search (Ctrl+F)
- Image file viewer & routing
- Undo / redo buttons in Editor & MarkdownViewer
"""

import os
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPixmap, QPainter, QColor
from PySide6.QtCore import Qt

from file_handler import create_viewer_widget, get_file_extension, is_binary_format, IMAGE_FORMATS
from image_viewer import ImageViewer
from editor import EditorTab
from markdown_renderer import MarkdownViewer, MODE_SIMPLE, MODE_SYNTAX


def test_image_formats_routing():
    for ext in ("png", "jpg", "jpeg", "gif", "bmp", "svg", "webp", "ico"):
        assert ext in IMAGE_FORMATS
        assert is_binary_format(f"test.{ext}")


def test_image_viewer_creation_and_zoom():
    app = QApplication.instance() or QApplication([])

    # Create dummy PNG image
    test_img_path = "test_temp_img.png"
    pix = QPixmap(100, 80)
    pix.fill(QColor("blue"))
    pix.save(test_img_path)

    try:
        viewer = create_viewer_widget(test_img_path)
        assert isinstance(viewer, ImageViewer)
        assert viewer.file_path == test_img_path
        assert viewer.toPlainText() == ""
        assert viewer.is_modified is False
        assert viewer._orig_pixmap is not None
        assert viewer._orig_pixmap.width() == 100
        assert viewer._orig_pixmap.height() == 80

        # Test zoom controls
        init_zoom = viewer._zoom_factor
        viewer.zoom_in()
        assert viewer._zoom_factor > init_zoom
        viewer.zoom_out()
        viewer.actual_size()
        assert viewer._zoom_factor == 1.0
        viewer.fit_to_window()
        assert viewer._fit_to_window is True

        viewer.close()
        viewer.deleteLater()
    finally:
        if os.path.exists(test_img_path):
            os.remove(test_img_path)


def test_editor_undo_redo_buttons():
    app = QApplication.instance() or QApplication([])

    editor = EditorTab()
    assert hasattr(editor, "btn_undo")
    assert hasattr(editor, "btn_redo")

    editor.editor.insertPlainText("First text")
    cursor = editor.editor.textCursor()
    cursor.beginEditBlock()
    cursor.insertText(" - added text")
    cursor.endEditBlock()
    assert "First text - added text" in editor.toPlainText()

    editor.btn_undo.click()
    app.processEvents()
    assert editor.toPlainText().strip() == "First text"

    editor.btn_redo.click()
    app.processEvents()
    assert editor.toPlainText().strip() == "First text - added text"

    editor.close()
    editor.deleteLater()


def test_markdown_undo_redo_buttons():
    app = QApplication.instance() or QApplication([])

    mv = MarkdownViewer(file_path=None, is_html=False)
    assert hasattr(mv, "btn_undo")
    assert hasattr(mv, "btn_redo")

    mv.enter_simple_mode()
    mv.simple_editor.insertPlainText("Step 1")
    cursor = mv.simple_editor.textCursor()
    cursor.beginEditBlock()
    cursor.insertText(" Step 2")
    cursor.endEditBlock()
    assert "Step 1 Step 2" in mv.simple_editor.toPlainText()

    mv.btn_undo.click()
    app.processEvents()
    assert mv.simple_editor.toPlainText().strip() == "Step 1"

    mv.btn_redo.click()
    app.processEvents()
    assert mv.simple_editor.toPlainText().strip() == "Step 1 Step 2"

    mv.close()
    mv.deleteLater()


def test_pdf_search_bar_wiring():
    app = QApplication.instance() or QApplication([])

    from pdf_viewer import PdfViewer, QTPDF_AVAILABLE
    if not QTPDF_AVAILABLE:
        return

    viewer = PdfViewer()
    assert hasattr(viewer, "search_bar_widget")
    assert hasattr(viewer, "search_input")
    assert hasattr(viewer, "btn_search")
    assert hasattr(viewer, "btn_search_prev")
    assert hasattr(viewer, "btn_search_next")
    assert hasattr(viewer, "lbl_search_count")

    # Search bar initially hidden
    assert viewer._search_visible is False
    assert viewer.search_bar_widget.isHidden()

    # Toggle search
    viewer._toggle_search()
    assert viewer._search_visible is True
    assert viewer.search_bar_widget.isVisible()

    # Hide search
    viewer._hide_search()
    assert viewer._search_visible is False
    assert viewer.search_bar_widget.isHidden()

    viewer.close()
    viewer.deleteLater()


if __name__ == "__main__":
    test_image_formats_routing()
    print("test_image_formats_routing passed")
    test_image_viewer_creation_and_zoom()
    print("test_image_viewer_creation_and_zoom passed")
    test_editor_undo_redo_buttons()
    print("test_editor_undo_redo_buttons passed")
    test_markdown_undo_redo_buttons()
    print("test_markdown_undo_redo_buttons passed")
    test_pdf_search_bar_wiring()
    print("test_pdf_search_bar_wiring passed")
    print("ALL TESTS PASSED!")
