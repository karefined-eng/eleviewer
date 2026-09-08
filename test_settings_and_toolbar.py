import sys
import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from settings_dialog import SettingsDialog
from settings import load_settings, save_settings, DEFAULT_SETTINGS
from ui import MainWindow


app = QApplication.instance() or QApplication(sys.argv)


def test_settings_dialog_tabs_and_controls():
    from PySide6.QtWidgets import QTabWidget
    dialog = SettingsDialog()
    tab_widget = dialog.findChild(QTabWidget)
    assert tab_widget is not None
    assert tab_widget.count() == 6
    titles = [tab_widget.tabText(i) for i in range(tab_widget.count())]
    assert "Startup & Defaults" in titles
    assert "Text Editing" in titles
    assert "PDF Reading" in titles
    assert "Web Browser Panel" in titles
    assert "Audio & Read Aloud" in titles
    assert "Folders & Organization" in titles
    
    # Check that the 6 tabs exist
    tab_count = 0
    from PySide6.QtWidgets import QTabWidget
    for child in dialog.children():
        if isinstance(child, QTabWidget):
            tab_count = child.count()
            titles = [child.tabText(i) for i in range(child.count())]
            assert "Startup & Defaults" in titles
            assert "Text Editing" in titles
            assert "PDF Reading" in titles
            assert "Web Browser Panel" in titles
            assert "Audio & Read Aloud" in titles
            assert "Folders & Organization" in titles
            break
    assert tab_count == 6

    # Check key controls
    assert hasattr(dialog, "toolbar_style_combo")
    assert dialog.toolbar_style_combo.findData("text_under_icon") >= 0
    assert dialog.toolbar_style_combo.findData("icon_only") >= 0
    assert dialog.toolbar_style_combo.findData("text_beside_icon") >= 0

    assert hasattr(dialog, "download_folder_input")
    assert hasattr(dialog, "web_default_zoom_combo")
    assert hasattr(dialog, "tts_engine_combo")
    assert hasattr(dialog, "tts_speed_combo")
    assert hasattr(dialog, "editor_font_spin")
    assert hasattr(dialog, "pdf_default_zoom_combo")

    dialog.close()
    dialog.deleteLater()
    app.processEvents()


def test_toolbar_style_switching():
    # Ensure default is icon_only
    settings = load_settings()
    settings["toolbar_button_style"] = "icon_only"
    save_settings(settings)

    window = MainWindow()
    assert window.toolbar.toolButtonStyle() == Qt.ToolButtonIconOnly

    # Switch to text_under_icon
    settings["toolbar_button_style"] = "text_under_icon"
    save_settings(settings)
    window._apply_toolbar_style()
    assert window.toolbar.toolButtonStyle() == Qt.ToolButtonTextUnderIcon

    # Switch back to icon_only
    settings["toolbar_button_style"] = "icon_only"
    save_settings(settings)
    window._apply_toolbar_style()
    assert window.toolbar.toolButtonStyle() == Qt.ToolButtonIconOnly

    window.close()
    window.deleteLater()
    app.processEvents()
