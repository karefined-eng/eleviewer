from theme import THEME_PALETTES, get_active_palette, main_window_stylesheet, xlsx_sheet_tab_stylesheet
from settings import DEFAULT_SETTINGS

def test_theme_palettes_exist():
    assert "dark" in THEME_PALETTES
    assert "light" in THEME_PALETTES
    assert THEME_PALETTES["light"]["BRAND_BACKGROUND"] == "#f3f3f3"

def test_theme_mode_default():
    assert DEFAULT_SETTINGS.get("theme_mode") == "dark"
    palette = get_active_palette()
    assert palette["BRAND_BACKGROUND"] in ("#131313", "#f8f9fa")

def test_main_window_stylesheet_generation():
    qss = main_window_stylesheet()
    assert "QMainWindow" in qss
    assert "QToolBar" in qss

def test_close_button_icon_matches_theme(monkeypatch):
    """The × must load a stroke colour baked per theme: QSS renders
    stroke="currentColor" SVGs black, invisible on the dark tab bar."""
    from icons import ICONS_DIR
    monkeypatch.setattr("theme.get_active_theme_name", lambda: "dark")
    dark_qss = main_window_stylesheet()
    assert f'url("{(ICONS_DIR / "x-bright.svg").as_posix()}")' in dark_qss

    monkeypatch.setattr("theme.get_active_theme_name", lambda: "light")
    light_qss = main_window_stylesheet()
    assert f'url("{(ICONS_DIR / "x-dark.svg").as_posix()}")' in light_qss

    # The old hover-reveal rules used `opacity` and a child selector, which
    # Qt QSS silently ignores — they must not come back.
    assert "QTabBar::tab:selected > QTabBar::close-button" not in dark_qss


def test_xlsx_tabs_follow_active_theme(monkeypatch):
    monkeypatch.setattr("theme.get_active_theme_name", lambda: "light")
    light_qss = xlsx_sheet_tab_stylesheet()
    assert THEME_PALETTES["light"]["BRAND_PANEL"] in light_qss
    assert THEME_PALETTES["light"]["BRAND_BACKGROUND"] in light_qss

def test_show_toolbar_default():
    assert DEFAULT_SETTINGS.get("show_toolbar") is True

def test_show_toolbar_preference_persists(tmp_path, monkeypatch):
    """A user's saved toolbar preference must survive load_settings — the
    toolbar may be hidden permanently (distraction-free mode)."""
    import settings as settings_mod
    fake = tmp_path / "settings.json"
    fake.write_text('{"show_toolbar": false}', encoding="utf-8")
    monkeypatch.setattr(settings_mod, "SETTINGS_FILE_PATH", fake)
    assert settings_mod.load_settings()["show_toolbar"] is False
