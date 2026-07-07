import json
import os
import re

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QToolButton, QLabel,
    QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QMessageBox,
    QComboBox, QMenu, QLineEdit, QTreeWidget, QTreeWidgetItem, QSplitter,
    QSizePolicy,
)
from PySide6.QtGui import QPixmap, QImage, QWheelEvent, QKeyEvent, QIntValidator
from PySide6.QtCore import Qt, Signal, QTimer, QSize

from icons import icon
from pdf_tts import PdfTts, TTS_AVAILABLE
from settings import load_settings
from theme import compact_toolbar_stylesheet, ICON_SIZE_COMPACT
from paths import APP_DATA_DIR

TOC_CACHE_PATH = APP_DATA_DIR / "pdf_toc_cache.json"


def _load_toc_cache():
    try:
        with open(TOC_CACHE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_toc_cache(cache):
    try:
        os.makedirs(os.path.dirname(TOC_CACHE_PATH), exist_ok=True)
        with open(TOC_CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2)
    except Exception:
        pass


def _scan_toc_from_text(doc):
    """
    Scan the first 10 pages for a Table of Contents page.
    Returns list of (title, page_number_1indexed) tuples, or [].
    """
    max_scan = min(10, len(doc))
    toc_page_text = None

    for i in range(max_scan):
        page = doc.load_page(i)
        text = page.get_text()
        if re.search(r'\b(table\s+of\s+contents?|contents?)\b', text, re.IGNORECASE):
            toc_page_text = text
            break

    if not toc_page_text:
        return []

    entries = []
    # Match: "Title text .......... 47" or "Title text   47" at line end
    pattern = re.compile(
        r'^(.+?)[\.\s]{2,}(\d{1,4})\s*$',
        re.MULTILINE,
    )
    for m in pattern.finditer(toc_page_text):
        title = m.group(1).strip()
        page_num = int(m.group(2))
        # Filter out noise: title must be at least 3 chars, page must be > 0
        if len(title) >= 3 and page_num > 0:
            entries.append((title, page_num))

    return entries


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
        self._bookmark_callback = None
        self.doc = None
        self.current_page = 0
        self.total_pages = 0
        self._pixmap_item = None
        self._user_zoom = 1.0
        self._fit_mode = load_settings().get("pdf_fit_mode", "width")
        self._cached_page = -1
        self._cached_render_scale = 0.0
        self._layout_complete = False
        self._first_resize_pending = True
        self._rotation = 0          # 0 / 90 / 180 / 270
        self._double_page = False   # side-by-side mode
        self._toc_visible = False
        self.tts = PdfTts(on_error=self._on_tts_error)

        self.setFocusPolicy(Qt.StrongFocus)

        # ── Outer layout ────────────────────────────────────────────
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # ── Toolbar ─────────────────────────────────────────────────
        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(4, 4, 4, 4)
        icon_sz = ICON_SIZE_COMPACT
        icon_qsize = QSize(icon_sz, icon_sz)

        def _tb(icon_name, tooltip, slot):
            btn = QToolButton()
            btn.setIconSize(icon_qsize)
            btn.setIcon(icon(icon_name, size=icon_sz))
            btn.setToolTip(tooltip)
            btn.setStyleSheet(compact_toolbar_stylesheet())
            btn.setAutoRaise(True)
            btn.clicked.connect(slot)
            return btn

        self.btn_toc      = _tb("list",       "Toggle Table of Contents",  self._toggle_toc)
        self.btn_prev     = _tb("chevron-left","Previous page",             self.prev_page)
        self.btn_next     = _tb("chevron-right","Next page",                self.next_page)

        # Page input  ─ editable box + "/ N" label
        self.page_input = QLineEdit()
        self.page_input.setFixedWidth(48)
        self.page_input.setAlignment(Qt.AlignCenter)
        self.page_input.setValidator(QIntValidator(1, 99999))
        self.page_input.setStyleSheet(
            "QLineEdit { background:#2d2d2d; color:#e0e0e0; border:1px solid #444;"
            " border-radius:3px; padding:1px 4px; font-weight:bold; }"
        )
        self.page_input.returnPressed.connect(self._jump_to_page)
        self.lbl_total = QLabel(" / 0")
        self.lbl_total.setStyleSheet("color:#aaa; font-weight:bold; padding:0 6px 0 0;")

        self.btn_zoom_out  = _tb("zoom-out",   "Zoom out",   lambda: self._apply_zoom(1 / 1.2))
        self.btn_fit_page  = _tb("minimize-2", "Fit page",   self.fit_page)
        self.btn_fit_width = _tb("maximize-2", "Fit width",  self.fit_to_width)
        self.btn_zoom_in   = _tb("zoom-in",    "Zoom in",    lambda: self._apply_zoom(1.2))
        self.btn_rotate    = _tb("rotate-cw",  "Rotate 90°", self._rotate_page)
        self.btn_dbl_page  = _tb("columns-2",  "Toggle double-page view", self._toggle_double_page)
        self.btn_bookmark  = _tb("book-open",  "Bookmark this page",      self._add_bookmark_here)

        self.voice_combo = QComboBox()
        self.voice_combo.setMinimumWidth(140)
        self._populate_voices()

        self.btn_speak = _tb("volume-2", "Read current page aloud", self.read_current_page)
        self.btn_stop  = _tb("square",   "Stop reading",            self.tts.stop)

        toolbar.addWidget(self.btn_toc)
        toolbar.addWidget(self.btn_prev)
        toolbar.addWidget(self.page_input)
        toolbar.addWidget(self.lbl_total)
        toolbar.addWidget(self.btn_next)
        toolbar.addStretch()
        toolbar.addWidget(self.btn_zoom_out)
        toolbar.addWidget(self.btn_fit_page)
        toolbar.addWidget(self.btn_fit_width)
        toolbar.addWidget(self.btn_zoom_in)
        toolbar.addWidget(self.btn_rotate)
        toolbar.addWidget(self.btn_dbl_page)
        toolbar.addWidget(self.btn_bookmark)
        toolbar.addWidget(self.voice_combo)
        toolbar.addWidget(self.btn_speak)
        toolbar.addWidget(self.btn_stop)

        # ── Content area: TOC splitter + graphics view ───────────────
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
        self.toc_tree = QTreeWidget()
        self.toc_tree.setHeaderHidden(True)
        self.toc_tree.setStyleSheet(
            "QTreeWidget { background:#1e1e1e; border:none; color:#d0d0d0; font-size:12px; }"
            "QTreeWidget::item { padding:4px 6px; }"
            "QTreeWidget::item:selected { background:#37373d; }"
            "QTreeWidget::item:hover { background:#2a2a2a; }"
        )
        self.toc_tree.itemClicked.connect(self._on_toc_item_clicked)
        toc_layout.addWidget(toc_lbl)
        toc_layout.addWidget(self.toc_tree)
        self.toc_widget.setMinimumWidth(160)
        self.toc_widget.setMaximumWidth(300)
        self.toc_widget.hide()

        # Graphics view
        self.view = PdfGraphicsView(self)
        self.view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.view.customContextMenuRequested.connect(self._show_context_menu)
        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)
        self.view.setStyleSheet("background: #1e1e1e; border: none;")
        self.view.zoom_requested.connect(self._apply_zoom)

        self.content_splitter.addWidget(self.toc_widget)
        self.content_splitter.addWidget(self.view)

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

    # ── Show / resize ────────────────────────────────────────────────

    def showEvent(self, event):
        super().showEvent(event)
        self._layout_complete = False
        QTimer.singleShot(100, self._ensure_viewport_ready)

    def _ensure_viewport_ready(self):
        if self.view.viewport().width() > 0 and self._layout_complete:
            self._apply_default_fit()
        else:
            if self.view.viewport().width() > 0:
                self._layout_complete = True
                self._apply_default_fit()
            else:
                QTimer.singleShot(100, self._ensure_viewport_ready)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.view.viewport().width() > 0:
            self._layout_complete = True
        if self.doc and self._pixmap_item:
            if self._first_resize_pending:
                self._first_resize_pending = False
                QTimer.singleShot(100, self._ensure_viewport_ready)
            self._apply_default_fit()

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
            self._user_zoom = 1.0
            self._rotation = 0
            self._double_page = False
            self._cached_page = -1
            self._cached_render_scale = 0.0
            self._fit_mode = load_settings().get("pdf_fit_mode", "width")
            self._layout_complete = False
            self.lbl_total.setText(f" / {self.total_pages}")
            self.page_input.setValidator(QIntValidator(1, self.total_pages))
            self.render_page(force=True)
            QTimer.singleShot(100, self._ensure_viewport_ready)
            self.is_modified = False
            self._load_toc(file_path)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load PDF: {str(e)}")

    def _load_toc(self, file_path):
        """Load TOC: built-in outline first, then cached scan, then live scan."""
        self.toc_tree.clear()
        entries = []  # list of (level, title, page_1indexed)

        # Tier 1: built-in outline
        raw = self.doc.get_toc()
        if raw:
            entries = [(lvl, title, pg) for lvl, title, pg in raw]
        else:
            # Tier 2: check cache
            cache = _load_toc_cache()
            key = os.path.abspath(file_path)
            if key in cache:
                cached = cache[key]
                entries = [(1, t, p) for t, p in cached]
            else:
                # Tier 3: live text scan
                scanned = _scan_toc_from_text(self.doc)
                if scanned:
                    cache[key] = scanned
                    _save_toc_cache(cache)
                    entries = [(1, t, p) for t, p in scanned]

        if not entries:
            item = QTreeWidgetItem(["No outline found"])
            item.setFlags(Qt.ItemIsEnabled)  # not selectable
            item.setData(0, Qt.UserRole, -1)
            self.toc_tree.addTopLevelItem(item)
            return

        # Build tree — level 1 = top-level, level 2+ = children
        stack = []  # (level, QTreeWidgetItem)
        for lvl, title, pg in entries:
            node = QTreeWidgetItem([f"{title}"])
            node.setData(0, Qt.UserRole, pg - 1)  # store 0-indexed page
            node.setToolTip(0, f"Page {pg}")
            if not stack or lvl <= stack[0][0]:
                self.toc_tree.addTopLevelItem(node)
                stack = [(lvl, node)]
            else:
                # Find parent
                while len(stack) > 1 and stack[-1][0] >= lvl:
                    stack.pop()
                stack[-1][1].addChild(node)
                stack.append((lvl, node))

        self.toc_tree.expandAll()

    def _on_toc_item_clicked(self, item, _col):
        page = item.data(0, Qt.UserRole)
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

    # ── Render ───────────────────────────────────────────────────────

    def _render_quality_scale(self):
        settings = load_settings()
        dpr = self.view.devicePixelRatioF() or 1.0
        if settings.get("pdf_render_quality", "high") == "high":
            return max(dpr, 1.5)
        return 1.0

    def _compute_render_scale(self):
        if not self.doc:
            return 1.0
        page = self.doc.load_page(self.current_page)
        viewport = self.view.viewport()
        vw = max(viewport.width(), 400)
        vh = max(viewport.height(), 500)
        quality = self._render_quality_scale()

        # In double-page mode, halve available width
        if self._double_page:
            vw = max(vw // 2 - 4, 200)

        if self._fit_mode == "width":
            base = vw / page.rect.width
        else:
            base = min(vw / page.rect.width, vh / page.rect.height)

        return base * quality * max(self._user_zoom, 1.0)

    def _needs_rerender(self, new_scale):
        if self._cached_page != self.current_page:
            return True
        if self._cached_render_scale <= 0:
            return True
        ratio = new_scale / self._cached_render_scale
        return ratio < 0.9 or ratio > 1.1

    def _page_to_pixmap(self, page_index, scale):
        """Render a single PDF page to QPixmap."""
        page = self.doc.load_page(page_index)
        mat = fitz.Matrix(scale, scale).prerotate(self._rotation)
        pix = page.get_pixmap(matrix=mat)
        img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
        return QPixmap.fromImage(img)

    def render_page(self, force=False):
        if not self.doc or self.total_pages == 0:
            return

        scale = self._compute_render_scale()
        if not force and not self._needs_rerender(scale):
            self.page_input.setText(str(self.current_page + 1))
            return

        self.scene.clear()

        if self._double_page and self.current_page + 1 < self.total_pages:
            # Render two pages side by side
            pm_left  = self._page_to_pixmap(self.current_page, scale)
            pm_right = self._page_to_pixmap(self.current_page + 1, scale)
            gap = 8
            item_left  = QGraphicsPixmapItem(pm_left)
            item_right = QGraphicsPixmapItem(pm_right)
            item_right.setX(pm_left.width() + gap)
            self.scene.addItem(item_left)
            self.scene.addItem(item_right)
            self._pixmap_item = item_left
            total_w = pm_left.width() + gap + pm_right.width()
            total_h = max(pm_left.height(), pm_right.height())
            from PySide6.QtCore import QRectF
            self.scene.setSceneRect(QRectF(0, 0, total_w, total_h))
        else:
            qpixmap = self._page_to_pixmap(self.current_page, scale)
            self._pixmap_item = QGraphicsPixmapItem(qpixmap)
            self.scene.addItem(self._pixmap_item)
            self.scene.setSceneRect(self._pixmap_item.boundingRect())

        self._cached_page = self.current_page
        self._cached_render_scale = scale
        self.page_input.setText(str(self.current_page + 1))
        self.view.resetTransform()

        # Highlight current TOC item
        self._highlight_toc_item()

    def _highlight_toc_item(self):
        """Select the TOC item whose page is closest to the current page."""
        cur = self.current_page
        best_item = None
        best_dist = 99999
        it = QTreeWidgetItemIterator(self.toc_tree)
        while it.value():
            item = it.value()
            pg = item.data(0, Qt.UserRole)
            if pg is not None and pg >= 0:
                dist = abs(pg - cur)
                if dist < best_dist:
                    best_dist = dist
                    best_item = item
            it += 1
        if best_item:
            self.toc_tree.blockSignals(True)
            self.toc_tree.setCurrentItem(best_item)
            self.toc_tree.blockSignals(False)

    # ── Fit / zoom ───────────────────────────────────────────────────

    def _apply_default_fit(self):
        if self._fit_mode == "width":
            self.fit_to_width()
        else:
            self.fit_page()

    def fit_page(self):
        if self._pixmap_item:
            self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
            self._user_zoom = 1.0
            self._fit_mode = "page"

    def fit_to_width(self):
        if not self._pixmap_item:
            return
        vp = self.view.viewport().rect()
        scene_rect = self.scene.sceneRect()
        if scene_rect.width() <= 0:
            return
        self.view.resetTransform()
        scale = vp.width() / scene_rect.width()
        self.view.scale(scale, scale)
        self._fit_mode = "width"

    def _apply_zoom(self, factor):
        self._user_zoom *= factor
        self.view.scale(factor, factor)
        new_scale = self._compute_render_scale()
        if self._needs_rerender(new_scale):
            self.render_page(force=True)
            self._apply_default_fit()

    # ── Rotation ─────────────────────────────────────────────────────

    def _rotate_page(self):
        self._rotation = (self._rotation + 90) % 360
        self._cached_page = -1  # force rerender
        self.render_page(force=True)
        QTimer.singleShot(0, self._apply_default_fit)

    # ── Double-page toggle ───────────────────────────────────────────

    def _toggle_double_page(self):
        self._double_page = not self._double_page
        self._cached_page = -1
        self.render_page(force=True)
        QTimer.singleShot(0, self._apply_default_fit)
        style = "background:#3c3c3c;" if self._double_page else ""
        self.btn_dbl_page.setStyleSheet(compact_toolbar_stylesheet() + style)

    # ── Navigation ───────────────────────────────────────────────────

    def prev_page(self):
        step = 2 if self._double_page else 1
        if self.current_page > 0:
            self.tts.stop()
            self.current_page = max(0, self.current_page - step)
            self._user_zoom = 1.0
            self.render_page(force=True)
            QTimer.singleShot(0, self._apply_default_fit)

    def next_page(self):
        step = 2 if self._double_page else 1
        if self.current_page < self.total_pages - 1:
            self.tts.stop()
            self.current_page = min(self.total_pages - 1, self.current_page + step)
            self._user_zoom = 1.0
            self.render_page(force=True)
            QTimer.singleShot(0, self._apply_default_fit)

    def go_to_bookmark(self, page_number=0, scroll_position_y=0.0):
        if not self.doc:
            return
        page_number = max(0, min(int(page_number), self.total_pages - 1))
        if page_number == self.current_page and self._pixmap_item:
            return
        self.tts.stop()
        self.current_page = page_number
        self._user_zoom = 1.0
        self.render_page(force=True)
        QTimer.singleShot(100, self._ensure_viewport_ready)

    def keyPressEvent(self, event: QKeyEvent):
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
        menu.exec(self.view.mapToGlobal(pos))

    # ── TTS ──────────────────────────────────────────────────────────

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


# Needed for _highlight_toc_item iteration
from PySide6.QtWidgets import QTreeWidgetItemIterator  # noqa: E402
