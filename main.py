import sys
import os

from PySide6.QtWidgets import QApplication

from ui import MainWindow
from autosave import AutoSaver
from instance_lock import SingleInstanceServer

import ctypes
from PySide6.QtCore import QByteArray
from settings import load_settings

if len(sys.argv) > 1 and sys.argv[1] == "--webview-worker":
    import webview_worker
    webview_worker.main()
    sys.exit(0)

APP_VERSION = "1.3.1"

# Set AppUserModelID so taskbar grouping and jump lists work correctly
try:
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(f"eleviewer.app.{APP_VERSION}")
except Exception:
    pass

# Create a Win32 Mutex so Inno Setup (SetupMutex=EleViewerMutex) can detect and close running instances
_win_mutex = None
try:
    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
    _win_mutex = kernel32.CreateMutexW(None, False, "EleViewerMutex")
except Exception:
    pass

import traceback
from datetime import datetime
import urllib.request
import json
from paths import strip_pii


def _show_crash_dialog_on_main_thread(tb_text):
    # Automatic clipboard log grabber (safe on GUI thread)
    try:
        clipboard = QApplication.clipboard()
        if clipboard:
            clipboard.setText(f"--- EleViewer Crash Report ---\n{tb_text}")
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
                headers={'Content-Type': 'application/json'}
            )
            urllib.request.urlopen(req, timeout=5)
        except Exception:
            pass
            
    sys.exit(1)


def global_exception_handler(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
        
    tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
    tb_text = "".join(tb_lines)
    
    # SECURITY: Strip PII (User's home directory path) from the traceback
    tb_text = strip_pii(tb_text)

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

    app = QApplication.instance()
    from PySide6.QtCore import QThread, QMetaObject, Qt
    if app and QThread.currentThread() != app.thread():
        QMetaObject.invokeMethod(
            app,
            lambda: _show_crash_dialog_on_main_thread(tb_text),
            Qt.QueuedConnection
        )
    else:
        _show_crash_dialog_on_main_thread(tb_text)

sys.excepthook = global_exception_handler

# Hardware acceleration toggle must be applied before QApplication starts
settings = load_settings()
_chromium_flags = [
    "--process-per-site",          # one renderer process shared across same-origin pages (saves ~100-200MB)
    "--disable-background-networking",  # no background prefetch/update pings
    "--disable-sync",              # no Chrome sync overhead
    "--no-first-run",              # skip first-run setup checks
    "--disable-extensions",        # no extension host process
]
if not settings.get("hardware_acceleration_enabled", True):
    _chromium_flags.append("--disable-gpu")
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = " ".join(_chromium_flags)

# Suppress Chromium renderer font-size noise (harmless QFont::setPointSize(-1) on web font init)
os.environ.setdefault("QT_LOGGING_RULES", "qt.qpa.fonts.warning=false")

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

window.show()

if not settings.get("onboarding_completed", False):
    window.start_onboarding()
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
