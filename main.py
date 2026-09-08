import sys
import os
import logging

from PySide6.QtWidgets import QApplication, QDialog

from ui import MainWindow
from autosave import AutoSaver
from instance_lock import SingleInstanceServer

import ctypes
from PySide6.QtCore import QByteArray
from settings import load_settings
from version import APP_VERSION
logger = logging.getLogger("eleviewer")

# Set AppUserModelID so taskbar grouping and jump lists work correctly
try:
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(f"eleviewer.app.{APP_VERSION}")
except Exception as exc:
    logger.debug("Could not set Windows AppUserModelID: %s", exc)

import traceback
from datetime import datetime
import urllib.request
import json
from paths import strip_pii


def global_exception_handler(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
        
    tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
    tb_text = "".join(tb_lines)
    
    # SECURITY: Strip PII (User's home directory path) from the traceback
    tb_text = strip_pii(tb_text)

        
    # Automatic clipboard log grabber
    clipboard = QApplication.clipboard()
    if clipboard:
        clipboard.setText(f"--- EleViewer Crash Report ---\n{tb_text}")

    
    # Log exception to APP_DATA_DIR / logs / app.log
    try:
        from paths import APP_DATA_DIR
        logs_dir = APP_DATA_DIR / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        log_file = logs_dir / "app.log"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"\n--- FATAL CRASH [{datetime.now().isoformat()}] ---\n{tb_text}\n")
    except Exception:
        pass
    
    from PySide6.QtWidgets import QMessageBox
    
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setWindowTitle("EleViewer - Fatal Error")
    msg.setText("Oops! EleViewer encountered a critical error and needs to close.")
    msg.setInformativeText("To help fix this, the error log has been automatically copied to your clipboard.\n\nWould you like to send this crash report securely to the developer (No PII is included)?")
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
                headers={
                    'Content-Type': 'application/json',
                    'User-Agent': f'EleViewer/{APP_VERSION}'
                }
            )
            urllib.request.urlopen(req, timeout=5)
        except Exception as exc:
            # Fallback: open GitHub issue in default browser
            logger.warning("Crash report API failed (%s), falling back to browser", exc)
            try:
                import urllib.parse
                from PySide6.QtGui import QDesktopServices
                from PySide6.QtCore import QUrl
                title = urllib.parse.quote(f"[Bug] Fatal Crash (v{APP_VERSION})")
                body = urllib.parse.quote(
                    f"**Version**: {APP_VERSION}\n**OS**: {sys.platform}\n\n"
                    f"**Crash Log**:\n```python\n{tb_text[:2000]}\n```"
                )
                url = f"https://github.com/karefined-eng/eleviewer/issues/new?title={title}&body={body}"
                QDesktopServices.openUrl(QUrl(url))
            except Exception:
                pass
            
    sys.exit(1)

sys.excepthook = global_exception_handler

app = QApplication(sys.argv)
from branding_logo import create_eleviewer_icon
app.setWindowIcon(create_eleviewer_icon(64))

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

# If another instance tries to start with a file or new note flag, handle it in this instance
instance_server.file_opened.connect(window._open_vault_file)
instance_server.new_note_requested.connect(window.bring_to_front_and_new_note)

# If this instance was started with a file or --new flag from CLI, open it
if len(sys.argv) > 1:
    arg = sys.argv[1].strip()
    if arg in ("--new", "-n", "--new-note"):
        window.new_tab()
    elif os.path.exists(arg):
        window._open_vault_file(os.path.abspath(arg))

from PySide6.QtCore import QEventLoop, QTimer, Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtGui import QGuiApplication
from morphing_loader import GlowingLogo

splash = QWidget()
splash.setWindowFlags(Qt.SplashScreen | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
splash.setAttribute(Qt.WA_TranslucentBackground)
splash_layout = QVBoxLayout(splash)
loader = GlowingLogo(size=120)
splash_layout.addWidget(loader)
loader.start()

screen_geo = QGuiApplication.primaryScreen().geometry()
splash.move((screen_geo.width() - 120) // 2, (screen_geo.height() - 120) // 2)
splash.show()

loop = QEventLoop()
QTimer.singleShot(1500, loop.quit)
loop.exec()

splash.close()

window.show()

if not settings.get("onboarding_completed", False):
    from onboarding import OnboardingManager
    from settings import save_settings
    
    manager = OnboardingManager(window)
    manager.start()
    
    settings["onboarding_completed"] = True
    settings["last_run_version"] = APP_VERSION
    save_settings(settings)
    
    from paths import BASE_DIR
    welcome_file = BASE_DIR / "getting_started" / "Welcome to EleViewer.md"
    if welcome_file.exists():
        window.open_file(str(welcome_file))
else:
    # Check for updates to show What's New
    last_ver = settings.get("last_run_version", "0.0.0")
    if last_ver != APP_VERSION:
        from whats_new import WhatsNewDialog
        from settings import save_settings
        
        dlg = WhatsNewDialog(window, APP_VERSION)
        dlg.exec()
        
        settings["last_run_version"] = APP_VERSION
        save_settings(settings)

sys.exit(app.exec())
