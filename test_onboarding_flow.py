import sys

from PySide6.QtWidgets import QApplication

from onboarding import OnboardingDialog
from settings_dialog import SettingsDialog


app = QApplication.instance() or QApplication(sys.argv)


def test_onboarding_ends_with_two_clear_first_actions():
    dialog = OnboardingDialog()

    for _ in range(dialog.stack.count() - 1):
        dialog._next()

    assert dialog.stack.currentIndex() == dialog.stack.count() - 1
    assert dialog.sample_btn.text() == "Try the Sample Note"
    assert dialog.open_file_btn.text() == "Open My File"
    assert dialog.next_btn.text() == "Finish"


def test_startup_settings_store_readable_labels_as_internal_values():
    dialog = SettingsDialog()

    assert dialog.launch_combo.itemText(0) == "Use my last window size"
    assert dialog.launch_combo.itemData(0) == "remembered"
    assert dialog.fresh_session_combo.itemText(0) == "Show the welcome screen"
    assert dialog.fresh_session_combo.itemData(0) == "welcome"
