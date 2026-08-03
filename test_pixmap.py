import os
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
import sys

app = QApplication(sys.argv)
base = os.path.dirname(os.path.abspath('branding_logo.py'))
icon_path = os.path.join(base, "icons", "eleviewer.ico")
icon = QIcon(icon_path)
pix = icon.pixmap(64, 64)
print(f"Pixmap IsNull: {pix.isNull()}")
