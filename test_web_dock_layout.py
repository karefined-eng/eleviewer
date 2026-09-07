import sys
from PySide6.QtWidgets import QApplication, QWidget, QToolButton
from PySide6.QtCore import Qt
from ui import MainWindow


def test_web_dock_header_and_layout():
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()

    # The dock must not exist before the web panel is first opened
    assert window._web_dock is None
    window.open_web_tab()

    dock = window._web_dock
    assert dock is not None, "Web dock was not created!"

    # The "WEB BROWSER" title row is gone: the title bar widget is empty
    title_bar = dock.titleBarWidget()
    assert title_bar is not None, "setTitleBarWidget was not called"
    assert not title_bar.layout() and title_bar.findChildren(QWidget) == [], \
        "Dock title bar should be an empty widget"

    # Dock controls merged into the web panel's navigation row
    web_panel = dock.widget()
    assert hasattr(web_panel, "nav_layout"), "WebPanel must expose its nav row"
    dock_buttons = []
    for i in range(web_panel.nav_layout.count()):
        widget = web_panel.nav_layout.itemAt(i).widget()
        if isinstance(widget, QToolButton):
            dock_buttons.append(widget)
    # 5 web nav buttons + maximize / pop out / close appended after a separator
    assert len(dock_buttons) == 8, f"Expected 8 buttons in nav row, got {len(dock_buttons)}"
    assert dock_buttons[-3:] == list(window._web_dock_buttons), \
        "Dock controls must be the last three buttons of the nav row"
    assert all(not btn.icon().isNull() for btn in dock_buttons), \
        "All nav buttons must have real icons"

    # Hit the roof: the right dock area owns the top-right corner
    assert window.corner(Qt.TopRightCorner) == Qt.RightDockWidgetArea

    # Toolbar toggle flips visibility, syncs the View menu action and persists
    from settings import load_settings, save_settings
    original_show_toolbar = load_settings().get("show_toolbar", True)
    try:
        was_hidden = window.toolbar.isHidden()
        window.toggle_main_toolbar()
        assert window.toolbar.isHidden() != was_hidden
        assert window.action_toggle_toolbar.isChecked() == (not window.toolbar.isHidden())
    finally:
        s = load_settings()
        s["show_toolbar"] = original_show_toolbar
        save_settings(s)

    window._quitting = True
    window.close()
