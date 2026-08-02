from theme import THEME_PALETTES, get_active_palette, main_window_stylesheet
from settings import DEFAULT_SETTINGS

def test_theme_palettes_exist():
    assert "dark" in THEME_PALETTES
    assert "light" in THEME_PALETTES
    assert THEME_PALETTES["light"]["BRAND_BACKGROUND"] == "#f3f3f3"

def test_theme_mode_default():
    assert DEFAULT_SETTINGS.get("theme_mode") == "dark"
    palette = get_active_palette()
    assert palette["BRAND_BACKGROUND"] in ("#131313", "#f3f3f3", "#f8f9fa")

def test_main_window_stylesheet_generation():
    qss = main_window_stylesheet()
    assert "QMainWindow" in qss
    assert "QToolBar" in qss
