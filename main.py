import sys
import os

from PySide6.QtWidgets import QApplication

from ui import MainWindow
from autosave import AutoSaver
from instance_lock import SingleInstanceServer

import ctypes
from PySide6.QtCore import QByteArray
from settings import load_settings

APP_VERSION = "1.3.0"

# Set AppUserModelID so taskbar grouping and jump lists work correctly
try:
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(f"eleviewer.app.{APP_VERSION}")
except Exception:
    pass

import traceback
def global_exception_handler(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
        
    tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
    tb_text = "".join(tb_lines)
    
    from PySide6.QtWidgets import QMessageBox
    import urllib.request
    import json
    
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setWindowTitle("EleViewer - Fatal Error")
    msg.setText("Oops! EleViewer encountered a critical error and needs to close.")
    msg.setInformativeText("Would you like to send this crash report securely to the developer so it can be fixed?")
    msg.setDetailedText(tb_text)
    
    send_btn = msg.addButton("Send Report", QMessageBox.ActionRole)
    msg.addButton("Close App", QMessageBox.RejectRole)
    msg.setDefaultButton(send_btn)
    
    msg.exec()
    
    if msg.clickedButton() == send_btn:
        try:
            data = {
                "type": "Bug",
                "description": f"**FATAL CRASH**\n\n```python\n{tb_text}\n```",
                "version": APP_VERSION,
                "os_name": os.name,
                "platform": sys.platform
            }
            req = urllib.request.Request(
                "https://eleviewer.vercel.app/api/feedback", 
                data=json.dumps(data).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            urllib.request.urlopen(req, timeout=5)
        except Exception:
            pass
            
    sys.exit(1)

sys.excepthook = global_exception_handler

app = QApplication(sys.argv)

# Attempt to lock single instance
instance_server = SingleInstanceServer()
if not instance_server.try_to_start():
    # Another instance is already running and we successfully sent our sys.argv to it.
    print("Another instance is running. Passing file arguments and exiting.")
    sys.exit(0)

window = MainWindow()

settings = load_settings()
launch_behavior = settings.get("launch_behavior", "remembered")
if launch_behavior == "remembered" and settings.get("window_geometry"):
    window.restoreGeometry(QByteArray.fromBase64(settings["window_geometry"].encode()))
elif launch_behavior == "maximized":
    window.showMaximized()

window.autosaver = AutoSaver(window)

# If another instance tries to start with a file, open it in this instance
instance_server.file_opened.connect(window._open_vault_file)

# If this instance was started with a file from the command line, open it
if len(sys.argv) > 1:
    file_path = os.path.abspath(sys.argv[1])
    if os.path.exists(file_path):
        window._open_vault_file(file_path)

window.show()

if not settings.get("onboarding_completed", False):
    from onboarding import OnboardingDialog
    from settings import save_settings
    from pathlib import Path
    
    dlg = OnboardingDialog(window)
    dlg.exec()
    
    settings["onboarding_completed"] = True
    save_settings(settings)
    
    welcome_file = Path("getting_started/Welcome to EleViewer.md").absolute()
    if welcome_file.exists():
        window.open_file(str(welcome_file))

sys.exit(app.exec())
