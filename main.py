import sys

from PySide6.QtWidgets import QApplication

from ui import MainWindow
from autosave import AutoSaver


app = QApplication(sys.argv)

window = MainWindow()

# START AUTOSAVE SYSTEM
autosave = AutoSaver(window)

window.show()

sys.exit(app.exec())