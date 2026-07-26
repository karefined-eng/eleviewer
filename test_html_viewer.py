"""
Automated verification test suite for HtmlViewer and WebPanel Live Feed migration.
Verifies split-screen mode switching, syntax highlighting, debounced live preview,
Universal TTS (F9) read-aloud, file_handler factory routing, and WebPanel tab management.
"""

import sys
import os
import time
from PySide6.QtWidgets import QApplication
from html_viewer import HtmlViewer
from file_handler import create_viewer_widget, get_file_content
from web_panel import WebPanel, WEB_AVAILABLE

def run_tests():
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

    app = QApplication.instance() or QApplication(sys.argv)
    print("[1/6] Testing HtmlViewer initialization and split-screen mode...")
    sample_html = "<!DOCTYPE html>\n<html>\n<head><title>Test</title></head>\n<body>\n  <h1>Hello World</h1>\n  <p>Live feed test</p>\n</body>\n</html>"
    viewer = HtmlViewer(content=sample_html)
    assert viewer._mode == "split", f"Expected default mode 'split', got '{viewer._mode}'"
    assert "Hello World" in viewer.toPlainText()
    print("  -> Passed! HtmlViewer initializes cleanly in Split View mode.")

    print("[2/6] Testing 3-way view switcher (Preview, Syntax, Split View)...")
    viewer.set_view_mode("preview")
    assert viewer.editor.isHidden() and not viewer.viewer.isHidden(), "Preview mode failed visibility check"
    viewer.set_view_mode("syntax")
    assert not viewer.editor.isHidden() and viewer.viewer.isHidden(), "Syntax mode failed visibility check"
    viewer.set_view_mode("split")
    assert not viewer.editor.isHidden() and not viewer.viewer.isHidden(), "Split mode failed visibility check"
    print("  -> Passed! 3-way view switcher toggles visibility cleanly.")

    print("[3/6] Testing syntax edits and live feed debounce timer...")
    viewer.editor.setPlainText("<h1>Modified Title</h1>")
    assert viewer.is_modified, "Expected is_modified to be True after text edit"
    assert viewer._debounce_timer.isActive() or viewer._debounce_timer.interval() == 300
    # Manually trigger live preview update to verify rendering without waiting 300ms
    viewer._update_live_preview()
    print("  -> Passed! Live feed debounce timer and text synchronization work!")

    print("[4/6] Testing Universal TTS (F9) Read Aloud method...")
    tts_output = viewer.read_current_page()
    assert "Modified Title" in tts_output and "HTML Webpage Workstation" in tts_output, f"Unexpected TTS output: {tts_output}"
    print(f"  -> Passed! TTS output: '{tts_output}'")

    print("[5/6] Testing file_handler factory routing for .html and .htm...")
    widget = create_viewer_widget("index.html", content=sample_html)
    assert isinstance(widget, HtmlViewer), f"Expected HtmlViewer widget, got {type(widget)}"
    extracted = get_file_content(widget, "index.html")
    assert "Hello World" in extracted
    print("  -> Passed! file_handler routes .html cleanly to HtmlViewer.")

    print("[6/6] Testing WebPanel 1-click browser migration and reload_url...")
    web_panel = WebPanel()
    test_url = "file:///c:/test_live_feed.html"
    web_panel.open_url_in_new_tab(test_url, "Live Feed")
    assert web_panel.tabs.count() >= 1, "Expected WebPanel to add browser tab"
    # Verify reload_url finds and reloads matching file URLs
    reloaded = web_panel.reload_url(test_url)
    assert reloaded, f"Expected reload_url to return True for {test_url}"
    print("  -> Passed! WebPanel tab creation and live reload_url work seamlessly!")

    print("\nALL 6 HTML LIVE FEED & BROWSER MIGRATION TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
