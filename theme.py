"""Centralized dark theme stylesheets for EleViewer."""

# Branding colors from site
BRAND_PRIMARY = "#f2f2f0"  # Light off-white
BRAND_PRIMARY_FG = "#131313"
BRAND_BACKGROUND = "#131313"  # Dark black
BRAND_PANEL = "#1c1c1c"    # Dark panel
BRAND_PANEL_2 = "#242424"  # Lighter dark panel
BRAND_BORDER = "#2c2c2c"   # Border
BRAND_MUTED = "#232323"    # Muted background
BRAND_MUTED_FG = "#9b9b96" # Gray text

THEME_ACCENTS = {
    "blue": {"accent": "#6cb6ff", "accent_fg": "#0c1826", "hover": "#7dc5ff", "pressed": "#5aa7ff"},
    "grey": {"accent": "#9b9b96", "accent_fg": "#131313", "hover": "#b5b5b0", "pressed": "#82827d"},
}

def get_active_accent():
    try:
        from settings import load_settings
        settings = load_settings()
        theme_accent = settings.get("theme_accent", "blue")
        return THEME_ACCENTS.get(theme_accent, THEME_ACCENTS["blue"])
    except Exception:
        return THEME_ACCENTS["blue"]

def get_brand_accent():
    return get_active_accent()["accent"]

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
    accent = get_active_accent()
    return f"""
        QMainWindow {{ background-color: {BRAND_BACKGROUND}; }}
        QToolBar {{ background-color: {BRAND_PANEL}; border-bottom: 1px solid {BRAND_BORDER}; padding: 8px; spacing: 15px; }}
        QToolButton {{ color: {BRAND_PRIMARY}; background-color: transparent; border: none; padding: 6px; border-radius: 4px; min-width: 28px; min-height: 28px; }}
        QToolButton:hover {{ background-color: {BRAND_PANEL_2}; }}
        QToolButton:pressed {{ background-color: {accent['pressed']}; color: {BRAND_BACKGROUND}; }}
        QToolButton:checked {{ background-color: {accent['accent']}; color: {BRAND_BACKGROUND}; }}
        QToolBar QToolButton {{ min-width: 70px; min-height: 52px; font-size: 11px; }}
        QTabWidget::pane {{ border: 1px solid {BRAND_BORDER}; background-color: {BRAND_PANEL}; }}
        QTabBar {{ background-color: #252526; border-bottom: 1px solid {BRAND_BORDER}; }}
        QTabBar::tab {{ background-color: #2d2d2d; color: #999999; padding: 7px 14px; margin-right: 1px; font-size: 12px; font-family: 'Consolas', 'Segoe UI', monospace; border-top: 2px solid transparent; }}
        QTabBar::tab:selected {{ background-color: {BRAND_BACKGROUND}; color: #ffffff; font-weight: bold; border-top: 2px solid {accent['accent']}; }}
        QTabBar::tab:hover:!selected {{ background-color: #333333; color: #e0e0e0; }}
        QTextEdit, QPlainTextEdit {{ background-color: {BRAND_PANEL}; color: {BRAND_PRIMARY}; border: none; padding: 15px; font-family: 'Consolas', monospace; font-size: 14px; }}
        QMenuBar {{ background-color: {BRAND_BACKGROUND}; color: {BRAND_PRIMARY}; border-bottom: 1px solid {BRAND_BORDER}; font-size: 13px; }}
        QMenuBar::item {{ padding: 5px 10px; }}
        QMenuBar::item:selected {{ background-color: {BRAND_PANEL}; }}
        QMenu {{ background-color: {BRAND_PANEL}; color: {BRAND_PRIMARY}; border: 1px solid {BRAND_BORDER}; font-size: 13px; }}
        QMenu::item {{ padding: 6px 60px 6px 20px; }}
        QMenu::item:selected {{ background-color: {BRAND_PANEL_2}; }}
        QMenu::separator {{ height: 1px; background: {BRAND_MUTED}; margin: 4px 0px; }}
        QStatusBar {{ background-color: {BRAND_BACKGROUND}; color: {BRAND_MUTED_FG}; border-top: 1px solid {BRAND_BORDER}; }}
        QFileDialog {{ background-color: {BRAND_PANEL}; color: {BRAND_PRIMARY}; }}
        QMessageBox {{ background-color: {BRAND_PANEL}; color: {BRAND_PRIMARY}; }}
        QPushButton {{ background-color: {accent['accent']}; color: {BRAND_BACKGROUND}; border: none; padding: 5px 10px; border-radius: 4px; font-weight: bold; }}
        QPushButton:hover {{ background-color: {accent['hover']}; opacity: 0.9; }}
        QPushButton:pressed {{ background-color: {accent['pressed']}; }}
        QDialog {{ background-color: {BRAND_BACKGROUND}; color: {BRAND_PRIMARY}; }}
        QLineEdit, QSpinBox, QCheckBox {{ color: {BRAND_PRIMARY}; }}
        QLineEdit, QSpinBox {{ background-color: {BRAND_MUTED}; border: 1px solid {BRAND_BORDER}; padding: 6px; border-radius: 3px; }}
        QLabel {{ color: {BRAND_PRIMARY}; }}
    """


def editor_stylesheet():
    return f"""
        QTextEdit, QPlainTextEdit {{
            background: {BRAND_BACKGROUND};
            color: {BRAND_PRIMARY};
            font-size: 15px;
            padding: 10px;
            border: none;
        }}
    """


def viewer_header_stylesheet():
    return f"""
        QLabel {{
            color: {BRAND_MUTED_FG};
            font-size: 12px;
            padding: 5px;
            background: {BRAND_MUTED};
        }}
    """


def markdown_editor_stylesheet():
    return f"""
        QPlainTextEdit {{
            background: {BRAND_BACKGROUND};
            color: {BRAND_PRIMARY};
            font-size: 14px;
            padding: 10px;
            border: none;
            font-family: 'Consolas', monospace;
        }}
    """


def markdown_preview_stylesheet():
    return f"""
        QTextBrowser {{
            background: {BRAND_PANEL};
            color: {BRAND_PRIMARY};
            font-size: 15px;
            padding: 10px;
            border: none;
            font-family: 'Segoe UI', sans-serif;
        }}
    """


def markdown_preview_css():
    accent = get_active_accent()
    return f"""
body {{
    background: {BRAND_PANEL};
    color: {BRAND_PRIMARY};
    font-family: 'Segoe UI', sans-serif;
    font-size: 15px;
    line-height: 1.6;
    margin: 0;
    padding: 8px;
}}
h1, h2, h3, h4 {{ color: {BRAND_PRIMARY}; margin-top: 1.2em; }}
a {{ color: {accent['accent']}; }}
code {{
    background: {BRAND_BACKGROUND};
    padding: 2px 6px;
    border-radius: 3px;
    font-family: Consolas, monospace;
    font-size: 13px;
}}
pre {{
    background: {BRAND_BACKGROUND};
    padding: 12px;
    border-radius: 6px;
    overflow-x: auto;
    border: 1px solid {BRAND_BORDER};
}}
pre code {{ background: none; padding: 0; }}
blockquote {{
    border-left: 4px solid {accent['accent']};
    margin: 0;
    padding: 4px 16px;
    color: {BRAND_MUTED_FG};
}}
table {{ border-collapse: collapse; width: 100%; margin: 12px 0; }}
th, td {{ border: 1px solid {BRAND_BORDER}; padding: 8px 12px; text-align: left; }}
th {{ background: {BRAND_PANEL_2}; }}
tr:nth-child(even) {{ background: {BRAND_MUTED}; }}
hr {{ border: none; border-top: 1px solid {BRAND_BORDER}; margin: 16px 0; }}
ul, ol {{ padding-left: 24px; }}
"""


def compact_toolbar_stylesheet():
    return f"""
        QToolButton {{
            background: transparent;
            border: none;
            padding: 4px;
            border-radius: 4px;
            min-width: 28px;
            min-height: 28px;
        }}
        QToolButton:hover {{ background: {BRAND_PANEL_2}; }}
        QToolButton:pressed {{ background: {get_active_accent()['pressed']}; color: {BRAND_BACKGROUND}; }}
        QToolButton:checked {{ background: {get_active_accent()['accent']}; color: {BRAND_BACKGROUND}; }}
    """


def xlsx_sheet_tab_stylesheet():
    accent = get_active_accent()
    return f"""
        QTabBar {{
            background: {BRAND_PANEL};
            border-top: 1px solid {BRAND_BORDER};
        }}
        QTabBar::tab {{
            background: {BRAND_PANEL_2};
            color: {BRAND_MUTED_FG};
            padding: 6px 16px;
            margin-right: 1px;
            border-right: 1px solid {BRAND_BORDER};
            font-size: 12px;
        }}
        QTabBar::tab:selected {{
            background: {BRAND_BACKGROUND};
            color: {BRAND_PRIMARY};
            font-weight: bold;
            border-top: 2px solid {accent['accent']};
        }}
        QTabBar::tab:hover {{ background: {BRAND_MUTED}; }}
    """
