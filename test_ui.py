import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from ui import MainWindow

app = QApplication(sys.argv)
window = MainWindow()
window.show()

def capture():
    pixmap = window.grab()
    # Save to the artifacts directory so the user can see it
    pixmap.save(r'C:\Users\kwadw\.gemini\antigravity-ide\brain\2fba3ea3-2884-4fa8-a819-2b091c44d467\scratch\ui_screenshot.png')
    app.quit()

QTimer.singleShot(1000, capture)
sys.exit(app.exec())
