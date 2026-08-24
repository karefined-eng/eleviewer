import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from onboarding import OnboardingDialog
from settings import DEFAULT_SETTINGS

app = QApplication.instance() or QApplication(sys.argv)


def test_first_run_onboarding_has_real_first_actions():
    dialog = OnboardingDialog()
    assert dialog.windowTitle() == "Start studying with EleViewer"

    for _ in range(dialog.stack.count() - 1):
        dialog._next()

    assert dialog.stack.currentIndex() == dialog.stack.count() - 1
    assert dialog.sample_btn.text() == "Try the Sample Note"
    assert dialog.open_file_btn.text() == "Open My File"
    assert dialog.next_btn.text() == "Finish"


def test_sample_note_teaches_the_same_first_actions_as_the_onboarding():
    sample = Path(__file__).parent / "getting_started" / "sample_notes.md"
    text = sample.read_text(encoding="utf-8")
    assert "Ctrl+O" in text
    assert "F9" in text
    assert "Alt+V" in text


def test_fresh_session_defaults_to_the_welcome_screen():
    assert DEFAULT_SETTINGS["fresh_session_behavior"] == "welcome"
