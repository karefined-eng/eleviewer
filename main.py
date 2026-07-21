import sys
import os

from PySide6.QtWidgets import QApplication

from ui import MainWindow
from autosave import AutoSaver
from instance_lock import SingleInstanceServer

APP_VERSION = "1.2.0"

app = QApplication(sys.argv)

# Attempt to lock single instance
instance_server = SingleInstanceServer()
if not instance_server.try_to_start():
    # Another instance is already running and we successfully sent our sys.argv to it.
    print("Another instance is running. Passing file arguments and exiting.")
    sys.exit(0)

window = MainWindow()
window.autosaver = AutoSaver(window)

# If another instance tries to start with a file, open it in this instance
instance_server.file_opened.connect(window._open_vault_file)

# If this instance was started with a file from the command line, open it
if len(sys.argv) > 1:
    file_path = os.path.abspath(sys.argv[1])
    if os.path.exists(file_path):
        window._open_vault_file(file_path)

window.show()

sys.exit(app.exec())
