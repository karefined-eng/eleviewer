import sys
from PySide6.QtWidgets import QApplication, QTabWidget, QWidget, QVBoxLayout, QPushButton
from PySide6.QtCore import Qt

app = QApplication(sys.argv)

tabs = QTabWidget()
tabs.resize(400, 300)

page1 = QWidget()
l1 = QVBoxLayout(page1)
btn1 = QPushButton("Go Fullscreen")
l1.addWidget(btn1)
tabs.addTab(page1, "Tab 1")

def toggle_fs():
    if not page1.isFullScreen():
        page1.setWindowFlag(Qt.Window, True)
        page1.showFullScreen()
    else:
        page1.setWindowFlag(Qt.Window, False)
        page1.showNormal()

btn1.clicked.connect(toggle_fs)

tabs.show()
sys.exit(app.exec())
