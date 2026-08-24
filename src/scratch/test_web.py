import sys, traceback
from PySide6.QtWidgets import QApplication
from ui import MainWindow

try:
    app = QApplication(sys.argv)
    w = MainWindow()
    w.open_web_tab()
    print('SUCCESS')
except Exception as e:
    traceback.print_exc()
