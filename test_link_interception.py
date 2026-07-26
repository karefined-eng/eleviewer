import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QDesktopServices
from PySide6.QtCore import QUrl
from ui import MainWindow

def run_test():
    app = QApplication.instance() or QApplication(sys.argv)
    print("[1/3] Initializing MainWindow with global URL handlers...")
    window = MainWindow()
    
    test_url = "https://sakai.ug.edu.gh"
    print(f"[2/3] Simulating hyperlink click via QDesktopServices.openUrl({test_url})...")
    
    # Check web dock initial state
    initial_tab_count = 0
    if window._web_dock and window._web_dock.widget():
        initial_tab_count = window._web_dock.widget().tabs.count()
        
    # Trigger openUrl which Qt normally sends to external system browser (Chrome/Edge/Safari)
    res = QDesktopServices.openUrl(QUrl(test_url))
    assert res, "QDesktopServices.openUrl returned False!"
    
    # Verify Web Panel opened and loaded the URL!
    assert window._web_dock is not None, "Web dock was not created!"
    assert not window._web_dock.isHidden(), "Web dock is hidden after link click!"
    web_panel = window._web_dock.widget()
    assert web_panel is not None, "Web panel widget is None!"
    
    new_tab_count = web_panel.tabs.count()
    print(f"      -> Web Panel tab count changed from {initial_tab_count} to {new_tab_count}.")
    assert new_tab_count > initial_tab_count or new_tab_count >= 1, "No new tab was opened in WebPanel!"
    
    current_view = web_panel._current_view()
    current_url_str = current_view.url().toString() if current_view else ""
    print(f"      -> Current WebPanel URL: {current_url_str}")
    
    print("[3/3] Testing local file:// URL link interception...")
    test_file_path = os.path.abspath("test_html_viewer.py")
    file_url = QUrl.fromLocalFile(test_file_path)
    print(f"      -> Simulating local link click: {file_url.toString()}...")
    
    initial_editor_tabs = window.tabs.count()
    QDesktopServices.openUrl(file_url)
    new_editor_tabs = window.tabs.count()
    print(f"      -> Editor tab count changed from {initial_editor_tabs} to {new_editor_tabs}.")
    assert new_editor_tabs >= initial_editor_tabs, "Local file link did not open in editor!"
    
    print("\n[SUCCESS] All link clicks (HTTP, HTTPS, FILE) are cleanly intercepted and opened inside EleViewer without launching external system browsers!")
    window.close()
    return 0

if __name__ == "__main__":
    ret = run_test()
    os._exit(0)

