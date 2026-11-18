"""PDF viewer using Qt's native QPdfView for vector-crisp rendering.

Display layer: QPdfDocument + QPdfView (PDFium-based, always sharp text).
Background:    PyMuPDF (fitz) kept only for TTS text extraction and TOC scanning.
"""

import json
import os
import re

try:
    from PySide6.QtPdf import QPdfDocument, QPdfBookmarkModel, QPdfSearchModel
    from PySide6.QtPdfWidgets import QPdfView
    QTPDF_AVAILABLE = True
except ImportError:
    QTPDF_AVAILABLE = False

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QToolButton, QLabel,
    QMessageBox, QComboBox, QMenu, QLineEdit, QTreeView,
    QSplitter, QColorDialog
)
from PySide6.QtGui import QIntValidator, QKeyEvent, QWheelEvent, QShortcut, QKeySequence, QColor, QPainter, QPen, QBrush, QMouseEvent
from PySide6.QtCore import Qt, Signal, QTimer, QSize, QPointF, QThread, QEvent, QObject, QRectF

class PdfTextWorker(QThread):
    """Off-thread PDF text extraction worker to prevent GUI freezes during TTS and page scans."""
    extracted = Signal(int, str)

    def __init__(self, pdf_doc, page_idx):
        super().__init__()
        self.pdf_doc = pdf_doc
        self.page_idx = page_idx

    def run(self):
        try:
            selection = self.pdf_doc.getAllText(self.page_idx)
            text = selection.text().strip() if hasattr(selection, "text") else ""
            self.extracted.emit(self.page_idx, text)
        except Exception:
            self.extracted.emit(self.page_idx, "")

from icons import icon
from tts_engine import TtsEngine as PdfTts, TTS_AVAILABLE
from settings import load_settings, save_settings
from theme import (
    get_active_palette,
    compact_toolbar_stylesheet, ICON_SIZE_COMPACT
)
from paths import APP_DATA_DIR

_PDF_DOCUMENT_CACHE = {}
_PDF_DOCUMENT_CACHE_MAX_ENTRIES = 8

# ── Custom QPdfView with Ctrl+Wheel zoom and key navigation ─────────

if QTPDF_AVAILABLE:
    class EleViewerPdfView(QPdfView):
        """QPdfView subclass adding Ctrl+Wheel zoom and arrow-key page changes."""
        page_change = Signal(int)       # -1 for prev, +1 for next
        bookmark_requested = Signal()
        search_requested = Signal()

        def wheelEvent(self, event: QWheelEvent):
            if event.modifiers() & Qt.ControlModifier:
                delta = event.angleDelta().y()
                factor = 1.15 if delta > 0 else 1 / 1.15
                self.setZoomMode(QPdfView.ZoomMode.Custom)
                self.setZoomFactor(self.zoomFactor() * factor)
                event.accept()
                return
            super().wheelEvent(event)

        def keyPressEvent(self, event: QKeyEvent):
            key = event.key()
            # In single-page mode, arrow keys change pages
            if self.pageMode() == QPdfView.PageMode.SinglePage:
                if key in (Qt.Key_Left, Qt.Key_PageUp):
                    self.page_change.emit(-1)
                    event.accept()
                    return
                elif key in (Qt.Key_Right, Qt.Key_PageDown):
                    self.page_change.emit(1)
                    event.accept()
                    return
            # Ctrl+D bookmark shortcut works in any mode
            if event.modifiers() & Qt.ControlModifier and key == Qt.Key_D:
                self.bookmark_requested.emit()
                event.accept()
                return
            if event.modifiers() & Qt.ControlModifier and key == Qt.Key_F:
                self.search_requested.emit()
                event.accept()
                return
            super().keyPressEvent(event)

        def resizeEvent(self, event):
            super().resizeEvent(event)
            if hasattr(self, "overlay_label") and self.overlay_label and self.overlay_label.isVisible():
                padding = 20
                self.overlay_label.adjustSize()
                lbl_w = self.overlay_label.width()
                lbl_h = self.overlay_label.height()
                self.overlay_label.move(
                    self.width() - lbl_w - padding,
                    self.height() - lbl_h - padding
                )


class SearchInputFilter(QObject):
    def __init__(self, on_escape, parent=None):
        super().__init__(parent)
        self.on_escape = on_escape

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Escape:
            self.on_escape()
            return True
        return super().eventFilter(obj, event)


# ── Annotation overlay widget ──────────────────────────────────────────

class AnnotationOverlay(QWidget):
    """Transparent overlay on top of QPdfView for drawing annotations."""

    annotation_created = Signal(dict)
    annotation_removed = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self._annotations = []
        self._drawing = False
        self._start_pos = None
        self._current_tool = "none"
        self._current_color = QColor(255, 255, 0, 120)
        self._current_rect = None

    def set_annotations(self, annotations):
        self._annotations = annotations
        self.update()

    def set_tool(self, tool):
        self._current_tool = tool
        self._drawing = False
        self._start_pos = None
        self._current_rect = None
        self.update()

    def set_color(self, color):
        self._current_color = color

    def annotations(self):
        return self._annotations

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        for ann in self._annotations:
            rect = QRectF(ann["rect"][0], ann["rect"][1], ann["rect"][2], ann["rect"][3])
            color = QColor(ann["color"][0], ann["color"][1], ann["color"][2], ann["color"][3])
            if ann["type"] == "highlight":
                painter.fillRect(rect, color)
            elif ann["type"] == "note":
                painter.fillRect(rect, QColor(255, 255, 0, 60))
                painter.setPen(QPen(QColor(255, 200, 0), 1))
                painter.drawRect(rect)
            elif ann["type"] == "pen":
                painter.setPen(QPen(QColor(ann["color"][0], ann["color"][1], ann["color"][2]), 2))
                painter.drawRect(rect)
        if self._current_rect and self._current_tool != "none":
            rect = QRectF(self._current_rect)
            painter.fillRect(rect, self._current_color)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton and self._current_tool != "none":
            self._drawing = True
            self._start_pos = event.pos()
            self._current_rect = [event.pos().x(), event.pos().y(), 0, 0]
            self.update()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._drawing and self._start_pos:
            self._current_rect = [
                self._start_pos.x(),
                self._start_pos.y(),
                event.pos().x() - self._start_pos.x(),
                event.pos().y() - self._start_pos.y(),
            ]
            self.update()
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton and self._drawing:
            self._drawing = False
            rect = self._current_rect
            self._current_rect = None
            page = self._current_page()
            ann = {
                "page": page,
                "rect": rect,
                "color": [self._current_color.red(), self._current_color.green(), self._current_color.blue(), self._current_color.alpha()],
                "type": self._current_tool,
                "text": "",
            }
            self._annotations.append(ann)
            self.annotation_created.emit(ann)
            self.update()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def _current_page(self):
        viewer = self.parentWidget()
        if hasattr(viewer, "current_page"):
            return viewer.current_page
        return 0

    def clear_annotations(self):
        self._annotations = []
        self.update()

    def remove_annotation(self, index):
        if 0 <= index < len(self._annotations):
            self._annotations.pop(index)
            self.annotation_removed.emit(index)
            self.update()


# ── Main PDF Viewer widget ───────────────────────────────────────────

class PdfViewer(QWidget):
    textChanged = Signal()

    def __init__(self, file_path=None, status_callback=None):
        super().__init__()
        self.file_path = file_path
        self.is_modified = False
        self._status_callback = status_callback
        self._bookmark_callback = None
        self.current_page = 0
        self.total_pages = 0
        self._toc_visible = load_settings().get("pdf_toc_visible", False)
        self._search_visible = False
        self.search_model = None
        self._multi_page = True
        self.tts = PdfTts(on_error=self._on_tts_error)
        # ── Annotation state ─────────────────────────────────────────
        self._annotations = []           # list of dicts: {page, rect, color, type, text}
        self._annot_tool = "none"        # "none" | "highlight" | "note" | "pen" | "erase"
        self._annot_color = QColor(255, 255, 0, 120)  # semi-transparent yellow
        self._annot_drawing = False
        self._annot_start_pos = None
        self._overlay = None             # AnnotationOverlay widget
        self._annot_colors = {
            "yellow": QColor(255, 255, 0, 120),
            "green": QColor(0, 255, 0, 120),
            "pink": QColor(255, 192, 203, 120),
        }

        self.setFocusPolicy(Qt.StrongFocus)

        # ── Outer layout ────────────────────────────────────────────
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

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

        self.btn_toc      = _tb("list",         "Table of Contents", self._toggle_toc, "Contents")
        self.btn_search   = _tb("search",       "Find in document (Ctrl+F)", self._toggle_search, "Find")
        self.btn_prev     = _tb("chevron-left",  "Previous page",           self.prev_page)
        self.btn_next     = _tb("chevron-right", "Next page",               self.next_page)

        # Page input  ─ editable box + "/ N" label
        p = get_active_palette()
        self.page_input = QLineEdit()
        self.page_input.setFixedWidth(44)
        self.page_input.setAlignment(Qt.AlignCenter)
        self.page_input.setValidator(QIntValidator(1, 99999))
        self.page_input.setStyleSheet(
            f"QLineEdit {{ background:{p['BRAND_PANEL_2']}; color:{p['BRAND_PRIMARY']}; border:1px solid {p['BRAND_BORDER']};"
            " border-radius:4px; padding:2px 4px; font-weight:bold; font-size:12px; }"
        )
        self.page_input.returnPressed.connect(self._jump_to_page)
        self.lbl_total = QLabel(" / 0")
        self.lbl_total.setStyleSheet(f"color:{p['BRAND_MUTED_FG']}; font-weight:bold; padding:0 6px 0 2px; font-size:12px;")

        self.btn_zoom_out  = _tb("zoom-out",   "Zoom out",                lambda: self._apply_zoom(1 / 1.2))
        self.btn_fit_page  = _tb("minimize-2",   "Fit to page",             self.fit_page)
        self.btn_fit_width = _tb("maximize-2",    "Fit to width",            self.fit_to_width)
        self.btn_zoom_in   = _tb("zoom-in",    "Zoom in",                 lambda: self._apply_zoom(1.2))
        self.btn_multi     = _tb("columns-2",    "Two-page view",           self._toggle_multi_page)
        self.btn_bookmark  = _tb("bookmark",   "Bookmark this page",      self._add_bookmark_here, "Bookmark")

        toolbar.addWidget(self.btn_toc)
        toolbar.addWidget(self.btn_search)
        toolbar.addSpacing(8)
        toolbar.addWidget(self.btn_prev)
        toolbar.addWidget(self.page_input)
        toolbar.addWidget(self.lbl_total)
        toolbar.addWidget(self.btn_next)
        toolbar.addStretch()
        toolbar.addWidget(self.btn_zoom_out)
        toolbar.addWidget(self.btn_fit_page)
        toolbar.addWidget(self.btn_fit_width)
        toolbar.addWidget(self.btn_zoom_in)
        toolbar.addSpacing(8)
        toolbar.addWidget(self.btn_multi)
        toolbar.addWidget(self.btn_bookmark)

        # ── Annotation tools ─────────────────────────────────────────
        self.btn_annot_highlight = _tb("maximize-2", "Highlight tool", self._set_annot_highlight)
        self.btn_annot_highlight.setCheckable(True)
        self.btn_annot_note = _tb("message-square", "Sticky note", self._set_annot_note)
        self.btn_annot_note.setCheckable(True)
        self.btn_annot_pen = _tb("pencil", "Freehand pen", self._set_annot_pen)
        self.btn_annot_pen.setCheckable(True)
        self.btn_annot_erase = _tb("x", "Clear annotations", self._clear_annotations)

        self.btn_annot_color = QToolButton()
        self.btn_annot_color.setIconSize(icon_qsize)
        self.btn_annot_color.setIcon(icon("palette", size=icon_sz) if False else icon("circle-help", size=icon_sz))
        self.btn_annot_color.setToolTip("Highlight color")
        self.btn_annot_color.setPopupMode(QToolButton.InstantPopup)
        color_menu = QMenu(self.btn_annot_color)
        for name, color in self._annot_colors.items():
            action = color_menu.addAction(name.title())
            action.setData(name)
            action.triggered.connect(lambda checked=False, n=name: self._set_annot_color(n))
        self.btn_annot_color.setMenu(color_menu)
        self.btn_annot_color.setStyleSheet(compact_toolbar_stylesheet())
        self.btn_annot_color.setAutoRaise(True)

        toolbar.addWidget(self.btn_annot_highlight)
        toolbar.addWidget(self.btn_annot_note)
        toolbar.addWidget(self.btn_annot_pen)
        toolbar.addWidget(self.btn_annot_color)
        toolbar.addWidget(self.btn_annot_erase)

        # ── Accessibility: accessible names for PDF toolbar buttons ───
        self.btn_toc.setAccessibleName("Table of Contents")
        self.btn_toc.setAccessibleDescription("Show or hide the document outline sidebar (Ctrl+Shift+L)")
        self.btn_search.setAccessibleName("Find in Document")
        self.btn_search.setAccessibleDescription("Search for text in the PDF (Ctrl+F)")
        self.btn_prev.setAccessibleName("Previous Page")
        self.btn_next.setAccessibleName("Next Page")
        self.btn_zoom_out.setAccessibleName("Zoom Out")
        self.btn_fit_page.setAccessibleName("Fit to Page")
        self.btn_fit_width.setAccessibleName("Fit to Width")
        self.btn_zoom_in.setAccessibleName("Zoom In")
        self.btn_multi.setAccessibleName("Two-Page View")
        self.btn_bookmark.setAccessibleName("Bookmark This Page")
        self.btn_annot_highlight.setAccessibleName("Highlight Tool")
        self.btn_annot_note.setAccessibleName("Sticky Note Tool")
        self.btn_annot_pen.setAccessibleName("Freehand Pen Tool")
        self.btn_annot_erase.setAccessibleName("Clear Annotations")
        self.btn_annot_color.setAccessibleName("Highlight Color")
        self.page_input.setAccessibleName("Page Number Input")
        self.page_input.setAccessibleDescription("Enter a page number to jump to")

        # ── Search Bar ──────────────────────────────────────────────
        self.search_bar_widget = QWidget()
        self.search_bar_widget.setStyleSheet(
            f"QWidget {{ background: {p['BRAND_PANEL_2']}; border-bottom: 1px solid {p['BRAND_BORDER']}; }}"
        )
        search_layout = QHBoxLayout(self.search_bar_widget)
        search_layout.setContentsMargins(8, 4, 8, 4)
        search_layout.setSpacing(6)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Find in document...")
        self.search_input.setStyleSheet(
            f"QLineEdit {{ background:{p['BRAND_PANEL']}; color:{p['BRAND_PRIMARY']}; border:1px solid {p['BRAND_BORDER']};"
            " border-radius:4px; padding:3px 6px; font-size:12px; min-width: 180px; }"
        )
        self.search_input.setAccessibleName("Find in Document Search Box")
        self.search_input.setAccessibleDescription("Type text to search in the PDF document")
        self.search_input.textChanged.connect(self._on_search_text_changed)
        self.search_input.returnPressed.connect(self._find_next_result)
        self._esc_filter = SearchInputFilter(self._hide_search, self)
        self.search_input.installEventFilter(self._esc_filter)

        self.lbl_search_count = QLabel("")
        self.lbl_search_count.setStyleSheet(f"color:{p['BRAND_MUTED_FG']}; font-size:11px; padding:0 4px;")

        self.btn_search_prev = _tb("chevron-up", "Previous match (Shift+Enter)", self._find_prev_result)
        self.btn_search_next = _tb("chevron-down", "Next match (Enter)", self._find_next_result)
        self.btn_search_close = _tb("x", "Close search (Esc)", self._hide_search)

        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.lbl_search_count)
        search_layout.addWidget(self.btn_search_prev)
        search_layout.addWidget(self.btn_search_next)
        search_layout.addStretch()
        search_layout.addWidget(self.btn_search_close)
        self.search_bar_widget.hide()

        # ── Content area: TOC splitter + QPdfView ───────────────────
        self.content_splitter = QSplitter(Qt.Horizontal)

        # TOC panel
        self.toc_widget = QWidget()
        toc_layout = QVBoxLayout(self.toc_widget)
        toc_layout.setContentsMargins(0, 0, 0, 0)
        toc_layout.setSpacing(0)
        toc_lbl = QLabel("Table of Contents")
        toc_lbl.setStyleSheet(
            f"background:{p['BRAND_BACKGROUND']}; color:{p['BRAND_MUTED_FG']}; font-size:11px; font-weight:bold;"
            f" padding:6px 8px; border-bottom:1px solid {p['BRAND_BORDER']};"
        )
        self.toc_tree = QTreeView()
        self.toc_tree.setHeaderHidden(True)
        self.bookmark_model = None
        self.toc_tree.setStyleSheet(
            f"QTreeView {{ background:{p['BRAND_PANEL']}; border:none; color:{p['BRAND_PRIMARY']}; font-size:12px; }}"
            "QTreeView::item { padding:4px 6px; }"
            f"QTreeView::item:selected {{ background:{p['BRAND_PANEL_2']}; }}"
            f"QTreeView::item:hover {{ background:{p['BRAND_BORDER']}; }}"
        )
        self.toc_tree.clicked.connect(self._on_toc_item_clicked)
        toc_layout.addWidget(toc_lbl)
        toc_layout.addWidget(self.toc_tree)
        self.toc_widget.setMinimumWidth(160)
        self.toc_widget.setMaximumWidth(300)
        self.toc_widget.hide()

        # QPdfView — vector-rendered PDF display
        if QTPDF_AVAILABLE:
            self.pdf_doc_qt = QPdfDocument(self)
            self.bookmark_model = QPdfBookmarkModel(self)
            self.bookmark_model.setDocument(self.pdf_doc_qt)
            self.toc_tree.setModel(self.bookmark_model)
            
            self.pdf_view = EleViewerPdfView(self)
            self.pdf_view.setDocument(self.pdf_doc_qt)
            self.pdf_view.setPageMode(QPdfView.PageMode.MultiPage)
            self.pdf_view.setZoomMode(QPdfView.ZoomMode.FitToWidth)
            self.pdf_view.setStyleSheet(f"background: {p['BRAND_BACKGROUND']}; border: none;")
            self.pdf_view.setContextMenuPolicy(Qt.CustomContextMenu)
            self.pdf_view.customContextMenuRequested.connect(self._show_context_menu)
            # Create overlay label
            self.pdf_view.overlay_label = QLabel(self.pdf_view)
            self.pdf_view.overlay_label.setStyleSheet(
                "background-color: rgba(30, 30, 30, 0.85); color: #e0e0e0; "
                "border: 1px solid #555; border-radius: 4px; padding: 4px 8px; "
                "font-size: 12px; font-weight: bold;"
            )
            self.pdf_view.overlay_label.setText("")
            self.pdf_view.overlay_label.hide()
            # Search model
            self.search_model = QPdfSearchModel(self)
            self.search_model.setDocument(self.pdf_doc_qt)
            self.search_model.countChanged.connect(self._on_search_count_changed)
            self.pdf_view.setSearchModel(self.search_model)
            self.pdf_view.currentSearchResultIndexChanged.connect(self._on_search_index_changed)
            self.pdf_view.search_requested.connect(self._toggle_search)
            # Wire signals
            self.pdf_view.pageNavigator().currentPageChanged.connect(self._on_page_changed)
            self.pdf_view.page_change.connect(self._on_page_change_key)
            self.pdf_view.bookmark_requested.connect(self._add_bookmark_here)
        else:
            self.pdf_doc_qt = None
            self.pdf_view = QLabel("QPdfView not available.\nPlease install PySide6 >= 6.6")
            self.pdf_view.setAlignment(Qt.AlignCenter)
            self.pdf_view.setStyleSheet("color: #e0e0e0; background: #1e1e1e; font-size: 14px;")

        self.content_splitter.addWidget(self.toc_widget)
        self.content_splitter.addWidget(self.pdf_view)

        # ── Annotation overlay (sits on top of QPdfView) ─────────────
        if QTPDF_AVAILABLE:
            self._overlay = AnnotationOverlay(self.pdf_view)
            self._overlay.setGeometry(self.pdf_view.rect())
            self._overlay.annotation_created.connect(self._on_annotation_created)
            self._overlay.setVisible(False)
            self.pdf_view.resizeEvent = self._on_pdf_resize

        QShortcut(QKeySequence(Qt.Key_Left), self, context=Qt.WidgetWithChildrenShortcut).activated.connect(self.prev_page)
        QShortcut(QKeySequence(Qt.Key_Right), self, context=Qt.WidgetWithChildrenShortcut).activated.connect(self.next_page)
        QShortcut(QKeySequence("Ctrl+F"), self, context=Qt.WidgetWithChildrenShortcut).activated.connect(self._toggle_search)

        outer.addLayout(toolbar)
        outer.addWidget(self.search_bar_widget)
        outer.addWidget(self.content_splitter)

        # Apply initial TOC visibility from settings
        if self._toc_visible:
            self.toc_widget.setVisible(True)
            total = self.content_splitter.width()
            self.content_splitter.setSizes([220, max(total - 220, 300)])
        else:
            self.toc_widget.setVisible(False)
            self.content_splitter.setSizes([0, self.content_splitter.width()])

        # Keyboard shortcut for TOC: Ctrl+Shift+O
        QShortcut(QKeySequence("Ctrl+Shift+O"), self, context=Qt.WidgetWithChildrenShortcut).activated.connect(self._toggle_toc)

        if file_path:
            self.load_from_path(file_path)

    # ── Status / bookmark callbacks ──────────────────────────────────

    def set_status_callback(self, callback):
        self._status_callback = callback

    def set_bookmark_callback(self, callback):
        self._bookmark_callback = callback

    def _on_tts_error(self, message):
        if self._status_callback:
            self._status_callback(f"TTS error: {message}", 4000)

    # ── Voice population ─────────────────────────────────────────────

    def _populate_voices(self):
        self.voice_combo.clear()
        if not TTS_AVAILABLE:
            self.voice_combo.addItem("(TTS unavailable)", "")
            self.btn_speak.setEnabled(False)
            return
        voices = self.tts.list_voices()
        if not voices:
            self.voice_combo.addItem("(Loading voices...)", "")
            QTimer.singleShot(500, self._populate_voices)
            return
        for voice_id, name in voices:
            self.voice_combo.addItem(name, voice_id)

    # ── Load ─────────────────────────────────────────────────────────

    def _get_render_cache_key(self, file_path):
        if not file_path or not os.path.exists(file_path):
            return None
        try:
            return (file_path, os.path.getmtime(file_path), os.path.getsize(file_path))
        except OSError:
            return None

    def load_from_path(self, file_path):
        if not QTPDF_AVAILABLE:
            QMessageBox.critical(
                self, "Missing Dependency",
                "PySide6 QtPdf module is required.\nPlease update PySide6 to 6.6+.",
            )
            return
        try:
            cache_key = self._get_render_cache_key(file_path)
            if cache_key is not None and cache_key in _PDF_DOCUMENT_CACHE:
                self.pdf_doc_qt = _PDF_DOCUMENT_CACHE[cache_key]
            else:
                self.pdf_doc_qt = QPdfDocument(self)
                self.pdf_doc_qt.load(file_path)
                if cache_key is not None:
                    if len(_PDF_DOCUMENT_CACHE) >= _PDF_DOCUMENT_CACHE_MAX_ENTRIES:
                        _PDF_DOCUMENT_CACHE.pop(next(iter(_PDF_DOCUMENT_CACHE)))
                    _PDF_DOCUMENT_CACHE[cache_key] = self.pdf_doc_qt

            self.bookmark_model.setDocument(self.pdf_doc_qt)
            self.pdf_view.setDocument(self.pdf_doc_qt)
            if self.search_model:
                self.search_model.setDocument(self.pdf_doc_qt)
                self.pdf_view.setSearchModel(self.search_model)
                if self._search_visible and self.search_input.text():
                    self.search_model.setSearchString(self.search_input.text().strip())
            self.total_pages = self.pdf_doc_qt.pageCount()
            self.current_page = 0
            self.lbl_total.setText(f" / {self.total_pages}")
            self.page_input.setValidator(QIntValidator(1, max(self.total_pages, 1)))
            self.page_input.setText("1")

            # Apply default fit mode from settings
            settings = load_settings()
            fit = settings.get("pdf_fit_mode", "width")
            if fit == "page":
                self.pdf_view.setZoomMode(QPdfView.ZoomMode.FitInView)
            else:
                self.pdf_view.setZoomMode(QPdfView.ZoomMode.FitToWidth)

            if hasattr(self.pdf_view, "overlay_label") and self.pdf_view.overlay_label:
                self.pdf_view.overlay_label.setText(f"1 / {self.total_pages}")
                self.pdf_view.overlay_label.show()
                self.pdf_view.overlay_label.adjustSize()
                padding = 20
                lbl_w = self.pdf_view.overlay_label.width()
                lbl_h = self.pdf_view.overlay_label.height()
                self.pdf_view.overlay_label.move(
                    self.pdf_view.width() - lbl_w - padding,
                    self.pdf_view.height() - lbl_h - padding
                )

            self.is_modified = False
            self.toc_tree.expandAll()
            self._load_annotations()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load PDF: {str(e)}")

    # ── Page change tracking ─────────────────────────────────────────

    def _on_page_changed(self, page):
        """Called by QPdfView's pageNavigator when the visible page changes."""
        self.current_page = page
        self.page_input.setText(str(page + 1))
        if hasattr(self.pdf_view, "overlay_label") and self.pdf_view.overlay_label:
            self.pdf_view.overlay_label.setText(f"{page + 1} / {self.total_pages}")
            self.pdf_view.overlay_label.adjustSize()
            padding = 20
            lbl_w = self.pdf_view.overlay_label.width()
            lbl_h = self.pdf_view.overlay_label.height()
            self.pdf_view.overlay_label.move(
                self.pdf_view.width() - lbl_w - padding,
                self.pdf_view.height() - lbl_h - padding
            )
        self._prefetch_page_text(page)

    def _prefetch_page_text(self, page):
        if not hasattr(self, "_page_text_cache"):
            self._page_text_cache = {}
        if not hasattr(self, "_active_workers"):
            self._active_workers = set()
        for p in (page, page + 1, page - 1):
            if 0 <= p < self.total_pages and p not in self._page_text_cache:
                if any(getattr(w, "page_idx", None) == p for w in self._active_workers):
                    continue
                worker = PdfTextWorker(self.pdf_doc_qt, p)
                self._active_workers.add(worker)

                def _on_extracted(idx, txt, w=worker):
                    self._page_text_cache[idx] = txt
                    self._active_workers.discard(w)

                worker.extracted.connect(_on_extracted)
                worker.finished.connect(worker.deleteLater)
                worker.start()

    def _on_page_change_key(self, delta):
        """Called by EleViewerPdfView arrow key signals (-1 or +1)."""
        if delta < 0:
            self.prev_page()
        else:
            self.next_page()

    def _on_toc_item_clicked(self, index):
        if self.bookmark_model:
            page = self.bookmark_model.data(index, QPdfBookmarkModel.Role.Page)
            if page is not None and page >= 0:
                self.go_to_bookmark(page_number=page)

    def _toggle_toc(self):
        self._toc_visible = not self._toc_visible
        self.toc_widget.setVisible(self._toc_visible)
        if self._toc_visible:
            total = self.content_splitter.width()
            self.content_splitter.setSizes([220, max(total - 220, 300)])
        else:
            self.content_splitter.setSizes([0, self.content_splitter.width()])
        # Persist TOC visibility
        s = load_settings()
        s["pdf_toc_visible"] = self._toc_visible
        save_settings(s)

    # ── Page jump ────────────────────────────────────────────────────

    def _jump_to_page(self):
        try:
            pg = int(self.page_input.text())
        except ValueError:
            return
        pg = max(1, min(pg, self.total_pages))
        self.go_to_bookmark(page_number=pg - 1)

    # ── Fit / zoom ───────────────────────────────────────────────────

    def fit_page(self):
        if QTPDF_AVAILABLE:
            self.pdf_view.setZoomMode(QPdfView.ZoomMode.FitInView)

    def fit_to_width(self):
        if QTPDF_AVAILABLE:
            self.pdf_view.setZoomMode(QPdfView.ZoomMode.FitToWidth)

    def _apply_zoom(self, factor):
        if not QTPDF_AVAILABLE:
            return
        self.pdf_view.setZoomMode(QPdfView.ZoomMode.Custom)
        current = self.pdf_view.zoomFactor()
        self.pdf_view.setZoomFactor(current * factor)

    # ── Multi-page toggle ────────────────────────────────────────────

    def _toggle_multi_page(self):
        if not QTPDF_AVAILABLE:
            return
        self._multi_page = not self._multi_page
        if self._multi_page:
            self.pdf_view.setPageMode(QPdfView.PageMode.MultiPage)
        else:
            self.pdf_view.setPageMode(QPdfView.PageMode.SinglePage)
        style = " QToolButton { background:#3c3c3c; font-size: 11px; padding: 2px 6px; }" if self._multi_page else " QToolButton { font-size: 11px; padding: 2px 6px; }"
        self.btn_multi.setStyleSheet(compact_toolbar_stylesheet() + style)

    # ── Navigation ───────────────────────────────────────────────────

    def prev_page(self):
        if not QTPDF_AVAILABLE or self.total_pages <= 0:
            return
        nav = self.pdf_view.pageNavigator()
        cur = nav.currentPage()
        self.tts.stop()
        if cur > 0:
            nav.jump(cur - 1, QPointF(), 0)
        else:
            nav.jump(self.total_pages - 1, QPointF(), 0)

    def next_page(self):
        if not QTPDF_AVAILABLE or self.total_pages <= 0:
            return
        nav = self.pdf_view.pageNavigator()
        cur = nav.currentPage()
        self.tts.stop()
        if cur < self.total_pages - 1:
            nav.jump(cur + 1, QPointF(), 0)
        else:
            nav.jump(0, QPointF(), 0)

    def go_to_bookmark(self, page_number=0, scroll_position_y=0.0):
        if not QTPDF_AVAILABLE or not self.pdf_doc_qt:
            return
        page_number = max(0, min(int(page_number), self.total_pages - 1))
        self.tts.stop()
        self.pdf_view.pageNavigator().jump(page_number, QPointF(), 0)

    def keyPressEvent(self, event: QKeyEvent):
        """Catch key events when the PdfViewer widget itself has focus."""
        key = event.key()
        if key in (Qt.Key_Left, Qt.Key_PageUp):
            self.prev_page()
            event.accept()
        elif key in (Qt.Key_Right, Qt.Key_PageDown):
            self.next_page()
            event.accept()
        elif event.modifiers() & Qt.ControlModifier and key == Qt.Key_D:
            self._add_bookmark_here()
            event.accept()
        elif event.modifiers() & Qt.ControlModifier and key == Qt.Key_F:
            self._toggle_search()
            event.accept()
        else:
            super().keyPressEvent(event)

    # ── Search ───────────────────────────────────────────────────────

    def show_find(self):
        self._show_search()

    def _toggle_search(self):
        if self._search_visible:
            self._hide_search()
        else:
            self._show_search()

    def _show_search(self):
        self._search_visible = True
        self.search_bar_widget.show()
        self.search_input.selectAll()
        self.search_input.setFocus()
        if self.search_model and self.search_input.text():
            self.search_model.setSearchString(self.search_input.text().strip())

    def _hide_search(self):
        self._search_visible = False
        self.search_bar_widget.hide()
        if self.search_model:
            self.search_model.setSearchString("")
        self.lbl_search_count.setText("")
        if hasattr(self, "pdf_view") and self.pdf_view:
            self.pdf_view.setFocus()

    def _on_search_text_changed(self, text):
        if not self.search_model:
            return
        query = text.strip()
        self.search_model.setSearchString(query)
        if not query:
            self.lbl_search_count.setText("")

    def _on_search_count_changed(self):
        if not self.search_model or not hasattr(self, "pdf_view"):
            return
        count = self.search_model.count()
        query = self.search_input.text().strip()
        if not query:
            self.lbl_search_count.setText("")
            return
        if count == 0:
            self.lbl_search_count.setText("No matches")
        else:
            cur = self.pdf_view.currentSearchResultIndex()
            if cur < 0:
                self.pdf_view.setCurrentSearchResultIndex(0)
                cur = 0
            self.lbl_search_count.setText(f"{cur + 1} of {count}")

    def _on_search_index_changed(self, idx):
        if not self.search_model:
            return
        count = self.search_model.count()
        if count > 0 and idx >= 0:
            self.lbl_search_count.setText(f"{idx + 1} of {count}")

    def _find_next_result(self):
        if not self.search_model or not hasattr(self, "pdf_view"):
            return
        count = self.search_model.count()
        if count <= 0:
            return
        cur = self.pdf_view.currentSearchResultIndex()
        next_idx = (cur + 1) % count
        self.pdf_view.setCurrentSearchResultIndex(next_idx)

    def _find_prev_result(self):
        if not self.search_model or not hasattr(self, "pdf_view"):
            return
        count = self.search_model.count()
        if count <= 0:
            return
        cur = self.pdf_view.currentSearchResultIndex()
        prev_idx = (cur - 1 + count) % count
        self.pdf_view.setCurrentSearchResultIndex(prev_idx)

    def find_text(self, text, match_case=False, whole_word=False, forward=True):
        if not self.search_model:
            return False
        if not self._search_visible:
            self._show_search()
        if text != self.search_input.text():
            self.search_input.setText(text)
        if forward:
            self._find_next_result()
        else:
            self._find_prev_result()
        return self.search_model.count() > 0

    # ── Annotations ────────────────────────────────────────────────────

    def _set_annot_highlight(self):
        self._deselect_annot_tools()
        self.btn_annot_highlight.setChecked(True)
        self._annot_tool = "highlight"
        if self._overlay:
            self._overlay.set_tool("highlight")
            self._overlay.setVisible(True)

    def _set_annot_note(self):
        self._deselect_annot_tools()
        self.btn_annot_note.setChecked(True)
        self._annot_tool = "note"
        if self._overlay:
            self._overlay.set_tool("note")
            self._overlay.setVisible(True)

    def _set_annot_pen(self):
        self._deselect_annot_tools()
        self.btn_annot_pen.setChecked(True)
        self._annot_tool = "pen"
        if self._overlay:
            self._overlay.set_tool("pen")
            self._overlay.setVisible(True)

    def _set_annot_color(self, name):
        self._annot_color = self._annot_colors.get(name, QColor(255, 255, 0, 120))
        if self._overlay:
            self._overlay.set_color(self._annot_color)

    def _deselect_annot_tools(self):
        self.btn_annot_highlight.setChecked(False)
        self.btn_annot_note.setChecked(False)
        self.btn_annot_pen.setChecked(False)
        self._annot_tool = "none"
        if self._overlay:
            self._overlay.set_tool("none")

    def _clear_annotations(self):
        self._annotations = []
        if self._overlay:
            self._overlay.clear_annotations()
        self._save_annotations()

    def _on_annotation_created(self, ann):
        self._annotations.append(ann)
        self._save_annotations()

    def _on_pdf_resize(self, event):
        if self._overlay:
            self._overlay.setGeometry(self.pdf_view.rect())
        # Call original resizeEvent if it exists
        if hasattr(self.pdf_view, "_original_resize_event"):
            self.pdf_view._original_resize_event(event)

    def _save_annotations(self):
        if not self.file_path:
            return
        sidecar = self.file_path + ".eleviewer_annotations.json"
        try:
            with open(sidecar, "w", encoding="utf-8") as f:
                json.dump(self._annotations, f, indent=2)
        except Exception as e:
            print(f"[PDF] Failed to save annotations: {e}")

    def _load_annotations(self):
        if not self.file_path:
            return
        sidecar = self.file_path + ".eleviewer_annotations.json"
        if not os.path.exists(sidecar):
            return
        try:
            with open(sidecar, "r", encoding="utf-8") as f:
                self._annotations = json.load(f)
            if self._overlay:
                self._overlay.set_annotations(self._annotations)
        except Exception as e:
            print(f"[PDF] Failed to load annotations: {e}")
            self._annotations = []

    # ── Bookmark ─────────────────────────────────────────────────────

    def _bookmark_payload(self):
        return {
            "page_number": self.current_page,
            "scroll_position_y": 0.0,
            "label": f"Page {self.current_page + 1}",
        }

    def _add_bookmark_here(self):
        if self._bookmark_callback:
            self._bookmark_callback(self._bookmark_payload())

    def _show_context_menu(self, pos):
        menu = QMenu(self)
        menu.addAction("Bookmark This Page", self._add_bookmark_here)
        if QTPDF_AVAILABLE:
            menu.exec(self.pdf_view.mapToGlobal(pos))

    # ── TTS ──────────────────────────────────────────────────────────

    def read_current_page(self, voice_id=None):
        if not self.pdf_doc_qt or not TTS_AVAILABLE:
            if self._status_callback:
                self._status_callback("TTS unavailable or document not loaded", 4000)
            return ""
        try:
            selection = self.pdf_doc_qt.getAllText(self.current_page)
            text = selection.text().strip() if hasattr(selection, "text") else ""
        except Exception as e:
            print(f"[PDF] Text extraction error: {e}")
            text = ""

        if not text:
            if self._status_callback:
                self._status_callback("No readable text on this page", 3000)
            return ""

        self.tts.speak(text, voice_id=voice_id)
        if self._status_callback:
            self._status_callback(f"Reading page {self.current_page + 1} aloud...", 2000)
        return text

    # ── Compatibility stubs ──────────────────────────────────────────

    def toPlainText(self):
        return ""

    def setPlainText(self, text):
        pass
