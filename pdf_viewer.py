try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QToolButton, QLabel,
    QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QMessageBox, QComboBox,
)
from PySide6.QtGui import QPixmap, QImage, QWheelEvent, QKeyEvent
from PySide6.QtCore import Qt, Signal, QTimer

from icons import icon
from pdf_tts import PdfTts, TTS_AVAILABLE
from settings import load_settings
from theme import compact_toolbar_stylesheet


class PdfGraphicsView(QGraphicsView):
    zoom_requested = Signal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)

    def wheelEvent(self, event: QWheelEvent):
        if event.modifiers() & Qt.ControlModifier:
            delta = event.angleDelta().y()
            factor = 1.15 if delta > 0 else 1 / 1.15
            self.zoom_requested.emit(factor)
            event.accept()
            return
        super().wheelEvent(event)

    def keyPressEvent(self, event: QKeyEvent):
        parent = self.parent()
        if parent and event.key() in (Qt.Key_Left, Qt.Key_Right, Qt.Key_PageUp, Qt.Key_PageDown):
            parent.keyPressEvent(event)
            return
        super().keyPressEvent(event)


class PdfViewer(QWidget):
    textChanged = Signal()

    def __init__(self, file_path=None, status_callback=None):
        super().__init__()
        self.file_path = file_path
        self.is_modified = False
        self._status_callback = status_callback
        self.doc = None
        self.current_page = 0
        self.total_pages = 0
        self._pixmap_item = None
        self._zoom_factor = 1.0
        self._fit_mode = load_settings().get("pdf_fit_mode", "page")
        self.tts = PdfTts(on_error=self._on_tts_error)

        self.setFocusPolicy(Qt.StrongFocus)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(4, 4, 4, 4)

        self.btn_prev = QToolButton()
        self.btn_prev.setIcon(icon("chevron-left"))
        self.btn_prev.setToolTip("Previous page")
        self.btn_prev.clicked.connect(self.prev_page)

        self.btn_next = QToolButton()
        self.btn_next.setIcon(icon("chevron-right"))
        self.btn_next.setToolTip("Next page")
        self.btn_next.clicked.connect(self.next_page)

        self.lbl_page = QLabel("Page 0 / 0")
        self.lbl_page.setStyleSheet("color: #aaa; font-weight: bold; padding: 0 8px;")

        self.btn_zoom_out = QToolButton()
        self.btn_zoom_out.setIcon(icon("zoom-out"))
        self.btn_zoom_out.setToolTip("Zoom out")
        self.btn_zoom_out.clicked.connect(lambda: self._apply_zoom(1 / 1.2))

        self.btn_fit_page = QToolButton()
        self.btn_fit_page.setIcon(icon("minimize-2"))
        self.btn_fit_page.setToolTip("Fit page")
        self.btn_fit_page.clicked.connect(self.fit_page)

        self.btn_fit_width = QToolButton()
        self.btn_fit_width.setIcon(icon("maximize-2"))
        self.btn_fit_width.setToolTip("Fit width")
        self.btn_fit_width.clicked.connect(self.fit_to_width)

        self.btn_zoom_in = QToolButton()
        self.btn_zoom_in.setIcon(icon("zoom-in"))
        self.btn_zoom_in.setToolTip("Zoom in")
        self.btn_zoom_in.clicked.connect(lambda: self._apply_zoom(1.2))

        self.voice_combo = QComboBox()
        self.voice_combo.setMinimumWidth(140)
        self._populate_voices()

        self.btn_speak = QToolButton()
        self.btn_speak.setIcon(icon("volume-2"))
        self.btn_speak.setToolTip("Read current page aloud")
        self.btn_speak.clicked.connect(self.read_current_page)

        self.btn_stop = QToolButton()
        self.btn_stop.setIcon(icon("square"))
        self.btn_stop.setToolTip("Stop reading")
        self.btn_stop.clicked.connect(self.tts.stop)

        for w in (
            self.btn_prev, self.btn_next, self.btn_zoom_out,
            self.btn_fit_page, self.btn_fit_width, self.btn_zoom_in,
            self.btn_speak, self.btn_stop,
        ):
            w.setStyleSheet(compact_toolbar_stylesheet())
            w.setAutoRaise(True)

        toolbar.addWidget(self.btn_prev)
        toolbar.addWidget(self.lbl_page)
        toolbar.addWidget(self.btn_next)
        toolbar.addStretch()
        toolbar.addWidget(self.btn_zoom_out)
        toolbar.addWidget(self.btn_fit_page)
        toolbar.addWidget(self.btn_fit_width)
        toolbar.addWidget(self.btn_zoom_in)
        toolbar.addWidget(self.voice_combo)
        toolbar.addWidget(self.btn_speak)
        toolbar.addWidget(self.btn_stop)

        self.view = PdfGraphicsView(self)
        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)
        self.view.setStyleSheet("background: #1e1e1e; border: none;")
        self.view.zoom_requested.connect(self._apply_zoom)

        layout.addLayout(toolbar)
        layout.addWidget(self.view)

        if file_path:
            self.load_from_path(file_path)

    def set_status_callback(self, callback):
        self._status_callback = callback

    def _on_tts_error(self, message):
        if self._status_callback:
            self._status_callback(f"TTS error: {message}", 4000)

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(50, self._apply_default_fit)

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

    def _render_quality_scale(self):
        settings = load_settings()
        dpr = self.view.devicePixelRatioF() or 1.0
        if settings.get("pdf_render_quality", "high") == "high":
            return max(dpr, 1.5)
        return 1.0

    def load_from_path(self, file_path):
        if not PYMUPDF_AVAILABLE:
            QMessageBox.critical(
                self, "Missing Dependency",
                "PyMuPDF is required.\nPlease run: pip install PyMuPDF",
            )
            return
        try:
            self.doc = fitz.open(file_path)
            self.total_pages = len(self.doc)
            self.current_page = 0
            self._zoom_factor = 1.0
            self._fit_mode = load_settings().get("pdf_fit_mode", "page")
            self.render_page()
            QTimer.singleShot(50, self._apply_default_fit)
            self.is_modified = False
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load PDF: {str(e)}")

    def _page_render_scale(self):
        if not self.doc:
            return 1.0
        page = self.doc.load_page(self.current_page)
        viewport = self.view.viewport()
        vw = max(viewport.width(), 400)
        vh = max(viewport.height(), 500)
        quality = self._render_quality_scale()

        if self._fit_mode == "width":
            base = vw / page.rect.width
        else:
            base = min(vw / page.rect.width, vh / page.rect.height)

        return base * quality

    def render_page(self):
        if not self.doc or self.total_pages == 0:
            return

        page = self.doc.load_page(self.current_page)
        scale = self._page_render_scale()
        mat = fitz.Matrix(scale, scale)
        pix = page.get_pixmap(matrix=mat)

        img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
        qpixmap = QPixmap.fromImage(img)

        self.scene.clear()
        self._pixmap_item = QGraphicsPixmapItem(qpixmap)
        self.scene.addItem(self._pixmap_item)
        self.scene.setSceneRect(self._pixmap_item.boundingRect())

        self.lbl_page.setText(f"Page {self.current_page + 1} / {self.total_pages}")
        self.view.resetTransform()
        self._zoom_factor = 1.0

    def _apply_default_fit(self):
        if self._fit_mode == "width":
            self.fit_to_width()
        else:
            self.fit_page()

    def fit_page(self):
        if self._pixmap_item:
            self.view.fitInView(self._pixmap_item, Qt.KeepAspectRatio)
            self._zoom_factor = 1.0
            self._fit_mode = "page"

    def fit_to_width(self):
        if not self._pixmap_item:
            return
        vp = self.view.viewport().rect()
        scene_rect = self._pixmap_item.boundingRect()
        if scene_rect.width() <= 0:
            return
        self.view.resetTransform()
        scale = vp.width() / scene_rect.width()
        self.view.scale(scale, scale)
        self._zoom_factor = scale
        self._fit_mode = "width"

    def _apply_zoom(self, factor):
        self.view.scale(factor, factor)
        self._zoom_factor *= factor

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.doc and self._pixmap_item:
            self.render_page()
            QTimer.singleShot(0, self._apply_default_fit)

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        if key in (Qt.Key_Left, Qt.Key_PageUp):
            self.prev_page()
            event.accept()
        elif key in (Qt.Key_Right, Qt.Key_PageDown):
            self.next_page()
            event.accept()
        else:
            super().keyPressEvent(event)

    def prev_page(self):
        if self.current_page > 0:
            self.tts.stop()
            self.current_page -= 1
            self.render_page()
            QTimer.singleShot(0, self._apply_default_fit)

    def next_page(self):
        if self.current_page < self.total_pages - 1:
            self.tts.stop()
            self.current_page += 1
            self.render_page()
            QTimer.singleShot(0, self._apply_default_fit)

    def read_current_page(self):
        if not self.doc or not TTS_AVAILABLE:
            return
        page = self.doc.load_page(self.current_page)
        text = page.get_text().strip()
        if not text:
            if self._status_callback:
                self._status_callback("No readable text on this page", 3000)
            return
        voice_id = self.voice_combo.currentData()
        self.tts.speak(text, voice_id=voice_id or None)
        if self._status_callback:
            self._status_callback("Reading page aloud...", 2000)

    def toPlainText(self):
        return ""

    def setPlainText(self, text):
        pass
