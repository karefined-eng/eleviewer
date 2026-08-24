import os
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
import sys

app = QApplication(sys.argv)
base = os.path.dirname(os.path.abspath('branding_logo.py'))
icon_path = os.path.join(base, "icons", "eleviewer.ico")
print(f"Path: {icon_path}")
print(f"Exists: {os.path.exists(icon_path)}")
icon = QIcon(icon_path)
print(f"IsNull: {icon.isNull()}")
