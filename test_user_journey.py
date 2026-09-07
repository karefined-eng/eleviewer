import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from settings import DEFAULT_SETTINGS

app = QApplication.instance() or QApplication(sys.argv)

def test_playground_teaches_first_actions():
    playground = Path(__file__).parent / "getting_started" / "Playground.md"
    assert playground.exists(), "Playground.md should exist"
    
    text = playground.read_text(encoding="utf-8")
    
    # Check that the interactive tasks are present
    assert "Alt+E" in text  # Global Quick Note
    assert "Ctrl+D" in text # Bookmark
    assert "Ctrl+T" in text # Split-screen web panel
    assert "Ctrl + +" in text or "Ctrl++" in text # Zoom web


def test_fresh_session_defaults_to_the_welcome_screen():
    assert DEFAULT_SETTINGS["fresh_session_behavior"] == "welcome"
