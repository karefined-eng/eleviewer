from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QStackedWidget,
    QPlainTextEdit, QTextBrowser, QToolButton, QHBoxLayout, QLabel, QMenu
)
from PySide6.QtCore import Signal, Qt, QEvent, QTimer, QSize, QObject
from PySide6.QtGui import QMouseEvent, QAction, QTextDocument
import markdown
import re

from icons import icon
from markdown_utils import markdown_to_simple, simple_to_markdown
from settings import load_settings, save_settings
from theme import (
    markdown_editor_stylesheet, MARKDOWN_PREVIEW_CSS, compact_toolbar_stylesheet,
    resolve_markdown_icon_size, markdown_preview_stylesheet, BRAND_PANEL, BRAND_PRIMARY, BRAND_MUTED_FG
)

MODE_VIEW = 0
MODE_SIMPLE = 1
MODE_SYNTAX = 2


class PreviewEventFilter(QObject):
    """Detect double/triple click on preview to switch edit modes."""

    def __init__(self, viewer):
        super().__init__()
        self._viewer = viewer
        self._click_count = 0
        self._click_timer = QTimer()
        self._click_timer.setSingleShot(True)
        self._click_timer.setInterval(300)
        self._click_timer.timeout.connect(self._on_timeout)

    def eventFilter(self, obj, event):
        if event.type() in (QEvent.MouseButtonPress, QEvent.MouseButtonDblClick) and isinstance(event, QMouseEvent):
            if event.button() == Qt.LeftButton:
                if not self._click_timer.isActive():
                    self._click_count = 0

                if event.type() == QEvent.MouseButtonDblClick:
                    self._click_count = max(self._click_count + 1, 2)
                else:
                    self._click_count += 1

                self._click_timer.start()

                if self._click_count >= 3:
                    self._viewer.enter_syntax_mode()
                    self._reset_clicks()
            return False
        return False

    def _on_timeout(self):
        if self._click_count == 2:
            if self._viewer.is_html:
                self._viewer.enter_syntax_mode()
            else:
                self._viewer.enter_simple_mode()
        self._click_count = 0

    def _reset_clicks(self):
        self._click_count = 0
        self._click_timer.stop()


class MarkdownViewer(QWidget):
    textChanged = Signal()

    def __init__(self, file_path=None, is_html=False):
        super().__init__()
        self.file_path = file_path
        self.is_html = is_html or (file_path and file_path.lower().endswith((".html", ".htm")))
        self.is_modified = False
        self._mode = MODE_VIEW
        self._icon_size = resolve_markdown_icon_size()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Toolbar ─────────────────────────────────────────────────
        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(8, 4, 8, 0)

        hint_text = "Double-click to edit source · Click 📖 to preview" if self.is_html else "Double-click to edit · Triple-click for syntax"
        self.hint = QLabel(hint_text)
        self.hint.setStyleSheet(f"color: {BRAND_MUTED_FG}; font-size: 11px;")
        toolbar.addWidget(self.hint)

        self.formatting_widget = QWidget()
        fmt_layout = QHBoxLayout(self.formatting_widget)
        fmt_layout.setContentsMargins(0, 0, 0, 0)
        fmt_layout.setSpacing(2)

        icon_sz = self._icon_size
        icon_qsize = QSize(icon_sz, icon_sz)

        def _tb(icon_name, tooltip, slot=None):
            btn = QToolButton()
            btn.setIconSize(icon_qsize)
            btn.setIcon(icon(icon_name, size=icon_sz))
            btn.setToolTip(tooltip)
            btn.setStyleSheet(compact_toolbar_stylesheet())
            btn.setAutoRaise(True)
            if slot:
                btn.clicked.connect(slot)
            return btn

        # Heading dropdown
        self.btn_h = _tb("type", "Heading")
        self.btn_h.setPopupMode(QToolButton.InstantPopup)
        h_menu = QMenu(self.btn_h)
        for i in range(1, 7):
            action = QAction(f"Heading {i}", self)
            action.triggered.connect(lambda checked=False, level=i: self._on_heading_clicked(level))
            h_menu.addAction(action)
        self.btn_h.setMenu(h_menu)

        # Direct list buttons
        self.btn_bullet = _tb("list", "Bullet List", lambda: self._on_list_clicked("bullet"))
        self.btn_numbered = _tb("list-ordered", "Numbered List", lambda: self._on_list_clicked("numbered"))

        self.btn_bold = _tb("bold", "Bold", self._on_bold_clicked)
        self.btn_italic = _tb("italic", "Italic", self._on_italic_clicked)
        self.btn_underline = _tb("underline", "Underline", self._on_underline_clicked)
        self.btn_strike = _tb("strikethrough", "Strikethrough", self._on_strike_clicked)
        self.btn_link = _tb("link", "Link", self._on_link_clicked)
        
        # Table dropdown
        self.btn_table = _tb("table", "Table")
        self.btn_table.setPopupMode(QToolButton.InstantPopup)
        tbl_menu = QMenu(self.btn_table)
        tbl_2x2 = QAction("Insert 2x2 Table", self)
        tbl_2x2.triggered.connect(lambda: self._on_table_clicked(2, 2))
        tbl_menu.addAction(tbl_2x2)
        tbl_3x3 = QAction("Insert 3x3 Table", self)
        tbl_3x3.triggered.connect(lambda: self._on_table_clicked(3, 3))
        tbl_menu.addAction(tbl_3x3)
        self.btn_table.setMenu(tbl_menu)

        self.btn_clear = _tb("eraser", "Clear Formatting", self._on_clear_clicked)

        # Pin button
        self.btn_pin = _tb("pin", "Pin Toolbar", self._on_pin_toggled)
        self.btn_pin.setCheckable(True)
        is_pinned = load_settings().get("formatting_toolbar_pinned", False)
        self.btn_pin.setChecked(is_pinned)
        self._update_pin_icon()

        for w in (self.btn_h, self.btn_bullet, self.btn_numbered, self.btn_bold, self.btn_italic,
                  self.btn_underline, self.btn_strike, self.btn_link, self.btn_table, self.btn_clear):
            fmt_layout.addWidget(w)
            
        fmt_layout.addStretch()
        fmt_layout.addWidget(self.btn_pin)

        toolbar.addWidget(self.formatting_widget)
        self.formatting_widget.setVisible(is_pinned)

        # Toggle button
        self.btn_toggle = _tb("chevron-down", "Toggle Formatting Toolbar", self._on_toggle_clicked)
        self.btn_toggle.setVisible(not is_pinned)
        toolbar.addWidget(self.btn_toggle)

        toolbar.addStretch()

        self.mode_btn = _tb("pencil", "Toggle Mode", self._toggle_syntax_from_view)
        toolbar.addWidget(self.mode_btn)

        # ── Editor Stack ─────────────────────────────────────────────
        self.stack = QStackedWidget()

        try:
            from web_panel import WebViewWrapper, WEB_AVAILABLE
        except ImportError:
            WEB_AVAILABLE = False

        if self.is_html and WEB_AVAILABLE:
            self.viewer = WebViewWrapper()
            self._preview_filter = PreviewEventFilter(self)
            self.viewer.installEventFilter(self._preview_filter)
            for child in self.viewer.findChildren(QWidget):
                child.installEventFilter(self._preview_filter)
        else:
            self.viewer = QTextBrowser()
            self.viewer.setStyleSheet(markdown_preview_stylesheet())
            self.viewer.setOpenExternalLinks(True)
            self._preview_filter = PreviewEventFilter(self)
            self.viewer.viewport().installEventFilter(self._preview_filter)

        self.simple_editor = QPlainTextEdit()
        self.simple_editor.setStyleSheet(f"""
            QPlainTextEdit {{
                background: {BRAND_PANEL};
                color: {BRAND_PRIMARY};
                font-size: 15px;
                padding: 16px;
                border: none;
                font-family: 'Segoe UI', sans-serif;
                line-height: 1.6;
            }}
        """)
        self.simple_editor.textChanged.connect(self._on_simple_changed)

        self.editor = QPlainTextEdit()
        self.editor.setStyleSheet(markdown_editor_stylesheet())
        self.editor.textChanged.connect(self._on_syntax_changed)

        self.stack.addWidget(self.viewer)
        self.stack.addWidget(self.simple_editor)
        self.stack.addWidget(self.editor)

        layout.addLayout(toolbar)
        layout.addWidget(self.stack)

        if file_path:
            self.load_from_path(file_path)
        else:
            self.enter_view_mode()

    # ── Formatting Actions ───────────────────────────────────────────

    def _current_edit_widget(self):
        if self._mode == MODE_SIMPLE:
            return self.simple_editor
        elif self._mode == MODE_SYNTAX:
            return self.editor
        return None

    def _on_heading_clicked(self, level):
        ed = self._current_edit_widget()
        if not ed: return
        cursor = ed.textCursor()
        cursor.movePosition(cursor.StartOfBlock)
        if self.is_html:
            cursor.movePosition(cursor.EndOfBlock, cursor.KeepAnchor)
            text = cursor.selectedText()
            cursor.insertText(f"<h{level}>{text}</h{level}>")
        else:
            cursor.insertText(("#" * level) + " ")
        ed.setFocus()

    def _on_list_clicked(self, list_type):
        ed = self._current_edit_widget()
        if not ed: return
        cursor = ed.textCursor()
        cursor.movePosition(cursor.StartOfBlock)
        if self.is_html:
            tag = "ul" if list_type == "bullet" else "ol"
            cursor.insertText(f"<{tag}>\n  <li></li>\n</{tag}>\n")
            cursor.movePosition(cursor.Up)
            cursor.movePosition(cursor.EndOfLine)
        else:
            prefix = "* " if list_type == "bullet" else "1. "
            cursor.insertText(prefix)
        ed.setTextCursor(cursor)
        ed.setFocus()

    def _on_bold_clicked(self):
        ed = self._current_edit_widget()
        if ed:
            prefix, suffix = ("<b>", "</b>") if self.is_html else ("**", "**")
            self._insert_format(ed, prefix, suffix)

    def _on_italic_clicked(self):
        ed = self._current_edit_widget()
        if ed:
            prefix, suffix = ("<i>", "</i>") if self.is_html else ("*", "*")
            self._insert_format(ed, prefix, suffix)

    def _on_underline_clicked(self):
        ed = self._current_edit_widget()
        if ed:
            prefix, suffix = ("<u>", "</u>")
            self._insert_format(ed, prefix, suffix)

    def _on_strike_clicked(self):
        ed = self._current_edit_widget()
        if ed:
            prefix, suffix = ("<s>", "</s>") if self.is_html else ("~~", "~~")
            self._insert_format(ed, prefix, suffix)

    def _on_link_clicked(self):
        ed = self._current_edit_widget()
        if ed:
            if self.is_html:
                self._insert_format(ed, '<a href="">', '</a>')
            else:
                self._insert_format(ed, "[", "](url)")

    def _on_table_clicked(self, rows, cols):
        ed = self._current_edit_widget()
        if not ed: return
        cursor = ed.textCursor()
        if self.is_html:
            tbl = "\n<table border='1'>\n"
            for r in range(rows):
                tbl += "  <tr>\n"
                for c in range(cols):
                    if r == 0:
                        tbl += f"    <th>H{c+1}</th>\n"
                    else:
                        tbl += f"    <td>C{c+1}</td>\n"
                tbl += "  </tr>\n"
            tbl += "</table>\n"
        else:
            tbl = "\n|" + "|".join([f" H{c+1} " for c in range(cols)]) + "|\n"
            tbl += "|" + "|".join(["---" for _ in range(cols)]) + "|\n"
            for r in range(1, rows):
                tbl += "|" + "|".join([f" C{c+1} " for c in range(cols)]) + "|\n"
            tbl += "\n"
        cursor.insertText(tbl)
        ed.setFocus()

    def _on_clear_clicked(self):
        ed = self._current_edit_widget()
        if not ed: return
        cursor = ed.textCursor()
        if not cursor.hasSelection():
            return
        text = cursor.selectedText()
        if self.is_html:
            text = re.sub(r'<[^>]+>', '', text)
        else:
            text = text.replace("**", "").replace("__", "")
            text = text.replace("*", "").replace("_", "")
            text = text.replace("~~", "")
            text = text.replace("<u>", "").replace("</u>", "")
            text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
            text = re.sub(r'^#{1,6}\s+', '', text)
        cursor.insertText(text)
        ed.setFocus()

    def _insert_format(self, editor, prefix, suffix):
        cursor = editor.textCursor()
        if cursor.hasSelection():
            text = cursor.selectedText()
            cursor.insertText(f"{prefix}{text}{suffix}")
        else:
            pos = cursor.position()
            cursor.insertText(f"{prefix}{suffix}")
            cursor.setPosition(pos + len(prefix))
            editor.setTextCursor(cursor)
        editor.setFocus()

    # ── UI toggles ──────────────────────────────────────────────────

    def _on_toggle_clicked(self):
        is_vis = self.formatting_widget.isVisible()
        self.formatting_widget.setVisible(not is_vis)

    def _on_pin_toggled(self, checked):
        save_settings({"formatting_toolbar_pinned": checked})
        self._update_pin_icon()
        if checked:
            self.formatting_widget.setVisible(True)
            self.btn_toggle.setVisible(False)
        elif self._mode != MODE_VIEW:
            self.btn_toggle.setVisible(True)

    def _update_pin_icon(self):
        checked = self.btn_pin.isChecked()
        icon_name = "pin" if checked else "pin-off"
        self.btn_pin.setIcon(icon(icon_name, size=self._icon_size))
        self.btn_pin.setToolTip("Unpin Toolbar" if checked else "Pin Toolbar")

    # ── Core Modes ───────────────────────────────────────────────────

    def _render_markdown(self, text):
        if self.is_html:
            return text
        html_body = markdown.markdown(
            text,
            extensions=["tables", "fenced_code", "nl2br", "sane_lists"],
        )
        return f"<html><head><style>{MARKDOWN_PREVIEW_CSS}</style></head><body>{html_body}</body></html>"

    def _sync_from_syntax(self):
        text = self.editor.toPlainText()
        if not self.is_html:
            self.simple_editor.blockSignals(True)
            self.simple_editor.setPlainText(markdown_to_simple(text))
            self.simple_editor.blockSignals(False)
        self.viewer.setHtml(self._render_markdown(text))

    def enter_view_mode(self):
        self._sync_from_syntax()
        self._mode = MODE_VIEW
        self.stack.setCurrentIndex(MODE_VIEW)
        self.hint.setVisible(True)
        if not self.btn_pin.isChecked():
            self.formatting_widget.setVisible(False)
            self.btn_toggle.setVisible(False)
        self._update_mode_button()

    def enter_simple_mode(self):
        if self.is_html:
            return
        if self._mode == MODE_VIEW:
            self.simple_editor.setPlainText(markdown_to_simple(self.editor.toPlainText()))
        self._mode = MODE_SIMPLE
        self.stack.setCurrentIndex(MODE_SIMPLE)
        self.hint.setVisible(False)
        if not self.btn_pin.isChecked():
            self.formatting_widget.setVisible(True)
            self.btn_toggle.setVisible(True)
        self._update_mode_button()

    def enter_syntax_mode(self):
        if self._mode == MODE_SIMPLE and not self.is_html:
            self.editor.setPlainText(simple_to_markdown(self.simple_editor.toPlainText()))
        self._mode = MODE_SYNTAX
        self.stack.setCurrentIndex(MODE_SYNTAX)
        self.hint.setVisible(False)
        if not self.btn_pin.isChecked():
            self.formatting_widget.setVisible(True)
            self.btn_toggle.setVisible(True)
        self._update_mode_button()

    def _toggle_syntax_from_view(self):
        if self._mode == MODE_VIEW:
            self.enter_syntax_mode()
        else:
            self.enter_view_mode()

    def _update_mode_button(self):
        size = resolve_markdown_icon_size()
        self._icon_size = size
        self.mode_btn.setIconSize(QSize(size, size))
        if self._mode == MODE_VIEW:
            self.mode_btn.setIcon(icon("pencil", size=size))
            self.mode_btn.setToolTip("Switch to edit mode")
        else:
            self.mode_btn.setIcon(icon("book-open", size=size))
            self.mode_btn.setToolTip("Switch to view mode")

    def load_from_path(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.setPlainText(content)
            if self.is_html:
                self.enter_view_mode()
            else:
                default = load_settings().get("markdown_default_mode", "view")
                if default == "syntax":
                    self.enter_syntax_mode()
                elif default == "simple":
                    self.enter_simple_mode()
                else:
                    self.enter_view_mode()
            self.is_modified = False
        except Exception as e:
            raise Exception(f"Failed to load: {str(e)}")

    def _on_syntax_changed(self):
        self.is_modified = True
        self.textChanged.emit()

    def _on_simple_changed(self):
        if self.is_html:
            return
        self.editor.blockSignals(True)
        self.editor.setPlainText(simple_to_markdown(self.simple_editor.toPlainText()))
        self.editor.blockSignals(False)
        self.is_modified = True
        self.textChanged.emit()

    def toPlainText(self):
        if self._mode == MODE_SIMPLE and not self.is_html:
            return simple_to_markdown(self.simple_editor.toPlainText())
        return self.editor.toPlainText()

    def setPlainText(self, text):
        self.editor.blockSignals(True)
        self.simple_editor.blockSignals(True)
        self.editor.setPlainText(text)
        if not self.is_html:
            self.simple_editor.setPlainText(markdown_to_simple(text))
        self.viewer.setHtml(self._render_markdown(text))
        self.editor.blockSignals(False)
        self.simple_editor.blockSignals(False)
        self.is_modified = False

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

        active = self._get_active_widget()
        found = active.find(text, options)
        
        if not found:
            cursor = active.textCursor()
            cursor.movePosition(cursor.Start if forward else cursor.End)
            active.setTextCursor(cursor)
            found = active.find(text, options)
            
        return found

    def replace_text(self, find_str, replace_str, match_case=False, whole_word=False):
        if self._mode == MODE_VIEW:
            return # Read-only
            
        active = self._get_active_widget()
        cursor = active.textCursor()
        if cursor.hasSelection() and cursor.selectedText() == find_str:
            cursor.insertText(replace_str)
            self.is_modified = True
            
        self.find_text(find_str, match_case, whole_word, True)

    def replace_all(self, find_str, replace_str, match_case=False, whole_word=False):
        if not find_str or self._mode == MODE_VIEW:
            return 0
            
        options = QTextDocument.FindFlags()
        if match_case:
            options |= QTextDocument.FindCaseSensitively
        if whole_word:
            options |= QTextDocument.FindWholeWords

        active = self._get_active_widget()
        cursor = active.textCursor()
        cursor.movePosition(cursor.Start)
        active.setTextCursor(cursor)

        count = 0
        while active.find(find_str, options):
            cursor = active.textCursor()
            cursor.insertText(replace_str)
            count += 1

        if count > 0:
            self.is_modified = True
            
        return count
