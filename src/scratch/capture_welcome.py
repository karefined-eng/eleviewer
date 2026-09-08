wimport sys, os
from PySide6.QtWidgets import QApplication, QMainWindow
from ui import MainWindow

app = QApplication(sys.argv)
from settings import save_settings
save_settings({"show_toolbar": False}) # force toolbar off

win = MainWindow()
win.resize(1000, 800)
win.show()

# Give it a moment to render, then grab
from PySide6.QtCore import QTimer
def capture():
    pixmap = win.grab()
    pixmap.save("test_welcome_no_toolbar.png")
    app.quit()

QTimer.singleShot(1000, capture)
app.exec()
