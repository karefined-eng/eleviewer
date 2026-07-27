"""PowerPoint (.pptx) Viewer component for EleViewer.

Extracts slide text, titles, notes, and bullet points using python-pptx
(with a zipfile XML fallback if python-pptx is unavailable).
Renders clean slide cards with toolbar navigation and TTS read-aloud support.
"""

import os
import zipfile
import xml.etree.ElementTree as ET

try:
    import pptx
    PPTX_AVAILABLE = True
except ImportError:
    PPTX_AVAILABLE = False

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QToolButton, QLabel,
    QTextBrowser, QLineEdit, QSplitter, QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIntValidator, QKeyEvent

from icons import icon
from theme import compact_toolbar_stylesheet, ICON_SIZE_COMPACT, BRAND_PANEL, BRAND_BORDER, BRAND_PRIMARY, BRAND_MUTED_FG, get_brand_accent
from tts_engine import TtsEngine


class PptxViewer(QWidget):
    """Slide-by-slide PowerPoint reader with TTS integration."""

    textChanged = Signal()

    def __init__(self, file_path=None, status_callback=None):
        super().__init__()
        self.file_path = file_path
        self.is_modified = False
        self._status_callback = status_callback
        self.slides = []  # list of dicts: {"title": str, "content": str, "notes": str}
        self.current_slide = 0
        self.total_slides = 0

        self.tts = TtsEngine(on_error=self._on_tts_error)

        self.setFocusPolicy(Qt.StrongFocus)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Toolbar ─────────────────────────────────────────────────
        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(6, 4, 6, 4)
        toolbar.setSpacing(4)
        icon_sz = ICON_SIZE_COMPACT
        icon_qsize = QSize(icon_sz, icon_sz)

        def _tb(icon_name, tooltip, slot, text=None):
            btn = QToolButton()
            btn.setIconSize(icon_qsize)
            btn.setIcon(icon(icon_name, size=icon_sz))
            if text:
                btn.setText(f" {text}")
                btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
                btn.setStyleSheet(compact_toolbar_stylesheet() + " QToolButton { font-size: 11px; padding: 2px 6px; }")
            else:
                btn.setStyleSheet(compact_toolbar_stylesheet())
            btn.setToolTip(tooltip)
            btn.setAutoRaise(True)
            btn.clicked.connect(slot)
            return btn

        self.btn_prev = _tb("chevron-left", "Previous Slide", self.prev_slide)
        self.btn_next = _tb("chevron-right", "Next Slide", self.next_slide)

        self.slide_input = QLineEdit()
        self.slide_input.setFixedWidth(44)
        self.slide_input.setAlignment(Qt.AlignCenter)
        self.slide_input.setValidator(QIntValidator(1, 9999))
        self.slide_input.setStyleSheet(
            "QLineEdit { background:#242424; color:#f2f2f0; border:1px solid #2c2c2c;"
            " border-radius:4px; padding:2px 4px; font-weight:bold; font-size:12px; }"
        )
        self.slide_input.returnPressed.connect(self._jump_to_slide)
        self.lbl_total = QLabel(" / 0")
        self.lbl_total.setStyleSheet("color:#9b9b96; font-weight:bold; padding:0 6px 0 2px; font-size:12px;")

        toolbar.addWidget(self.btn_prev)
        toolbar.addWidget(self.slide_input)
        toolbar.addWidget(self.lbl_total)
        toolbar.addWidget(self.btn_next)
        toolbar.addStretch()

        # ── Main Splitter: Slide list + Slide Viewer ────────────────
        self.splitter = QSplitter(Qt.Horizontal)

        self.slide_list = QListWidget()
        self.slide_list.setMaximumWidth(220)
        self.slide_list.setStyleSheet(f"""
            QListWidget {{
                background: {BRAND_PANEL};
                color: {BRAND_PRIMARY};
                border-right: 1px solid {BRAND_BORDER};
                font-size: 12px;
            }}
            QListWidget::item {{ padding: 6px; border-bottom: 1px solid #222; }}
            QListWidget::item:selected {{ background: {get_brand_accent()}; color: #131313; font-weight: bold; }}
        """)
        self.slide_list.currentRowChanged.connect(self.go_to_slide)

        self.viewer = QTextBrowser()
        self.viewer.setStyleSheet(f"""
            QTextBrowser {{
                background: #131313;
                color: #f2f2f0;
                border: none;
                padding: 20px;
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
            }}
        """)
        self.viewer.setOpenExternalLinks(True)

        self.splitter.addWidget(self.slide_list)
        self.splitter.addWidget(self.viewer)

        layout.addLayout(toolbar)
        layout.addWidget(self.splitter)

        if file_path:
            self.load_from_path(file_path)

    def load_from_path(self, file_path):
        self.file_path = file_path
        self.slides = []

        if PPTX_AVAILABLE:
            try:
                prs = pptx.Presentation(file_path)
                for idx, slide in enumerate(prs.slides, start=1):
                    title = f"Slide {idx}"
                    texts = []
                    image_count = 0
                    for shape in slide.shapes:
                        if shape.has_text_frame:
                            for paragraph in shape.text_frame.paragraphs:
                                text = paragraph.text.strip()
                                if text:
                                    if not texts and shape == slide.shapes.title:
                                        title = text
                                    texts.append(text)
                        elif hasattr(shape, "shape_type"):
                            # MSO_SHAPE_TYPE.PICTURE == 13
                            try:
                                from pptx.enum.shapes import MSO_SHAPE_TYPE
                                if shape.shape_type == MSO_SHAPE_TYPE.PICTURE:
                                    try:
                                        import base64
                                        img_bytes = shape.image.blob
                                        img_ext = shape.image.ext.lower()
                                        if img_bytes and img_ext:
                                            b64_data = base64.b64encode(img_bytes).decode('utf-8')
                                            mime_type = "image/jpeg" if img_ext == "jpg" else f"image/{img_ext}"
                                            texts.append(f'<img src="data:{mime_type};base64,{b64_data}" style="max-width:100%; border-radius:4px; margin-top:10px; margin-bottom:10px;" />')
                                            image_count += 1
                                    except Exception as e:
                                        print(f"Failed to extract image: {e}")
                            except Exception:
                                pass
                    notes = ""
                    if slide.has_notes_slide and slide.notes_slide.notes_text_frame:
                        notes = slide.notes_slide.notes_text_frame.text.strip()

                    self.slides.append({
                        "title": title,
                        "content": "\n\n".join(texts),
                        "notes": notes,
                    })
            except Exception as e:
                print(f"[PPTX Viewer] python-pptx load failed: {e}")
                self._fallback_zip_parse(file_path)
        else:
            self._fallback_zip_parse(file_path)

        self.total_slides = len(self.slides)
        self.lbl_total.setText(f" / {self.total_slides}")

        self.slide_list.clear()
        for idx, s in enumerate(self.slides, start=1):
            title_text = s["title"][:28] + ("…" if len(s["title"]) > 28 else "")
            item = QListWidgetItem(f"{idx}. {title_text}")
            self.slide_list.addItem(item)

        if self.total_slides > 0:
            self.go_to_slide(0)

    def _fallback_zip_parse(self, file_path):
        """Fallback parser extracting slide text XML from pptx zip container."""
        try:
            with zipfile.ZipFile(file_path, "r") as z:
                slide_files = sorted(
                    [name for name in z.namelist() if name.startswith("ppt/slides/slide") and name.endswith(".xml")]
                )
                for idx, sfile in enumerate(slide_files, start=1):
                    xml_content = z.read(sfile)
                    tree = ET.fromstring(xml_content)
                    texts = []
                    for elem in tree.iter():
                        if elem.tag.endswith("}t") and elem.text:
                            t = elem.text.strip()
                            if t:
                                texts.append(t)
                    title = f"Slide {idx}"
                    if texts:
                        title = texts[0]
                    self.slides.append({
                        "title": title,
                        "content": "\n\n".join(texts),
                        "notes": "",
                    })
        except Exception as e:
            print(f"[PPTX Viewer] Fallback zip parse error: {e}")

    def _on_tts_error(self, message):
        if self._status_callback:
            self._status_callback(f"TTS error: {message}", 4000)

    def go_to_slide(self, index):
        if index < 0 or index >= self.total_slides:
            return
        self.current_slide = index
        self.slide_input.setText(str(index + 1))
        self.slide_list.setCurrentRow(index)

        slide_data = self.slides[index]
        accent = get_brand_accent()

        html = f"""
        <div style="max-width: 700px; margin: 0 auto;">
            <div style="color: {accent}; font-size: 11px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;">
                SLIDE {index + 1} OF {self.total_slides}
            </div>
            <h1 style="color: #ffffff; font-size: 22px; margin-top: 0; margin-bottom: 20px; border-bottom: 1px solid #2c2c2c; padding-bottom: 10px;">
                {slide_data['title']}
            </h1>
            <div style="font-size: 15px; line-height: 1.7; color: #e0e0e0; white-space: pre-wrap;">
                {slide_data['content'] or '<i>(No text content on this slide)</i>'}
            </div>
        """

        if slide_data.get("notes"):
            html += f"""
            <div style="margin-top: 30px; padding: 12px; background: #1c1c1c; border-left: 3px solid {accent}; border-radius: 4px;">
                <div style="color: #9b9b96; font-size: 11px; font-weight: bold; margin-bottom: 4px;">SPEAKER NOTES</div>
                <div style="font-size: 13px; color: #cccccc;">{slide_data['notes']}</div>
            </div>
            """

        html += "</div>"
        self.viewer.setHtml(html)

    def prev_slide(self):
        if self.current_slide > 0:
            self.go_to_slide(self.current_slide - 1)

    def next_slide(self):
        if self.current_slide < self.total_slides - 1:
            self.go_to_slide(self.current_slide + 1)

    def _jump_to_slide(self):
        try:
            s = int(self.slide_input.text()) - 1
            self.go_to_slide(s)
        except ValueError:
            pass

    def read_current_page(self, voice_id=None):
        """TTS helper to read the active slide content."""
        if 0 <= self.current_slide < self.total_slides:
            slide_data = self.slides[self.current_slide]
            text = f"{slide_data['title']}. {slide_data['content']}"
            if text.strip():
                self.tts.speak(text, voice_id=voice_id)
                if self._status_callback:
                    self._status_callback(f"Reading slide {self.current_slide + 1} aloud...", 2000)
                return text
        return ""

    def toPlainText(self):
        """Return all text content across all slides."""
        full_text = []
        for idx, s in enumerate(self.slides, start=1):
            full_text.append(f"--- Slide {idx}: {s['title']} ---\n{s['content']}\n")
        return "\n".join(full_text)

    def setPlainText(self, text):
        pass

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        if key in (Qt.Key_Left, Qt.Key_PageUp):
            self.prev_slide()
            event.accept()
        elif key in (Qt.Key_Right, Qt.Key_PageDown):
            self.next_slide()
            event.accept()
        else:
            super().keyPressEvent(event)
