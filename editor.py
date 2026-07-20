from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QToolButton, QTextEdit, QMenu, QSizePolicy
)
from PySide6.QtCore import Signal, QSize, Qt
from PySide6.QtGui import QAction, QTextDocument

from icons import icon
from theme import editor_stylesheet, compact_toolbar_stylesheet, resolve_markdown_icon_size
from settings import load_settings, save_settings


class EditorTab(QWidget):
    textChanged = Signal()

    def __init__(self):
        super().__init__()
        self.file_path = None
        self.is_modified = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Toolbar ─────────────────────────────────────────────────
        self.toolbar_widget = QWidget()
        toolbar = QHBoxLayout(self.toolbar_widget)
        toolbar.setContentsMargins(4, 4, 4, 4)
        toolbar.setSpacing(2)

        icon_sz = resolve_markdown_icon_size()
        self._icon_size = icon_sz
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
            toolbar.addWidget(w)
            
        toolbar.addStretch()
        toolbar.addWidget(self.btn_pin)

        # ── Toggle button (Chevron) ─────────────────────────────────
        self.toggle_layout = QHBoxLayout()
        self.toggle_layout.setContentsMargins(0, 0, 4, 0)
        self.btn_toggle = _tb("chevron-down", "Toggle Formatting Toolbar", self._on_toggle_clicked)
        self.toggle_layout.addStretch()
        self.toggle_layout.addWidget(self.btn_toggle)

        # Initial visibility based on pin state
        self.toolbar_widget.setVisible(is_pinned)
        self.btn_toggle.setVisible(not is_pinned)

        # ── Editor ──────────────────────────────────────────────────
        self.editor = QTextEdit()
        self.editor.setStyleSheet(editor_stylesheet())
        self.editor.textChanged.connect(self._on_text_changed)

        layout.addWidget(self.toolbar_widget)
        layout.addLayout(self.toggle_layout)
        layout.addWidget(self.editor)

    def _is_html(self):
        return self.file_path and self.file_path.lower().endswith((".html", ".htm"))

    # ── Actions ──────────────────────────────────────────────────

    def _on_heading_clicked(self, level):
        cursor = self.editor.textCursor()
        cursor.movePosition(cursor.StartOfBlock)
        if self._is_html():
            # Very basic HTML heading insertion - wraps current block
            cursor.movePosition(cursor.EndOfBlock, cursor.KeepAnchor)
            text = cursor.selectedText()
            cursor.insertText(f"<h{level}>{text}</h{level}>")
        else:
            cursor.insertText(("#" * level) + " ")
        self.editor.setFocus()

    def _on_list_clicked(self, list_type):
        cursor = self.editor.textCursor()
        cursor.movePosition(cursor.StartOfBlock)
        if self._is_html():
            tag = "ul" if list_type == "bullet" else "ol"
            cursor.insertText(f"<{tag}>\n  <li></li>\n</{tag}>\n")
            cursor.movePosition(cursor.Up)
            cursor.movePosition(cursor.EndOfLine)
        else:
            prefix = "* " if list_type == "bullet" else "1. "
            cursor.insertText(prefix)
        self.editor.setTextCursor(cursor)
        self.editor.setFocus()

    def _on_bold_clicked(self):
        prefix, suffix = ("<b>", "</b>") if self._is_html() else ("**", "**")
        self._insert_format(prefix, suffix)

    def _on_italic_clicked(self):
        prefix, suffix = ("<i>", "</i>") if self._is_html() else ("*", "*")
        self._insert_format(prefix, suffix)

    def _on_underline_clicked(self):
        prefix, suffix = ("<u>", "</u>")
        self._insert_format(prefix, suffix)

    def _on_strike_clicked(self):
        prefix, suffix = ("<s>", "</s>") if self._is_html() else ("~~", "~~")
        self._insert_format(prefix, suffix)

    def _on_link_clicked(self):
        if self._is_html():
            self._insert_format('<a href="">', '</a>')
        else:
            self._insert_format("[", "](url)")

    def _on_table_clicked(self, rows, cols):
        cursor = self.editor.textCursor()
        if self._is_html():
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
        self.editor.setFocus()

    def _on_clear_clicked(self):
        cursor = self.editor.textCursor()
        if not cursor.hasSelection():
            return
        text = cursor.selectedText()
        if self._is_html():
            import re
            text = re.sub(r'<[^>]+>', '', text)
        else:
            # Strip basic markdown
            text = text.replace("**", "").replace("__", "")
            text = text.replace("*", "").replace("_", "")
            text = text.replace("~~", "")
            text = text.replace("<u>", "").replace("</u>", "")
            # Removing links [text](url) -> text
            import re
            text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
            # Remove heading hashes if at start
            text = re.sub(r'^#{1,6}\s+', '', text)
        
        cursor.insertText(text)
        self.editor.setFocus()

    def _insert_format(self, prefix, suffix):
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            text = cursor.selectedText()
            cursor.insertText(f"{prefix}{text}{suffix}")
        else:
            pos = cursor.position()
            cursor.insertText(f"{prefix}{suffix}")
            cursor.setPosition(pos + len(prefix))
            self.editor.setTextCursor(cursor)
        self.editor.setFocus()

    # ── UI toggles ──────────────────────────────────────────────────

    def _on_toggle_clicked(self):
        is_vis = self.toolbar_widget.isVisible()
        self.toolbar_widget.setVisible(not is_vis)

    def _on_pin_toggled(self, checked):
        save_settings({"formatting_toolbar_pinned": checked})
        self._update_pin_icon()
        if checked:
            self.toolbar_widget.setVisible(True)
            self.btn_toggle.setVisible(False)
        else:
            self.btn_toggle.setVisible(True)

    def _update_pin_icon(self):
        checked = self.btn_pin.isChecked()
        icon_name = "pin" if checked else "pin-off"
        self.btn_pin.setIcon(icon(icon_name, size=self._icon_size))
        self.btn_pin.setToolTip("Unpin Toolbar" if checked else "Pin Toolbar")

    # ── Standard interface ──────────────────────────────────────────

    def _on_text_changed(self):
        self.is_modified = True
        self.textChanged.emit()

    def setPlainText(self, text):
        self.editor.blockSignals(True)
        self.editor.setPlainText(text)
        self.editor.blockSignals(False)
        self.is_modified = False

    def toPlainText(self):
        return self.editor.toPlainText()

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
        
        # Wrap around if not found
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
            cursor = self.editor.textCursor()
            cursor.insertText(replace_str)
            count += 1

        if count > 0:
            self.is_modified = True
        return count

