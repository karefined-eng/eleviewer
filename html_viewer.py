
"""
HTML Table & Document Workstation for EleViewer.
Provides Split-Screen real-time HTML/CSS/JS previewing (QSplitter with 300ms debounce),
monochromatic syntax highlighting, Universal TTS (F9) support, and 1-click Browser Migration
to EleViewer's integrated Chromium WebPanel.
"""

import os
import re
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QPlainTextEdit,
    QToolButton, QLabel, QApplication, QTextBrowser
)
from PySide6.QtCore import Qt, Signal, QTimer, QUrl, QSize
from PySide6.QtGui import QFont, QColor, QIcon, QTextDocument, QShortcut, QKeySequence

from theme import (
    BRAND_PANEL, BRAND_PRIMARY, BRAND_MUTED_FG, get_brand_accent,
    BRAND_BORDER, BRAND_BACKGROUND, compact_toolbar_stylesheet,
    ICON_SIZE_COMPACT, resolve_markdown_icon_size, markdown_editor_stylesheet, get_active_palette
)
from icons import icon
from syntax_highlighter import HtmlHighlighter
from paths import APP_DATA_DIR

try:
    from web_panel import WebViewWrapper, WEB_AVAILABLE
except ImportError:
    WEB_AVAILABLE = False


class HtmlViewer(QWidget):
    """
    Dedicated HTML/XML Workstation with live split-screen previewing and WebPanel migration.
    """
    textChanged = Signal()
    pushToBrowserRequested = Signal(str, str)  # (file_path, url_str)

    def __init__(self, file_path=None, content=None, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.is_modified = False
        self._mode = "split"  # "preview", "syntax", "split"
        self._icon_size = resolve_markdown_icon_size()

        self._setup_ui()

        # 300ms debounce timer for live rendering without typing lag or flickering
        self._debounce_timer = QTimer(self)
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.setInterval(300)
        self._debounce_timer.timeout.connect(self._update_live_preview)

        if content is not None:
            self.setPlainText(content)
        elif file_path and os.path.exists(file_path):
            self.load_from_path(file_path)
        else:
            self.setPlainText("<!DOCTYPE html>\n<html>\n<head>\n  <title>Live Feed</title>\n</head>\n<body>\n  <h1>Hello EleViewer!</h1>\n  <p>Type HTML on the left and see live results on the right.</p>\n</body>\n</html>")

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Toolbar ───────────────────────────────────────────────────────
        tb_layout = QHBoxLayout()
        tb_layout.setContentsMargins(8, 4, 8, 4)
        tb_layout.setSpacing(6)

        icon_sz = QSize(self._icon_size, self._icon_size)

        self.btn_preview = self._create_btn("book-open", "Preview", "Preview Only", lambda: self.set_view_mode("preview"))
        self.btn_syntax = self._create_btn("code", "Syntax", "Syntax Only", lambda: self.set_view_mode("syntax"))
        self.btn_split = self._create_btn("layout", "Split View", "Split View (Live Feed)", lambda: self.set_view_mode("split"))

        tb_layout.addWidget(self.btn_preview)
        tb_layout.addWidget(self.btn_syntax)
        tb_layout.addWidget(self.btn_split)
        tb_layout.addStretch()

        # 🌐 Push to Web Panel button (1-Click Browser Migration)
        self.btn_push = QToolButton()
        self.btn_push.setIconSize(icon_sz)
        self.btn_push.setIcon(icon("globe", size=self._icon_size))
        self.btn_push.setText(" Push to Web Panel")
        self.btn_push.setStyleSheet(compact_toolbar_stylesheet())
        self.btn_push.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.btn_push.setToolTip("Open live HTML feed in right-hand Web Panel dock (Ctrl+Shift+B)")
        self.btn_push.clicked.connect(self._push_to_browser)
        tb_layout.addWidget(self.btn_push)

        # Shortcut for Browser Push
        QShortcut(QKeySequence("Ctrl+Shift+B"), self, self._push_to_browser)

        layout.addLayout(tb_layout)

        # ── Splitter Area ─────────────────────────────────────────────────
        p = get_active_palette()
        self.splitter = QSplitter(Qt.Horizontal, self)
        self.splitter.setStyleSheet(f"""
            QSplitter::handle {{
                background-color: {p['BRAND_BORDER']};
                width: 2px;
            }}
        """)

        # Left: Monochromatic Syntax Editor
        self.editor = QPlainTextEdit()
        self.editor.setStyleSheet(markdown_editor_stylesheet())
        self.editor.textChanged.connect(self._on_text_changed)
        self.highlighter = HtmlHighlighter(self.editor.document())

        # Right: Live Chromium Browser Preview (or fallback QTextBrowser)
        if WEB_AVAILABLE:
            self.viewer = WebViewWrapper()
        else:
            self.viewer = QTextBrowser()
            self.viewer.setOpenExternalLinks(True)
            self.viewer.setStyleSheet(f"background: {p['BRAND_BACKGROUND']}; color: {p['BRAND_PRIMARY']}; border: none; padding: 16px;")

        self.splitter.addWidget(self.editor)
        self.splitter.addWidget(self.viewer)
        layout.addWidget(self.splitter)
        self.set_view_mode(self._mode)
        self.reload_theme()

    def _create_btn(self, icon_name, text, tooltip, callback):
        btn = QToolButton()
        btn.setIconSize(QSize(self._icon_size, self._icon_size))
        btn.setIcon(icon(icon_name, size=self._icon_size))
        btn.setText(f" {text}")
        btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        btn.setStyleSheet(compact_toolbar_stylesheet())
        btn.setToolTip(tooltip)
        btn.clicked.connect(callback)
        return btn

    def reload_theme(self):
        from theme import get_active_palette, markdown_editor_stylesheet, compact_toolbar_stylesheet
        from PySide6.QtGui import QPalette, QColor, QFont
        p = get_active_palette()
        
        self.editor.setStyleSheet(markdown_editor_stylesheet())
        self.viewer.setStyleSheet(f"background: {p['BRAND_BACKGROUND']}; color: {p['BRAND_PRIMARY']}; border: none; padding: 16px;")
        
        for btn in (self.btn_preview, self.btn_syntax, self.btn_split, self.btn_push):
            btn.setStyleSheet(compact_toolbar_stylesheet())
        self._update_button_states()
        
        pal = self.editor.palette()
        pal.setColor(QPalette.Text, QColor(p['BRAND_PRIMARY']))
        self.editor.setPalette(pal)
        
        syntax_font = QFont("Consolas", 14)
        self.editor.setFont(syntax_font)
        
        if hasattr(self, 'highlighter'):
            self.highlighter._setup_formats()
            self.highlighter.rehighlight()

    def set_view_mode(self, mode):
        self._mode = mode
        if mode == "preview":
            self.editor.setVisible(False)
            self.viewer.setVisible(True)
        elif mode == "syntax":
            self.editor.setVisible(True)
            self.viewer.setVisible(False)
        elif mode == "split":
            self.editor.setVisible(True)
            self.viewer.setVisible(True)
            self.splitter.setSizes([600, 600])
        self._update_button_states()
        self._update_live_preview()

    def _update_button_states(self):
        accent = get_brand_accent()
        accent_style = f"background: {accent}; color: #ffffff; border-radius: 6px; padding: 4px 8px; font-weight: bold;"
        default_style = compact_toolbar_stylesheet()
        self.btn_preview.setStyleSheet(accent_style if self._mode == "preview" else default_style)
        self.btn_syntax.setStyleSheet(accent_style if self._mode == "syntax" else default_style)
        self.btn_split.setStyleSheet(accent_style if self._mode == "split" else default_style)

    def _on_text_changed(self):
        self.is_modified = True
        self.textChanged.emit()
        if self._mode in ("split", "preview"):
            self._debounce_timer.start()

    def _update_live_preview(self):
        text = self.editor.toPlainText()
        if WEB_AVAILABLE and isinstance(self.viewer, WebViewWrapper):
            if self.file_path and os.path.exists(self.file_path):
                base_url = QUrl.fromLocalFile(os.path.abspath(self.file_path))
            else:
                # Fallback base URL to app data dir so relative assets don't fail completely
                base_url = QUrl.fromLocalFile(str(APP_DATA_DIR) + "/")
            self.viewer.setHtml(text, base_url)
        else:
            self.viewer.setHtml(text)

    def _push_to_browser(self):
        """1-Click Browser Migration: pushes current HTML to right-hand Web Panel."""
        target_path = self.file_path
        if not target_path or not os.path.exists(target_path) or self.is_modified:
            # Create a live temp file if unsaved or modified so browser can render and reload cleanly
            temp_dir = APP_DATA_DIR / "web_live"
            temp_dir.mkdir(parents=True, exist_ok=True)
            filename = os.path.basename(self.file_path) if self.file_path else "live_feed.html"
            target_path = str(temp_dir / filename)
            try:
                with open(target_path, "w", encoding="utf-8") as f:
                    f.write(self.editor.toPlainText())
            except Exception as e:
                print(f"[HtmlViewer] Error writing live temp file for browser migration: {e}")

        url_str = QUrl.fromLocalFile(os.path.abspath(target_path)).toString()
        self.pushToBrowserRequested.emit(target_path, url_str)

    def load_from_path(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.setPlainText(content)
            self.file_path = file_path
            self.is_modified = False
        except Exception as e:
            raise Exception(f"Failed to load HTML file: {str(e)}")

    def setPlainText(self, text):
        self.editor.blockSignals(True)
        self.editor.setPlainText(text)
        self.editor.blockSignals(False)
        self._update_live_preview()
        self.is_modified = False

    def toPlainText(self):
        return self.editor.toPlainText()

    def read_current_page(self, voice_id=None):
        """Duck-typed Universal TTS (F9) method: reads plain text content of HTML."""
        raw_html = self.toPlainText()
        # Clean HTML tags to extract readable text
        clean_text = re.sub(r"<[^>]+>", " ", raw_html)
        clean_text = re.sub(r"\s+", " ", clean_text).strip()
        if not clean_text:
            return "HTML document is empty."
        preview_snip = clean_text[:300] + ("..." if len(clean_text) > 300 else "")
        return f"HTML Webpage Workstation. Text summary: {preview_snip}"

    # ── Find & Replace Compatibility ─────────────────────────────────
    def find_text(self, text, match_case=False, whole_word=False, forward=True):
        if not text:
            return False
        options = QTextDocument.FindFlags()
        if match_case:
            options |= QTextDocument.FindCaseSensitively
        if whole_word:
            options |= QTextDocument.FindWholeWords
        if not forward:
            options |= QTextDocument.FindBackward

        found = self.editor.find(text, options)
        if not found:
            cursor = self.editor.textCursor()
            cursor.movePosition(cursor.Start if forward else cursor.End)
            self.editor.setTextCursor(cursor)
            found = self.editor.find(text, options)
        return found

    def replace_text(self, find_str, replace_str, match_case=False, whole_word=False):
        cursor = self.editor.textCursor()
        if cursor.hasSelection() and cursor.selectedText() == find_str:
            cursor.insertText(replace_str)
            self.is_modified = True
        self.find_text(find_str, match_case, whole_word, True)

    def replace_all(self, find_str, replace_str, match_case=False, whole_word=False):
        if not find_str:
            return 0
        options = QTextDocument.FindFlags()
        if match_case:
            options |= QTextDocument.FindCaseSensitively
        if whole_word:
            options |= QTextDocument.FindWholeWords
        cursor = self.editor.textCursor()
        cursor.movePosition(cursor.Start)
        self.editor.setTextCursor(cursor)
        count = 0
        while self.editor.find(find_str, options):
            self.editor.textCursor().insertText(replace_str)
            count += 1
        if count > 0:
            self.is_modified = True
        return count
