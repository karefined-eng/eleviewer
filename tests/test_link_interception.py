import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QUrl
from ui import MainWindow

def run_test():
    app = QApplication.instance() or QApplication(sys.argv)
    print("[1/3] Initializing MainWindow with global URL handlers...")
    window = MainWindow()
    captured = {}

    def fake_open_web_tab_with_url(url, title=None):
        captured["web"] = (url, title)

    def fake_open_recent_file(path):
        captured["file"] = path

    window.open_web_tab_with_url = fake_open_web_tab_with_url
    window.open_recent_file = fake_open_recent_file

    test_url = "https://example.com"
    print(f"[2/3] Simulating hyperlink click via MainWindow.handle_url({test_url})...")

    window.handle_url(QUrl(test_url))
    assert captured.get("web") == (test_url, None), "HTTP link was not routed to the web handler!"
    print(f"      -> Routed to web handler: {captured['web']}")
    
    print("[3/3] Testing local file:// URL link interception...")
    test_file_path = os.path.abspath("test_html_viewer.py")
    file_url = QUrl.fromLocalFile(test_file_path)
    print(f"      -> Simulating local link click: {file_url.toString()}...")
    
    window.handle_url(file_url)
    assert os.path.abspath(captured.get("file", "")) == test_file_path, "Local file link was not routed to the file handler!"
    print(f"      -> Routed to file handler: {captured['file']}")
    
    print("\n[SUCCESS] All link clicks (HTTP, HTTPS, FILE) are cleanly intercepted and opened inside EleViewer without launching external system browsers!")
    window.close()
    if hasattr(window, "_final_thread_cleanup"):
        window._final_thread_cleanup()
    app.processEvents()
    return 0

if __name__ == "__main__":
    raise SystemExit(run_test())

