import sys

from PySide6.QtWidgets import QApplication

from ui import MainWindow
from autosave import AutoSaver

app = QApplication(sys.argv)

window = MainWindow()
window.autosaver = AutoSaver(window)

window.show()

sys.exit(app.exec())
