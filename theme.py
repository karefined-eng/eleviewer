"""Centralized dark theme stylesheets for EleViewer."""

ICON_SIZE_TOOLBAR = 24
ICON_SIZE_COMPACT = 22
ICON_SIZE_MARKDOWN = 32
ICON_SIZE_VAULT_TREE = 24

MARKDOWN_ICON_SIZE_MIN = 24
MARKDOWN_ICON_SIZE_MAX = 48


def resolve_markdown_icon_size(value=None):
    """Return a clamped markdown mode-button icon size from settings or a raw value."""
    if value is None:
        from settings import load_settings
        value = load_settings().get("markdown_icon_size", ICON_SIZE_MARKDOWN)
    try:
        size = int(value)
    except (TypeError, ValueError):
        return ICON_SIZE_MARKDOWN
    return max(MARKDOWN_ICON_SIZE_MIN, min(MARKDOWN_ICON_SIZE_MAX, size))


def main_window_stylesheet():
    return """
        QMainWindow { background-color: #1e1e1e; }
        QToolBar { background-color: #252526; border-bottom: 1px solid #333; padding: 8px; spacing: 15px; }
        QToolButton { color: #e0e0e0; background-color: transparent; border: none; padding: 6px; border-radius: 4px; min-width: 28px; min-height: 28px; }
        QToolButton:hover { background-color: #3c3c3c; }
        QTabWidget::pane { border: 1px solid #333; background-color: #2d2d2d; }
        QTabBar::tab { background-color: #3c3c3c; color: #ffffff; padding: 8px 15px; margin-right: 2px; font-size: 13px; }
        QTabBar::tab:selected { background-color: #1e1e1e; font-weight: bold; }
        QTabBar::tab:!selected { margin-top: 2px; }
        QTextEdit, QPlainTextEdit { background-color: #2d2d2d; color: #e0e0e0; border: none; padding: 15px; font-family: 'Consolas', monospace; font-size: 14px; }
        QMenuBar { background-color: #1e1e1e; color: #ffffff; border-bottom: 1px solid #333; font-size: 13px; }
        QMenuBar::item { padding: 5px 10px; }
        QMenuBar::item:selected { background-color: #333; }
        QMenu { background-color: #2d2d2d; color: #ffffff; border: 1px solid #333; font-size: 13px; }
        QStatusBar { background-color: #1e1e1e; color: #aaaaaa; border-top: 1px solid #333; }
        QFileDialog { background-color: #2d2d2d; color: white; }
        QMessageBox { background-color: #2d2d2d; color: white; }
        QPushButton { background-color: #4a4a4a; color: white; border: none; padding: 5px 10px; border-radius: 4px; }
        QPushButton:hover { background-color: #5a5a5a; }
        QPushButton:pressed { background-color: #3a3a3a; }
        QDialog { background-color: #1e1e1e; color: #ffffff; }
        QLineEdit, QSpinBox, QCheckBox { color: #ffffff; }
        QLineEdit, QSpinBox { background-color: #2a2a2a; border: 1px solid #444; padding: 6px; border-radius: 3px; }
        QLabel { color: #cccccc; }
    """


def editor_stylesheet():
    return """
        QTextEdit, QPlainTextEdit {
            background: #1e1e1e;
            color: #ffffff;
            font-size: 15px;
            padding: 10px;
            border: none;
        }
    """


def viewer_header_stylesheet():
    return """
        QLabel {
            color: #888;
            font-size: 12px;
            padding: 5px;
            background: #2a2a2a;
        }
    """


def markdown_editor_stylesheet():
    return """
        QPlainTextEdit {
            background: #1e1e1e;
            color: #ffffff;
            font-size: 14px;
            padding: 10px;
            border: none;
            font-family: 'Consolas', monospace;
        }
    """


def markdown_preview_stylesheet():
    return """
        QTextBrowser {
            background: #252526;
            color: #ffffff;
            font-size: 15px;
            padding: 10px;
            border: none;
            font-family: 'Segoe UI', sans-serif;
        }
    """


MARKDOWN_PREVIEW_CSS = """
body {
    background: #252526;
    color: #e0e0e0;
    font-family: 'Segoe UI', sans-serif;
    font-size: 15px;
    line-height: 1.6;
    margin: 0;
    padding: 8px;
}
h1, h2, h3, h4 { color: #ffffff; margin-top: 1.2em; }
a { color: #6cb6ff; }
code {
    background: #1e1e1e;
    padding: 2px 6px;
    border-radius: 3px;
    font-family: Consolas, monospace;
    font-size: 13px;
}
pre {
    background: #1e1e1e;
    padding: 12px;
    border-radius: 6px;
    overflow-x: auto;
    border: 1px solid #333;
}
pre code { background: none; padding: 0; }
blockquote {
    border-left: 4px solid #555;
    margin: 0;
    padding: 4px 16px;
    color: #aaa;
}
table { border-collapse: collapse; width: 100%; margin: 12px 0; }
th, td { border: 1px solid #444; padding: 8px 12px; text-align: left; }
th { background: #333; }
tr:nth-child(even) { background: #2a2a2a; }
hr { border: none; border-top: 1px solid #444; margin: 16px 0; }
ul, ol { padding-left: 24px; }
"""


def compact_toolbar_stylesheet():
    return """
        QToolButton {
            background: transparent;
            border: none;
            padding: 4px;
            border-radius: 4px;
            min-width: 28px;
            min-height: 28px;
        }
        QToolButton:hover { background: #3c3c3c; }
    """


def xlsx_sheet_tab_stylesheet():
    return """
        QTabBar {
            background: #252526;
            border-top: 1px solid #333;
        }
        QTabBar::tab {
            background: #2d2d2d;
            color: #ccc;
            padding: 6px 16px;
            margin-right: 1px;
            border-right: 1px solid #333;
            font-size: 12px;
        }
        QTabBar::tab:selected {
            background: #1e1e1e;
            color: #fff;
            font-weight: bold;
            border-top: 2px solid #0e639c;
        }
        QTabBar::tab:hover { background: #333; }
    """
