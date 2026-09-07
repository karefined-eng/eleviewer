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

def get_active_theme_name():
    """Return 'dark' or 'light' after resolving the 'system' setting."""
    try:
        from settings import load_settings
        mode = load_settings().get("theme_mode", "dark").lower()
        if mode == "system":
            mode = "light" if is_system_in_light_mode() else "dark"
        return mode if mode in ("dark", "light") else "dark"
    except Exception:
        return "dark"

def get_active_palette():
    return THEME_PALETTES.get(get_active_theme_name(), THEME_PALETTES["dark"])

def get_active_accent():
    try:
        from settings import load_settings
        settings = load_settings()
        theme_accent = settings.get("theme_accent", "grey")
        return THEME_ACCENTS.get(theme_accent, THEME_ACCENTS["grey"])
    except Exception:
        return THEME_ACCENTS["grey"]

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
    is_dark = get_active_theme_name() == "dark"
    from icons import ICONS_DIR
    close_icon = ICONS_DIR / ("x-bright.svg" if is_dark else "x-dark.svg")
    # Subtle gradient for the toolbar: two very close shades for depth
    tb_top = "#1e1e1e" if is_dark else "#fafafa"
    tb_bot = "#191919" if is_dark else "#f0f0f0"
    return f"""
        QMainWindow {{ background-color: {p['BRAND_BACKGROUND']}; }}

        /* ── Toolbar ─────────────────────────────────────────── */
        QToolBar {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {tb_top}, stop:1 {tb_bot});
            border: none;
            border-bottom: 1px solid {p['BRAND_BORDER']};
            padding: 4px 8px;
            spacing: 2px;
        }}
        QToolButton {{
            color: {p['BRAND_PRIMARY']};
            background-color: transparent;
            border: none;
            padding: 5px 6px;
            border-radius: 8px;
            min-width: 24px;
            min-height: 24px;
        }}
        QToolButton:hover {{ background-color: {p['BRAND_PANEL_2']}; }}
        QToolButton:pressed {{ background-color: {accent['pressed']}; color: {p['BRAND_BACKGROUND']}; }}
        QToolButton:checked {{ background-color: {accent['accent']}; color: {p['BRAND_BACKGROUND']}; }}
        QToolBar QToolButton {{
            color: {p['BRAND_PRIMARY']};
            border: none;
            border-radius: 6px;
            padding: 4px 6px;
            min-width: 54px;
            min-height: 50px;
            font-size: 11px;
            font-family: 'Segoe UI', -apple-system, sans-serif;
            text-align: center;
        }}

        /* ── Tabs ────────────────────────────────────────────── */
        QTabWidget::pane {{
            border: none;
            border-top: 1px solid {p['BRAND_BORDER']};
            background-color: {p['BRAND_PANEL']};
        }}
        QTabBar {{
            background-color: {p['TAB_BAR_BG']};
            border-bottom: 1px solid {p['BRAND_BORDER']};
            qproperty-drawBase: 0;
        }}
        QTabBar::tab {{
            background-color: transparent;
            color: {p['BRAND_MUTED_FG']};
            padding: 6px 16px;
            margin: 3px 1px 0px 1px;
            font-size: 11px;
            font-family: 'Segoe UI', sans-serif;
            border-radius: 8px;
            border: none;
            min-width: 64px;
        }}
        QTabBar::tab:selected {{
            background-color: {p['BRAND_PANEL_2']};
            color: {p['TAB_SELECTED_FG']};
            font-weight: 600;
            border-bottom: 2px solid {accent['accent']};
            border-radius: 8px;
        }}
        QTabBar::tab:hover:!selected {{
            background-color: {p['TAB_HOVER']};
            color: {p['BRAND_PRIMARY']};
            border-radius: 8px;
        }}
        QTabBar::close-button {{
            image: url("{close_icon.as_posix()}");
            subcontrol-position: right;
            width: 10px;
            height: 10px;
            border-radius: 4px;
            padding: 2px;
            margin-left: 4px;
        }}
        QTabBar::close-button:hover {{ background-color: {p['BRAND_BORDER']}; }}
        QTabBar QToolButton {{
            background-color: {p['TAB_BAR_BG']};
            border: none;
            padding: 2px;
            min-width: 16px;
            min-height: 16px;
        }}
        QTabBar QToolButton:hover {{
            background-color: {p['TAB_HOVER']};
            border-radius: 4px;
        }}

        /* ── Editors ─────────────────────────────────────────── */
        QTextEdit, QPlainTextEdit {{
            background-color: {p['BRAND_PANEL']};
            color: {p['BRAND_PRIMARY']};
            border: none;
            padding: 15px;
            font-family: 'Consolas', monospace;
            font-size: 14px;
        }}

        /* ── Menu bar ────────────────────────────────────────── */
        QMenuBar {{
            background-color: {p['BRAND_BACKGROUND']};
            color: {p['BRAND_PRIMARY']};
            border-bottom: 1px solid {p['BRAND_BORDER']};
            font-size: 13px;
            font-family: 'Segoe UI', sans-serif;
            padding: 2px 4px;
        }}
        QMenuBar::item {{ padding: 5px 10px; border-radius: 5px; }}
        QMenuBar::item:selected {{ background-color: {p['BRAND_PANEL']}; }}
        QMenu {{
            background-color: {p['BRAND_PANEL']};
            color: {p['BRAND_PRIMARY']};
            border: 1px solid {p['BRAND_BORDER']};
            border-radius: 10px;
            padding: 4px;
            font-size: 13px;
        }}
        QMenu::item {{ padding: 7px 48px 7px 18px; border-radius: 6px; }}
        QMenu::item:selected {{ background-color: {p['BRAND_PANEL_2']}; }}
        QMenu::separator {{ height: 1px; background: {p['BRAND_BORDER']}; margin: 4px 8px; }}

        /* ── Status bar ──────────────────────────────────────── */
        QStatusBar {{
            background-color: {p['BRAND_BACKGROUND']};
            color: {p['BRAND_MUTED_FG']};
            border-top: 1px solid {p['BRAND_BORDER']};
            padding: 2px 8px;
            font-size: 11px;
        }}

        /* ── Dialogs / message boxes ─────────────────────────── */
        QFileDialog {{ background-color: {p['BRAND_PANEL']}; color: {p['BRAND_PRIMARY']}; }}
        QMessageBox {{ background-color: {p['BRAND_PANEL']}; color: {p['BRAND_PRIMARY']}; }}
        QDialog {{ background-color: {p['BRAND_BACKGROUND']}; color: {p['BRAND_PRIMARY']}; }}

        /* ── Buttons ─────────────────────────────────────────── */
        QPushButton {{
            background-color: {accent['accent']};
            color: {accent['accent_fg']};
            border: none;
            padding: 7px 14px;
            border-radius: 8px;
            font-weight: 600;
            font-size: 12px;
            letter-spacing: 0.2px;
        }}
        QPushButton:hover {{ background-color: {accent['hover']}; }}
        QPushButton:pressed {{ background-color: {accent['pressed']}; }}

        /* ── Labels ──────────────────────────────────────────── */
        QLabel {{ color: {p['BRAND_PRIMARY']}; }}

        /* ── Inputs ──────────────────────────────────────────── */
        QLineEdit, QSpinBox, QCheckBox {{ color: {p['BRAND_PRIMARY']}; }}
        QLineEdit, QSpinBox {{
            background-color: {p['BRAND_MUTED']};
            border: 1px solid {p['BRAND_BORDER']};
            padding: 7px 10px;
            border-radius: 8px;
            font-size: 13px;
        }}
        QLineEdit:focus, QSpinBox:focus {{
            border: 1px solid {accent['accent']};
        }}
        QComboBox {{
            background-color: {p['BRAND_PANEL']};
            color: {p['BRAND_PRIMARY']};
            border: 1px solid {p['BRAND_BORDER']};
            padding: 6px 10px;
            border-radius: 8px;
        }}
        QComboBox QAbstractItemView {{
            background-color: {p['BRAND_PANEL']};
            color: {p['BRAND_PRIMARY']};
            border: 1px solid {p['BRAND_BORDER']};
            border-radius: 8px;
            selection-background-color: {accent['accent']};
            selection-color: {accent['accent_fg']};
        }}

        /* ── Tooltips ────────────────────────────────────────── */
        QToolTip {{
            background-color: {p['BRAND_PANEL']};
            color: {p['BRAND_PRIMARY']};
            border: 1px solid {p['BRAND_BORDER']};
            padding: 6px 10px;
            border-radius: 6px;
            font-family: 'Segoe UI', sans-serif;
            font-size: 12px;
        }}

        /* ── Scrollbars (macOS-style thin bars) ──────────────── */
        QScrollBar:vertical {{
            background: transparent;
            width: 8px;
            margin: 0px;
        }}
        QScrollBar::handle:vertical {{
            background: {p['BRAND_MUTED_FG']};
            min-height: 24px;
            border-radius: 4px;
            margin: 1px 2px;
        }}
        QScrollBar::handle:vertical:hover {{ background: {accent['accent']}; }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: none; }}

        QScrollBar:horizontal {{
            background: transparent;
            height: 8px;
            margin: 0px;
        }}
        QScrollBar::handle:horizontal {{
            background: {p['BRAND_MUTED_FG']};
            min-width: 24px;
            border-radius: 4px;
            margin: 2px 1px;
        }}
        QScrollBar::handle:horizontal:hover {{ background: {accent['accent']}; }}
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
            color: {p['BRAND_PRIMARY']};
            font-size: 14px;
            padding: 10px;
            border: none;
            font-family: 'Consolas', monospace;
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
            min-width: 24px;
            min-height: 24px;
        }}
        QToolButton:hover {{ background: {p['BRAND_PANEL_2']}; }}
        QToolButton:pressed {{ background: {get_active_accent()['pressed']}; color: {p['BRAND_BACKGROUND']}; }}
        QToolButton:checked {{ background: {get_active_accent()['accent']}; color: {p['BRAND_BACKGROUND']}; }}
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
