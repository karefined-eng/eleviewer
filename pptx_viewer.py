"""PowerPoint (.pptx) Viewer component for EleViewer.

Extracts slide text, titles, notes, and bullet points using python-pptx
(with a zipfile XML fallback if python-pptx is unavailable).
Renders clean slide cards with toolbar navigation and TTS read-aloud support.
"""

import os
import zipfile
import xml.etree.ElementTree as ET

try:
    import pptx  # type: ignore
    PPTX_AVAILABLE = True
except ImportError:
    PPTX_AVAILABLE = False

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QToolButton, QLabel,
    QTextBrowser, QLineEdit, QSplitter, QListWidget, QListWidgetItem, QFrame
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIntValidator, QKeyEvent, QShortcut, QKeySequence

from icons import icon
from theme import (
    compact_toolbar_stylesheet, ICON_SIZE_COMPACT,
    BRAND_PANEL, BRAND_PANEL_2, BRAND_BORDER, BRAND_PRIMARY,
    BRAND_MUTED_FG, BRAND_BACKGROUND, get_brand_accent,
)


class PptxViewer(QWidget):
    """Slide-by-slide PowerPoint reader with TTS integration."""

    textChanged = Signal()

    def __init__(self, file_path=None, status_callback=None):
        super().__init__()
        self.file_path = file_path
        self.is_modified = False
        self._status_callback = status_callback
        self._bookmark_callback = None
        self.slides = []  # list of dicts: {"title": str, "content": str, "notes": str}
        self.current_slide = 0
        self.total_slides = 0

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
        self.btn_bookmark = _tb("book-open", "Bookmark this slide", self._add_bookmark_here)

        self.slide_input = QLineEdit()
        self.slide_input.setFixedWidth(44)
        self.slide_input.setAlignment(Qt.AlignCenter)
        self.slide_input.setValidator(QIntValidator(1, 9999))
        self.slide_input.setStyleSheet(
            f"QLineEdit {{ background:{BRAND_PANEL_2}; color:{BRAND_PRIMARY}; border:1px solid {BRAND_BORDER};"
            f" border-radius:4px; padding:2px 4px; font-weight:bold; font-size:12px; }}"
        )
        self.slide_input.returnPressed.connect(self._jump_to_slide)
        self.lbl_total = QLabel(" / 0")
        self.lbl_total.setStyleSheet(f"color:{BRAND_MUTED_FG}; font-weight:bold; padding:0 6px 0 2px; font-size:12px;")

        toolbar.addWidget(self.btn_prev)
        toolbar.addWidget(self.slide_input)
        toolbar.addWidget(self.lbl_total)
        toolbar.addWidget(self.btn_next)
        toolbar.addStretch()
        toolbar.addWidget(self.btn_bookmark)

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
            QListWidget::item {{ padding: 6px; border-bottom: 1px solid {BRAND_BORDER}; }}
            QListWidget::item:selected {{ background: {get_brand_accent()}; color: {BRAND_BACKGROUND}; font-weight: bold; }}
        """)
        self.slide_list.currentRowChanged.connect(self._on_sidebar_click)

        # ── Search Bar ──────────────────────────────────────────────
        self.search_container = QWidget()
        self.search_container.setStyleSheet(f"background: {BRAND_PANEL_2}; border-bottom: 1px solid {BRAND_BORDER};")
        search_layout = QHBoxLayout(self.search_container)
        search_layout.setContentsMargins(10, 4, 10, 4)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Find in presentation (Ctrl+F)...")
        self.search_input.setStyleSheet(f"background: {BRAND_PANEL}; color: {BRAND_PRIMARY}; border: 1px solid {BRAND_BORDER}; border-radius: 4px; padding: 4px;")
        self.search_input.returnPressed.connect(self._perform_search)
        self.btn_search_next = QToolButton()
        self.btn_search_next.setIcon(icon("chevron-down", size=14))
        self.btn_search_next.clicked.connect(self._perform_search)
        search_layout.addWidget(QLabel("Search:"))
        search_layout.addWidget(self.search_input, stretch=1)
        search_layout.addWidget(self.btn_search_next)
        self.search_container.hide()

        self.viewer = QTextBrowser()
        # Enable continuous elastic scaling (no fixed px sizes)
        self.viewer.setStyleSheet(f"""
            QTextBrowser {{
                background: {BRAND_BACKGROUND};
                color: {BRAND_PRIMARY};
                border: none;
                padding: 0px;
                font-family: 'Segoe UI', sans-serif;
            }}
        """)
        self.viewer.setOpenExternalLinks(True)
        # Sync scrolling back to sidebar
        self.viewer.verticalScrollBar().valueChanged.connect(self._on_scroll)
        self._is_jumping = False # prevent circular sync

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        right_layout.addWidget(self.search_container)
        right_layout.addWidget(self.viewer)

        self.splitter.addWidget(self.slide_list)
        self.splitter.addWidget(right_panel)

        layout.addLayout(toolbar)
        layout.addWidget(self.splitter)
        
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(self._show_search)
        
        QShortcut(QKeySequence(Qt.Key_Left), self, context=Qt.WidgetWithChildrenShortcut).activated.connect(self.prev_slide)
        QShortcut(QKeySequence(Qt.Key_Right), self, context=Qt.WidgetWithChildrenShortcut).activated.connect(self.next_slide)

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
                        elif getattr(shape, "shape_type", None) == 13:
                            # MSO_SHAPE_TYPE.PICTURE == 13
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
            self._render_continuous_html()
            self.go_to_slide(0)

    def _fallback_zip_parse(self, file_path):
        """Fallback parser extracting slide text XML from pptx zip container."""
        try:
            with zipfile.ZipFile(file_path, "r") as z:
                slide_files = [name for name in z.namelist() if name.startswith("ppt/slides/slide") and name.endswith(".xml")]
                # Sort numerically by extracting the integer from "ppt/slides/slideX.xml" to prevent slide10 from coming after slide1
                slide_files.sort(key=lambda x: int(x.split("slide")[-1].split(".xml")[0]))
                for idx, sfile in enumerate(slide_files, start=1):
                    xml_content = z.read(sfile)
                    tree = ET.fromstring(xml_content)
                    texts = []
                    for elem in tree.iter():
                        if elem.tag.endswith("}t") and elem.text:
                            t = elem.text.strip()
                            if t:
                                texts.append(t)
                                
                    # Ponytail native image extraction: grab from .rels mapping
                    import base64
                    parts = sfile.split("/")
                    rels_path = "/".join(parts[:-1]) + "/_rels/" + parts[-1] + ".rels"
                    if rels_path in z.namelist():
                        rels_tree = ET.fromstring(z.read(rels_path))
                        for rel in rels_tree.iter():
                            if rel.tag.endswith("}Relationship"):
                                target = rel.attrib.get("Target", "")
                                if target.startswith("../media/"):
                                    media_path = "ppt/media/" + target.split("/")[-1]
                                    if media_path in z.namelist():
                                        img_bytes = z.read(media_path)
                                        b64_data = base64.b64encode(img_bytes).decode("utf-8")
                                        ext = media_path.split(".")[-1].lower()
                                        mime = "image/jpeg" if ext == "jpg" else f"image/{ext}"
                                        texts.append(f'<img src="data:{mime};base64,{b64_data}" style="max-width:100%; border-radius:4px; margin-top:10px; margin-bottom:10px;" />')
                    title = f"Slide {idx}"
                    if texts:
                        # Find the first text element that isn't an img tag
                        for t in texts:
                            if not t.startswith("<img"):
                                title = t
                                break
                    self.slides.append({
                        "title": title,
                        "content": "\n\n".join(texts),
                        "notes": "",
                    })
        except Exception as e:
            print(f"[PPTX Viewer] Fallback zip parse error: {e}")

    def set_bookmark_callback(self, callback):
        self._bookmark_callback = callback

    def _bookmark_payload(self):
        name = os.path.basename(self.file_path) if self.file_path else "presentation"
        return {
            "page_number": self.current_slide,
            "scroll_position_y": 0.0,
            "label": f"Slide {self.current_slide + 1} in {name}",
        }

    def _add_bookmark_here(self):
        if self._bookmark_callback:
            self._bookmark_callback(self._bookmark_payload())

    def go_to_bookmark(self, page_number=0, scroll_position_y=0.0):
        self.go_to_slide(int(page_number))

    def _show_search(self):
        self.search_container.show()
        self.search_input.setFocus()
        self.search_input.selectAll()

    def _perform_search(self):
        query = self.search_input.text()
        if query:
            # find() natively scrolls to and highlights the next match
            if not self.viewer.find(query):
                # loop back to top
                self.viewer.moveCursor(self.viewer.textCursor().Start)
                self.viewer.find(query)

    def _render_continuous_html(self):
        accent = get_brand_accent()
        html = f"<div style='background: {BRAND_BACKGROUND}; padding-bottom: 40px;'>"
        
        for index, slide_data in enumerate(self.slides):
            raw_content = slide_data['content'] or ''
            content_html = raw_content.replace('\n', '<br>') if raw_content else '<i>(No text content on this slide)</i>'
            
            # Use anchor for scrolling
            html += f"<a name='slide_{index}'></a>"
            html += f"""
            <div style="max-width: 800px; margin: 30px auto; padding: 40px; background: {BRAND_PANEL}; border: 1px solid {BRAND_BORDER}; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
                <div style="color: {accent}; font-size: 0.8em; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;">
                    SLIDE {index + 1} OF {self.total_slides}
                </div>
                <h1 style="color: {BRAND_PRIMARY}; font-size: 1.5em; margin-top: 0; margin-bottom: 20px; border-bottom: 1px solid {BRAND_BORDER}; padding-bottom: 10px;">
                    {slide_data['title']}
                </h1>
                <div style="font-size: 1.1em; line-height: 1.7; color: {BRAND_PRIMARY};">
                    {content_html}
                </div>
            """
            
            if slide_data.get("notes"):
                html += f"""
                <div style="margin-top: 30px; padding: 12px; background: {BRAND_PANEL_2}; border-left: 3px solid {accent}; border-radius: 4px;">
                    <div style="color: {BRAND_MUTED_FG}; font-size: 0.8em; font-weight: bold; margin-bottom: 4px;">SPEAKER NOTES</div>
                    <div style="font-size: 0.9em; color: {BRAND_MUTED_FG};">{slide_data['notes']}</div>
                </div>
                """
            html += "</div>"
            
        html += "</div>"
        self.viewer.setHtml(html)

    def _on_sidebar_click(self, index):
        if not self._is_jumping:
            self.go_to_slide(index)

    def _on_scroll(self, value):
        if self._is_jumping or self.total_slides == 0:
            return
            
        # Estimate which slide is currently in view based on scroll bar percentage
        scrollbar = self.viewer.verticalScrollBar()
        max_val = scrollbar.maximum()
        if max_val <= 0:
            return
            
        percentage = value / max_val
        # Add slight offset so it switches earlier
        estimated_index = min(self.total_slides - 1, int(percentage * self.total_slides + 0.1))
        
        if estimated_index != self.current_slide:
            self.current_slide = estimated_index
            self.slide_input.setText(str(estimated_index + 1))
            
            # Update list without triggering currentRowChanged
            self.slide_list.blockSignals(True)
            self.slide_list.setCurrentRow(estimated_index)
            self.slide_list.blockSignals(False)

    def go_to_slide(self, index):
        if index < 0 or index >= self.total_slides:
            return
            
        self._is_jumping = True
        self.current_slide = index
        self.slide_input.setText(str(index + 1))
        
        self.slide_list.blockSignals(True)
        self.slide_list.setCurrentRow(index)
        self.slide_list.blockSignals(False)

        self.viewer.scrollToAnchor(f"slide_{index}")
        
        # Debounce the jump lock
        import PySide6.QtCore
        PySide6.QtCore.QTimer.singleShot(100, lambda: setattr(self, '_is_jumping', False))

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
        """Return text of current slide for TTS. Playback handled by MainWindow."""
        if 0 <= self.current_slide < self.total_slides:
            slide_data = self.slides[self.current_slide]
            text = f"{slide_data['title']}. {slide_data['content']}"
            return text.strip() if text.strip() else ""
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
