import sys

from PySide6.QtWidgets import QApplication, QStatusBar

from onboarding import OnboardingManager
from settings_dialog import SettingsDialog


app = QApplication.instance() or QApplication(sys.argv)

from PySide6.QtCore import QObject

class MockWebPanel:
    def isVisible(self):
        return False

class MockWindow(QObject):
    def __init__(self):
        super().__init__()
        self._status_bar = QStatusBar()
        self.web_panel = MockWebPanel()
        
    def statusBar(self):
        return self._status_bar
        
    def toggle_web_panel(self):
        pass
        
    def _open_vault_file(self, path):
        pass
        
    def open_scratchpad(self):
        pass
        
    def _add_bookmark_from_editor(self, editor, data):
        pass


def test_onboarding_manager_hooks_actions():
    window = MockWindow()
    manager = OnboardingManager(window)
    
    manager.start()
    
    # Test that hooking works
    assert manager.note_opened is False
    window.open_scratchpad()
    assert manager.note_opened is True

    assert manager.bookmark_added is False
    window._add_bookmark_from_editor(None, None)
    assert manager.bookmark_added is True
    
    # Check that Web Panel gets "opened" (at least flag sets if we call toggle again)
    assert manager.web_opened is False
    # Mocking isVisible to return True to simulate it being open
    window.web_panel.isVisible = lambda: True
    window.toggle_web_panel()
    assert manager.web_opened is True


def test_startup_settings_store_readable_labels_as_internal_values():
    dialog = SettingsDialog()

    assert dialog.launch_combo.itemText(0) == "Use my last window size"
    assert dialog.launch_combo.itemData(0) == "remembered"
    assert dialog.fresh_session_combo.itemText(0) == "Show the welcome screen"
    assert dialog.fresh_session_combo.itemData(0) == "welcome"
    dialog.close()
    dialog.deleteLater()
    app.processEvents()
