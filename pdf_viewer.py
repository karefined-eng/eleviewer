"""PDF viewer using Qt's native QPdfView for vector-crisp rendering.

Display layer: QPdfDocument + QPdfView (PDFium-based, always sharp text).
Background:    PyMuPDF (fitz) kept only for TTS text extraction and TOC scanning.
"""

import json
import os
import re

try:
    from PySide6.QtPdf import QPdfDocument, QPdfBookmarkModel
    from PySide6.QtPdfWidgets import QPdfView
    QTPDF_AVAILABLE = True
except ImportError:
    QTPDF_AVAILABLE = False

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QToolButton, QLabel,
    QMessageBox, QComboBox, QMenu, QLineEdit, QTreeView,
    QSplitter,
)
from PySide6.QtGui import QIntValidator, QKeyEvent, QWheelEvent
from PySide6.QtCore import Qt, Signal, QTimer, QSize, QPointF

from icons import icon
from tts_engine import TtsEngine as PdfTts, TTS_AVAILABLE
from settings import load_settings
from theme import compact_toolbar_stylesheet, ICON_SIZE_COMPACT
from paths import APP_DATA_DIR

# ── Custom QPdfView with Ctrl+Wheel zoom and key navigation ─────────

if QTPDF_AVAILABLE:
    class EleViewerPdfView(QPdfView):
        """QPdfView subclass adding Ctrl+Wheel zoom and arrow-key page changes."""
        page_change = Signal(int)       # -1 for prev, +1 for next
        bookmark_requested = Signal()

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
        self._toc_visible = False
        self._multi_page = False
        self.tts = PdfTts(on_error=self._on_tts_error)

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
        self.btn_prev     = _tb("chevron-left",  "Previous page",           self.prev_page)
        self.btn_next     = _tb("chevron-right", "Next page",               self.next_page)

        # Page input  ─ editable box + "/ N" label
        self.page_input = QLineEdit()
        self.page_input.setFixedWidth(44)
        self.page_input.setAlignment(Qt.AlignCenter)
        self.page_input.setValidator(QIntValidator(1, 99999))
        self.page_input.setStyleSheet(
            "QLineEdit { background:#242424; color:#f2f2f0; border:1px solid #2c2c2c;"
            " border-radius:4px; padding:2px 4px; font-weight:bold; font-size:12px; }"
        )
        self.page_input.returnPressed.connect(self._jump_to_page)
        self.lbl_total = QLabel(" / 0")
        self.lbl_total.setStyleSheet("color:#9b9b96; font-weight:bold; padding:0 6px 0 2px; font-size:12px;")

        self.btn_zoom_out  = _tb("zoom-out",   "Zoom out",                lambda: self._apply_zoom(1 / 1.2))
        self.btn_fit_page  = _tb("maximize",   "Fit to page",             self.fit_page)
        self.btn_fit_width = _tb("monitor",    "Fit to width",            self.fit_to_width)
        self.btn_zoom_in   = _tb("zoom-in",    "Zoom in",                 lambda: self._apply_zoom(1.2))
        self.btn_multi     = _tb("columns",    "Two-page view",           self._toggle_multi_page)
        self.btn_bookmark  = _tb("bookmark",   "Bookmark this page",      self._add_bookmark_here, "Bookmark")

        toolbar.addWidget(self.btn_toc)
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

        # ── Content area: TOC splitter + QPdfView ───────────────────
        self.content_splitter = QSplitter(Qt.Horizontal)

        # TOC panel
        self.toc_widget = QWidget()
        toc_layout = QVBoxLayout(self.toc_widget)
        toc_layout.setContentsMargins(0, 0, 0, 0)
        toc_layout.setSpacing(0)
        toc_lbl = QLabel("Table of Contents")
        toc_lbl.setStyleSheet(
            "background:#1a1a1a; color:#888; font-size:11px; font-weight:bold;"
            " padding:6px 8px; border-bottom:1px solid #333;"
        )
        self.toc_tree = QTreeView()
        self.toc_tree.setHeaderHidden(True)
        self.bookmark_model = None
        self.toc_tree.setStyleSheet(
            "QTreeView { background:#1e1e1e; border:none; color:#d0d0d0; font-size:12px; }"
            "QTreeView::item { padding:4px 6px; }"
            "QTreeView::item:selected { background:#37373d; }"
            "QTreeView::item:hover { background:#2a2a2a; }"
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
            self.pdf_view.setPageMode(QPdfView.PageMode.SinglePage)
            self.pdf_view.setZoomMode(QPdfView.ZoomMode.FitToWidth)
            self.pdf_view.setStyleSheet("background: #1e1e1e; border: none;")
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

        outer.addLayout(toolbar)
        outer.addWidget(self.content_splitter)

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

    def load_from_path(self, file_path):
        if not QTPDF_AVAILABLE:
            QMessageBox.critical(
                self, "Missing Dependency",
                "PySide6 QtPdf module is required.\nPlease update PySide6 to 6.6+.",
            )
            return
        try:
            # Load into Qt's native PDF engine for display
            self.pdf_doc_qt.load(file_path)
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
        if not QTPDF_AVAILABLE:
            return
        nav = self.pdf_view.pageNavigator()
        cur = nav.currentPage()
        if cur > 0:
            self.tts.stop()
            nav.jump(cur - 1, QPointF(), 0)

    def next_page(self):
        if not QTPDF_AVAILABLE:
            return
        nav = self.pdf_view.pageNavigator()
        cur = nav.currentPage()
        if cur < self.total_pages - 1:
            self.tts.stop()
            nav.jump(cur + 1, QPointF(), 0)

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
        else:
            super().keyPressEvent(event)

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

    def read_current_page(self):
        if not self.pdf_doc_qt or not TTS_AVAILABLE:
            if self._status_callback:
                self._status_callback("TTS unavailable or document not loaded", 4000)
            return
        text = self.pdf_doc_qt.getAllText(self.current_page).text().strip()
        if not text:
            if self._status_callback:
                self._status_callback("No readable text on this page", 3000)
            return
        voice_id = self.voice_combo.currentData()
        self.tts.speak(text, voice_id=voice_id or None)
        if self._status_callback:
            self._status_callback("Reading page aloud...", 2000)

    # ── Compatibility stubs ──────────────────────────────────────────

    def toPlainText(self):
        return ""

    def setPlainText(self, text):
        pass
