import re
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QFont, QColor
from PySide6.QtCore import Qt
from theme import get_brand_accent, BRAND_MUTED, BRAND_MUTED_FG

class MarkdownHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_formats()

    def _setup_formats(self):
        accent_hex = get_brand_accent()
        accent_color = QColor(accent_hex)
        muted_color = QColor(BRAND_MUTED_FG)
        bg_muted = QColor(BRAND_MUTED)

        self.rules = []

        # Headings: # Heading
        h_format = QTextCharFormat()
        h_format.setFontWeight(QFont.Bold)
        h_format.setForeground(accent_color)
        self.rules.append((re.compile(r"^(#{1,6})\s+(.*)"), h_format))

        # Bold: **bold** or __bold__
        b_format = QTextCharFormat()
        b_format.setFontWeight(QFont.Bold)
        self.rules.append((re.compile(r"(\*\*|__)(.*?)\1"), b_format))

        # Italic: *italic* or _italic_
        i_format = QTextCharFormat()
        i_format.setFontItalic(True)
        self.rules.append((re.compile(r"(\*|_)(.*?)\1"), i_format))

        # Code: `code`
        c_format = QTextCharFormat()
        c_format.setFontFamily("Consolas")
        c_format.setBackground(bg_muted)
        c_format.setForeground(accent_color)
        self.rules.append((re.compile(r"(`)(.*?)\1"), c_format))

        # Links: [text](url)
        l_format = QTextCharFormat()
        l_format.setForeground(accent_color)
        l_format.setFontUnderline(True)
        self.rules.append((re.compile(r"\[([^\]]+)\]\([^\)]+\)"), l_format))

        # Lists: - or *
        list_format = QTextCharFormat()
        list_format.setForeground(muted_color)
        self.rules.append((re.compile(r"^(\s*[-*+]\s+)"), list_format))

        # Blockquotes: > text
        bq_format = QTextCharFormat()
        bq_format.setForeground(muted_color)
        bq_format.setFontItalic(True)
        self.rules.append((re.compile(r"^>\s+(.*)"), bq_format))

    def highlightBlock(self, text):
        for pattern, fmt in self.rules:
            for match in pattern.finditer(text):
                start = match.start()
                length = match.end() - start
                self.setFormat(start, length, fmt)
