import sys
from PySide6.QtWidgets import QApplication, QLabel
app = QApplication(sys.argv)
label = QLabel('Hello World')
label.resize(400, 300)
label.show()
pixmap = label.grab()
pixmap.save('test_grab.png')
