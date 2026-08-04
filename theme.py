"""Centralized dark theme stylesheets for EleViewer."""

# Branding palettes
THEME_PALETTES = {
    "dark": {
        "BRAND_PRIMARY": "#f2f2f0",
        "BRAND_PRIMARY_FG": "#131313",
        "BRAND_BACKGROUND": "#131313",
        "BRAND_PANEL": "#1c1c1c",
        "BRAND_PANEL_2": "#242424",
        "BRAND_BORDER": "#2c2c2c",
        "BRAND_MUTED": "#232323",
        "BRAND_MUTED_FG": "#9b9b96",
        "BRAND_ERROR": "#ef4444",
        "TAB_BAR_BG": "#1a1a1a",
        "TAB_BG": "#242424",
        "TAB_HOVER": "#2a2a2a",
        "TAB_SELECTED_FG": "#ffffff",
    },
    "light": {
        "BRAND_PRIMARY": "#1c1c1c",
        "BRAND_PRIMARY_FG": "#ffffff",
        "BRAND_BACKGROUND": "#f3f3f3",
        "BRAND_PANEL": "#ffffff",
        "BRAND_PANEL_2": "#e5e5e5",
        "BRAND_BORDER": "#e5e5e5",
        "BRAND_MUTED": "#f9f9f9",
        "BRAND_MUTED_FG": "#616161",
        "BRAND_ERROR": "#d32f2f",
        "TAB_BAR_BG": "#f3f3f3",
        "TAB_BG": "#e5e5e5",
        "TAB_HOVER": "#d1d1d1",
        "TAB_SELECTED_FG": "#1c1c1c",
    }
}

# Module-level legacy aliases pointing to dark by default
BRAND_PRIMARY = THEME_PALETTES["dark"]["BRAND_PRIMARY"]
BRAND_PRIMARY_FG = THEME_PALETTES["dark"]["BRAND_PRIMARY_FG"]
BRAND_BACKGROUND = THEME_PALETTES["dark"]["BRAND_BACKGROUND"]
BRAND_PANEL = THEME_PALETTES["dark"]["BRAND_PANEL"]
BRAND_PANEL_2 = THEME_PALETTES["dark"]["BRAND_PANEL_2"]
BRAND_BORDER = THEME_PALETTES["dark"]["BRAND_BORDER"]
BRAND_MUTED = THEME_PALETTES["dark"]["BRAND_MUTED"]
BRAND_MUTED_FG = THEME_PALETTES["dark"]["BRAND_MUTED_FG"]
BRAND_ERROR = THEME_PALETTES["dark"]["BRAND_ERROR"]

THEME_ACCENTS = {
    "blue": {"accent": "#6cb6ff", "accent_fg": "#0c1826", "hover": "#7dc5ff", "pressed": "#5aa7ff"},
    "grey": {"accent": "#9b9b96", "accent_fg": "#131313", "hover": "#b5b5b0", "pressed": "#82827d"},
}

def is_system_in_light_mode():
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
        val, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
        return bool(val)
    except Exception:
        return False

def get_active_palette():
    try:
        from settings import load_settings
        mode = load_settings().get("theme_mode", "dark").lower()
        if mode == "system":
            mode = "light" if is_system_in_light_mode() else "dark"
        return THEME_PALETTES.get(mode, THEME_PALETTES["dark"])
    except Exception:
        return THEME_PALETTES["dark"]

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
    p = get_active_palette()
    accent = get_active_accent()
    return f"""
        QMainWindow {{ background-color: {p['BRAND_BACKGROUND']}; }}
        QToolBar {{ background-color: {p['BRAND_PANEL']}; border-bottom: 1px solid {p['BRAND_BORDER']}; padding: 4px 8px; spacing: 4px; }}
        QToolButton {{ color: {p['BRAND_PRIMARY']}; background-color: transparent; border: none; padding: 4px 6px; border-radius: 6px; }}
        QToolButton:hover {{ background-color: {p['BRAND_PANEL_2']}; }}
        QToolButton:pressed {{ background-color: {accent['pressed']}; color: {p['BRAND_BACKGROUND']}; }}
        QToolButton:checked {{ background-color: {accent['accent']}; color: {p['BRAND_BACKGROUND']}; }}
        QToolBar QToolButton {{ min-width: 32px; min-height: 28px; padding: 4px 8px; font-size: 12px; }}
        QTabWidget::pane {{ border: 1px solid {p['BRAND_BORDER']}; background-color: {p['BRAND_PANEL']}; }}
        QTabBar {{ background-color: {p['TAB_BAR_BG']}; border-bottom: 1px solid {p['BRAND_BORDER']}; }}
        QTabBar::tab {{ background-color: {p['TAB_BG']}; color: {p['BRAND_MUTED_FG']}; padding: 8px 18px; margin-right: 1px; font-size: 11px; font-family: 'Segoe UI', sans-serif; border-top: 2px solid transparent; border-top-left-radius: 6px; border-top-right-radius: 6px; }}
        QTabBar::tab:selected {{ background-color: {p['BRAND_BACKGROUND']}; color: {p['TAB_SELECTED_FG']}; font-weight: bold; border-top: 2px solid {accent['accent']}; }}
        QTabBar::tab:hover:!selected {{ background-color: {p['TAB_HOVER']}; color: {p['BRAND_PRIMARY']}; }}
        
        QSplitter::handle {{ background-color: transparent; }}
        QSplitter::handle:hover {{ background-color: {accent['accent']}; }}
        QSplitter::handle:horizontal {{ width: 2px; margin: 0 1px; }}
        QSplitter::handle:vertical {{ height: 2px; margin: 1px 0; }}
        QTextEdit, QPlainTextEdit {{ background-color: {p['BRAND_PANEL']}; color: {p['BRAND_PRIMARY']}; border: none; padding: 15px; font-family: 'Consolas', monospace; font-size: 14px; }}
        QMenuBar {{ background-color: {p['BRAND_BACKGROUND']}; color: {p['BRAND_PRIMARY']}; border-bottom: 1px solid {p['BRAND_BORDER']}; font-size: 13px; }}
        QMenuBar::item {{ padding: 5px 10px; }}
        QMenuBar::item:selected {{ background-color: {p['BRAND_PANEL']}; }}
        QMenu {{ background-color: {p['BRAND_PANEL']}; color: {p['BRAND_PRIMARY']}; border: 1px solid {p['BRAND_BORDER']}; font-size: 13px; }}
        QMenu::item {{ padding: 6px 60px 6px 20px; }}
        QMenu::item:selected {{ background-color: {p['BRAND_PANEL_2']}; }}
        QMenu::separator {{ height: 1px; background: {p['BRAND_MUTED']}; margin: 4px 0px; }}
        QStatusBar {{ background-color: {p['BRAND_BACKGROUND']}; color: {p['BRAND_MUTED_FG']}; border-top: 1px solid {p['BRAND_BORDER']}; }}
        QFileDialog {{ background-color: {p['BRAND_PANEL']}; color: {p['BRAND_PRIMARY']}; }}
        QMessageBox {{ background-color: {p['BRAND_PANEL']}; color: {p['BRAND_PRIMARY']}; }}
        QPushButton {{ background-color: {accent['accent']}; color: {accent['accent_fg']}; border: none; padding: 5px 10px; border-radius: 6px; font-weight: bold; }}
        QPushButton:hover {{ background-color: {accent['hover']}; opacity: 0.9; }}
        QPushButton:pressed {{ background-color: {accent['pressed']}; }}
        QDialog {{ background-color: {p['BRAND_BACKGROUND']}; color: {p['BRAND_PRIMARY']}; }}
        QLineEdit, QSpinBox, QCheckBox {{ color: {p['BRAND_PRIMARY']}; }}
        QLineEdit, QSpinBox {{ background-color: {p['BRAND_MUTED']}; border: 1px solid {p['BRAND_BORDER']}; padding: 6px; border-radius: 6px; }}
        QLabel {{ color: {p['BRAND_PRIMARY']}; }}
        QComboBox {{ background-color: {p['BRAND_PANEL']}; color: {p['BRAND_PRIMARY']}; border: 1px solid {p['BRAND_BORDER']}; padding: 5px; border-radius: 6px; }}
        QComboBox QAbstractItemView {{ background-color: {p['BRAND_PANEL']}; color: {p['BRAND_PRIMARY']}; border: 1px solid {p['BRAND_BORDER']}; selection-background-color: {accent['accent']}; selection-color: {accent['accent_fg']}; }}
        
        QScrollBar:vertical {{
            background: {p['BRAND_BACKGROUND']};
            width: 8px;
            margin: 0px;
        }}
        QScrollBar::handle:vertical {{
            background: {p['BRAND_BORDER']};
            min-height: 30px;
            border-radius: 4px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: {p['BRAND_MUTED_FG']};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: none; }}
        
        QScrollBar:horizontal {{
            background: {p['BRAND_BACKGROUND']};
            height: 8px;
            margin: 0px;
        }}
        QScrollBar::handle:horizontal {{
            background: {p['BRAND_BORDER']};
            min-width: 30px;
            border-radius: 4px;
        }}
        QScrollBar::handle:horizontal:hover {{
            background: {p['BRAND_MUTED_FG']};
        }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0px; }}
        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{ background: none; }}
    """


def editor_stylesheet():
    p = get_active_palette()
    return f"""
        QTextEdit, QPlainTextEdit {{
            background: {p['BRAND_BACKGROUND']};
            color: {p['BRAND_PRIMARY']};
            font-size: 15px;
            padding: 10px;
            border: none;
        }}
    """


def viewer_header_stylesheet():
    p = get_active_palette()
    return f"""
        QLabel {{
            color: {p['BRAND_MUTED_FG']};
            font-size: 12px;
            padding: 5px;
            background: {p['BRAND_MUTED']};
        }}
    """


def markdown_editor_stylesheet():
    p = get_active_palette()
    return f"""
        QPlainTextEdit {{
            background: {p['BRAND_BACKGROUND']};
            padding: 10px;
            border: none;
        }}
    """


def markdown_preview_stylesheet():
    p = get_active_palette()
    return f"""
        QTextBrowser {{
            background: {p['BRAND_PANEL']};
            color: {p['BRAND_PRIMARY']};
            font-size: 15px;
            padding: 10px;
            border: none;
            font-family: 'Segoe UI', sans-serif;
        }}
    """


def markdown_preview_css():
    p = get_active_palette()
    accent = get_active_accent()
    return f"""
body {{
    background: {p['BRAND_PANEL']};
    color: {p['BRAND_PRIMARY']};
    font-family: 'Segoe UI', sans-serif;
    font-size: 15px;
    line-height: 1.6;
    margin: 0;
    padding: 8px;
}}
h1, h2, h3, h4 {{ color: {p['BRAND_PRIMARY']}; margin-top: 1.2em; }}
a {{ color: {accent['accent']}; }}
code {{
    background: {p['BRAND_BACKGROUND']};
    padding: 2px 6px;
    border-radius: 3px;
    font-family: Consolas, monospace;
    font-size: 13px;
}}
pre {{
    background: {p['BRAND_BACKGROUND']};
    padding: 12px;
    border-radius: 6px;
    overflow-x: auto;
    border: 1px solid {p['BRAND_BORDER']};
}}
pre code {{ background: none; padding: 0; }}
blockquote {{
    border-left: 4px solid {accent['accent']};
    margin: 0;
    padding: 4px 16px;
    color: {p['BRAND_MUTED_FG']};
}}
table {{ border-collapse: collapse; width: 100%; margin: 12px 0; }}
th, td {{ border: 1px solid {p['BRAND_BORDER']}; padding: 8px 12px; text-align: left; }}
th {{ background: {p['BRAND_PANEL_2']}; }}
tr:nth-child(even) {{ background: {p['BRAND_MUTED']}; }}
hr {{ border: none; border-top: 1px solid {p['BRAND_BORDER']}; margin: 16px 0; }}
ul, ol {{ padding-left: 24px; }}
"""


def compact_toolbar_stylesheet():
    p = get_active_palette()
    return f"""
        QToolButton {{
            background: transparent;
            border: none;
            padding: 4px;
            border-radius: 6px;
            min-width: 28px;
            min-height: 28px;
        }}
        QToolButton:hover {{ background: {p['BRAND_PANEL_2']}; }}
        QToolButton:pressed {{ background: {get_active_accent()['pressed']}; color: {p['BRAND_BACKGROUND']}; }}
        QToolButton:checked {{ background: {get_active_accent()['accent']}; color: {p['BRAND_BACKGROUND']}; }}
    """


def xlsx_sheet_tab_stylesheet():
    p = get_active_palette()
    accent = get_active_accent()
    return f"""
        QTabBar {{
            background: {p['BRAND_PANEL']};
            border-top: 1px solid {p['BRAND_BORDER']};
        }}
        QTabBar::tab {{
            background: {p['BRAND_PANEL_2']};
            color: {p['BRAND_MUTED_FG']};
            padding: 6px 16px;
            margin-right: 1px;
            border-right: 1px solid {p['BRAND_BORDER']};
            font-size: 12px;
        }}
        QTabBar::tab:selected {{
            background: {p['BRAND_BACKGROUND']};
            color: {p['BRAND_PRIMARY']};
            font-weight: bold;
            border-top: 2px solid {accent['accent']};
        }}
        QTabBar::tab:hover {{ background: {p['BRAND_MUTED']}; }}
    """
