import sys, os
from PySide6.QtWidgets import QApplication
from ui import MainWindow

if not QApplication.instance():
    app = QApplication(sys.argv)
else:
    app = QApplication.instance()

from settings import save_settings
save_settings({"show_toolbar": False, "toolbar_button_style": "icon_only"}) 

win = MainWindow()
win.resize(1000, 800)
win.show()

from PySide6.QtCore import QTimer
def capture():
    pixmap = win.grab()
    pixmap.save("test_welcome_no_toolbar_fixed.png")
    app.quit()

QTimer.singleShot(1500, capture)
app.exec()
