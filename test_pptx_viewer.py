from pptx import Presentation
from pptx.util import Inches
from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication

import pptx_viewer


def test_embedded_images_keep_slide_order(tmp_path, monkeypatch):
    app = QApplication.instance() or QApplication([])
    monkeypatch.setattr(pptx_viewer, "_WEB_AVAILABLE", False)

    image_path = tmp_path / "embedded.png"
    image = QImage(12, 8, QImage.Format.Format_RGB32)
    image.fill(0x2A82DA)
    assert image.save(str(image_path), "PNG")

    presentation_path = tmp_path / "ordered.pptx"
    presentation = Presentation()
    slide = presentation.slides.add_slide(presentation.slide_layouts[6])
    before = slide.shapes.add_textbox(Inches(1), Inches(0.5), Inches(5), Inches(0.5))
    before.text = "Text before image"
    slide.shapes.add_picture(str(image_path), Inches(1), Inches(1.2), width=Inches(2))
    after = slide.shapes.add_textbox(Inches(1), Inches(3), Inches(5), Inches(0.5))
    after.text = "Text after image"
    presentation.save(str(presentation_path))

    viewer = pptx_viewer.PptxViewer(str(presentation_path))
    try:
        elements = viewer.slides[0]["elements"]
        assert [kind for kind, _ in elements] == ["text", "image", "text"]
        # Values for text elements are now rich dicts with a "text" key
        assert elements[0][1]["text"] == "Text before image"
        assert elements[2][1]["text"] == "Text after image"

        rendered = viewer._render_qtext_elements(elements, ["pptx-img://0/0.png"])
        assert rendered.index("Text before image") < rendered.index("pptx-img://0/0.png")
        assert rendered.index("pptx-img://0/0.png") < rendered.index("Text after image")
    finally:
        viewer.close()


def test_invalid_qtext_image_gets_visible_placeholder():
    app = QApplication.instance() or QApplication([])
    viewer = pptx_viewer.PptxViewer()
    try:
        rendered = viewer._render_qtext_elements(
            [("text", "Slide text"), ("image", (b"not-an-image", "emf"))],
            [None],
        )
        assert "not supported on this system" in rendered
    finally:
        viewer.close()


def _build_titled_presentation(tmp_path):
    presentation = Presentation()
    slide = presentation.slides.add_slide(presentation.slide_layouts[1])
    slide.shapes.title.text = "Deck Title"
    slide.placeholders[1].text = "Point A"
    path = tmp_path / "titled.pptx"
    presentation.save(str(path))
    return path


def test_title_placeholder_not_repeated_in_body(tmp_path, monkeypatch):
    app = QApplication.instance() or QApplication([])
    monkeypatch.setattr(pptx_viewer, "_WEB_AVAILABLE", False)
    path = _build_titled_presentation(tmp_path)

    viewer = pptx_viewer.PptxViewer(str(path))
    try:
        slide_data = viewer.slides[0]
        assert slide_data["title"] == "Deck Title"
        body_texts = [
            val["text"] for kind, val in slide_data["elements"] if kind == "text"
        ]
        assert body_texts == ["Point A"]
        # TTS/search content must carry the body once, not the title twice
        assert slide_data["content"] == "Point A"
    finally:
        viewer.close()


def test_fallback_zip_parse_keeps_title_out_of_body(tmp_path, monkeypatch):
    app = QApplication.instance() or QApplication([])
    monkeypatch.setattr(pptx_viewer, "_WEB_AVAILABLE", False)
    path = _build_titled_presentation(tmp_path)

    viewer = pptx_viewer.PptxViewer()
    try:
        viewer._fallback_zip_parse(str(path))
        assert len(viewer.slides) == 1
        assert viewer.slides[0]["title"] == "Deck Title"
        assert viewer.slides[0]["content"] == "Point A"
    finally:
        viewer.close()


def test_search_no_match_wraps_without_crash(tmp_path, monkeypatch):
    app = QApplication.instance() or QApplication([])
    monkeypatch.setattr(pptx_viewer, "_WEB_AVAILABLE", False)
    path = _build_titled_presentation(tmp_path)

    viewer = pptx_viewer.PptxViewer(str(path))
    try:
        viewer.search_input.setText("zzz-no-such-text")
        viewer._perform_search()
    finally:
        viewer.close()


def test_scroll_bridge_updates_sidebar_state():
    app = QApplication.instance() or QApplication([])
    viewer = pptx_viewer.PptxViewer()
    try:
        viewer.slides = [
            {"title": "One", "content": "a", "elements": [], "notes": ""},
            {"title": "Two", "content": "b", "elements": [], "notes": ""},
        ]
        viewer.total_slides = 2
        viewer.slide_list.clear()
        viewer.slide_list.addItem("1. One")
        viewer.slide_list.addItem("2. Two")

        bridge = pptx_viewer._SlideScrollBridge(viewer)
        bridge.reportActiveSlide(1)
        assert viewer.current_slide == 1
        assert viewer.slide_input.text() == "2"
        assert viewer.slide_list.currentRow() == 1

        # Reports are ignored while a programmatic jump is in flight
        viewer._is_jumping = True
        bridge.reportActiveSlide(0)
        assert viewer.current_slide == 1

        # Out-of-range reports are dropped
        viewer._is_jumping = False
        bridge.reportActiveSlide(9)
        assert viewer.current_slide == 1
    finally:
        viewer.close()
