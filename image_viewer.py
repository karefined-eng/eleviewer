"""Image viewer widget for EleViewer.

Supports PNG, JPG, JPEG, GIF, BMP, SVG, WEBP, ICO.
Features smooth zoom, fit to window, actual size, and mouse drag panning.
"""

import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QToolButton, QLabel,
    QScrollArea, QSizePolicy
)
from PySide6.QtGui import (
    QPixmap, QMovie, QWheelEvent, QMouseEvent,
    QPainter, QColor
)
from PySide6.QtCore import Qt, Signal, QSize, QPoint

try:
    from PySide6.QtSvgWidgets import QSvgWidget
    SVG_AVAILABLE = True
except ImportError:
    SVG_AVAILABLE = False

from icons import icon
from theme import (
    get_active_palette,
    compact_toolbar_stylesheet, ICON_SIZE_COMPACT
)


class ImageScrollArea(QScrollArea):
    """Custom scroll area adding Ctrl+Wheel zoom and click-and-drag panning."""

    def __init__(self, parent_viewer, parent=None):
        super().__init__(parent)
        self.viewer = parent_viewer
        self._dragging = False
        self._drag_start = QPoint()

    def wheelEvent(self, event: QWheelEvent):
        if event.modifiers() & Qt.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self.viewer.zoom_in()
            else:
                self.viewer.zoom_out()
            event.accept()
            return
        super().wheelEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self._dragging = True
            self._drag_start = event.pos()
            self.setCursor(Qt.ClosedHandCursor)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._dragging:
            delta = event.pos() - self._drag_start
            self._drag_start = event.pos()
            h_bar = self.horizontalScrollBar()
            v_bar = self.verticalScrollBar()
            h_bar.setValue(h_bar.value() - delta.x())
            v_bar.setValue(v_bar.value() - delta.y())
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton and self._dragging:
            self._dragging = False
            self.setCursor(Qt.ArrowCursor)
            event.accept()
            return
        super().mouseReleaseEvent(event)


class ImageViewer(QWidget):
    textChanged = Signal()

    def __init__(self, file_path=None):
        super().__init__()
        self.file_path = file_path
        self.is_modified = False
        self._zoom_factor = 1.0
        self._fit_to_window = True
        self._movie = None
        self._orig_pixmap = None
        self._svg_widget = None
        self._orig_size = QSize(0, 0)

        p = get_active_palette()
        self.setStyleSheet(f"background: {p['BRAND_BACKGROUND']};")

        # ── Outer Layout ────────────────────────────────────────────
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

        self.btn_zoom_out = _tb("zoom-out", "Zoom Out (Ctrl+Minus)", self.zoom_out)
        self.btn_fit = _tb("maximize-2", "Fit to Window", self.fit_to_window, "Fit")
        self.btn_actual = _tb("square", "Original Size (100%)", self.actual_size, "100%")
        self.btn_zoom_in = _tb("zoom-in", "Zoom In (Ctrl+Plus)", self.zoom_in)

        self.lbl_zoom = QLabel("100%")
        self.lbl_zoom.setStyleSheet(f"color: {p['BRAND_MUTED_FG']}; font-weight: bold; font-size: 11px; padding: 0 6px;")

        self.lbl_dimensions = QLabel("")
        self.lbl_dimensions.setStyleSheet(f"color: {p['BRAND_MUTED_FG']}; font-size: 11px; padding: 0 8px;")

        toolbar.addWidget(self.btn_zoom_out)
        toolbar.addWidget(self.btn_fit)
        toolbar.addWidget(self.btn_actual)
        toolbar.addWidget(self.btn_zoom_in)
        toolbar.addWidget(self.lbl_zoom)
        toolbar.addStretch()
        toolbar.addWidget(self.lbl_dimensions)

        outer.addLayout(toolbar)

        # ── Scroll Area and Image Container ─────────────────────────
        self.scroll_area = ImageScrollArea(self)
        self.scroll_area.setStyleSheet(f"QScrollArea {{ border: none; background: {p['BRAND_BACKGROUND']}; }}")
        self.scroll_area.setAlignment(Qt.AlignCenter)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.image_label.setScaledContents(True)

        self.scroll_area.setWidget(self.image_label)
        outer.addWidget(self.scroll_area)

        if file_path:
            self.load_from_path(file_path)

    def load_from_path(self, file_path):
        self.file_path = file_path
        ext = os.path.splitext(file_path)[1].lower().lstrip(".")

        if ext == "svg" and SVG_AVAILABLE:
            self._svg_widget = QSvgWidget(file_path)
            self.scroll_area.setWidget(self._svg_widget)
            s = self._svg_widget.sizeHint()
            self._orig_size = s
            self.lbl_dimensions.setText(f"{s.width()} × {s.height()} px (SVG)")
            self._fit_to_window = True
            self._apply_zoom()
            return

        if ext == "gif":
            self._movie = QMovie(file_path)
            if self._movie.isValid():
                self.image_label.setMovie(self._movie)
                self._movie.start()
                first_frame = self._movie.currentPixmap()
                if not first_frame.isNull():
                    self._orig_pixmap = first_frame
                    self._orig_size = first_frame.size()
                    self.lbl_dimensions.setText(f"{first_frame.width()} × {first_frame.height()} px (GIF)")
                self._fit_to_window = True
                self._apply_zoom()
                return

        pix = QPixmap(file_path)
        if not pix.isNull():
            self._orig_pixmap = pix
            self._orig_size = pix.size()
            self.lbl_dimensions.setText(f"{pix.width()} × {pix.height()} px")
            self._fit_to_window = True
            self._apply_zoom()
        else:
            self.image_label.setText("Failed to load image.")
            self.image_label.setStyleSheet("color: red; font-size: 14px;")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._fit_to_window:
            self._apply_zoom()

    def zoom_in(self):
        self._fit_to_window = False
        self._zoom_factor = min(self._zoom_factor * 1.25, 20.0)
        self._apply_zoom()

    def zoom_out(self):
        self._fit_to_window = False
        self._zoom_factor = max(self._zoom_factor / 1.25, 0.05)
        self._apply_zoom()

    def fit_to_window(self):
        self._fit_to_window = True
        self._apply_zoom()

    def actual_size(self):
        self._fit_to_window = False
        self._zoom_factor = 1.0
        self._apply_zoom()

    def _apply_zoom(self):
        if self._svg_widget is not None:
            if self._fit_to_window:
                area_size = self.scroll_area.viewport().size()
                orig = self._orig_size
                if orig.width() > 0 and orig.height() > 0:
                    w_ratio = (area_size.width() - 8) / orig.width()
                    h_ratio = (area_size.height() - 8) / orig.height()
                    ratio = min(w_ratio, h_ratio, 1.0)
                    self._zoom_factor = max(ratio, 0.05)
            target_w = max(1, int(self._orig_size.width() * self._zoom_factor))
            target_h = max(1, int(self._orig_size.height() * self._zoom_factor))
            self._svg_widget.setFixedSize(target_w, target_h)
            self.lbl_zoom.setText(f"{int(self._zoom_factor * 100)}%")
            return

        if self._orig_pixmap is None or self._orig_pixmap.isNull():
            return

        if self._fit_to_window:
            area_size = self.scroll_area.viewport().size()
            orig_w = self._orig_pixmap.width()
            orig_h = self._orig_pixmap.height()
            if orig_w > 0 and orig_h > 0:
                w_ratio = (area_size.width() - 8) / orig_w
                h_ratio = (area_size.height() - 8) / orig_h
                self._zoom_factor = min(w_ratio, h_ratio, 1.0)

        target_w = max(1, int(self._orig_pixmap.width() * self._zoom_factor))
        target_h = max(1, int(self._orig_pixmap.height() * self._zoom_factor))

        if self._movie and self._movie.isValid():
            self._movie.setScaledSize(QSize(target_w, target_h))
            self.image_label.setFixedSize(target_w, target_h)
        else:
            scaled_pix = self._orig_pixmap.scaled(
                target_w, target_h,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pix)
            self.image_label.setFixedSize(target_w, target_h)

        self.lbl_zoom.setText(f"{int(self._zoom_factor * 100)}%")

    # ── Compatibility methods for MainWindow ─────────────────────────

    def toPlainText(self):
        return ""

    def setPlainText(self, text):
        pass
