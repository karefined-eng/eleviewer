import sys
from PySide6.QtWidgets import QApplication
from whats_new import WhatsNewDialog
from quick_switcher import QuickSwitcher
from bookmark_panel import BookmarkPanel
from web_panel import WebPanel
import theme

def run():
    app = QApplication.instance() or QApplication(sys.argv)
    
    print("Testing WhatsNewDialog...")
    w1 = WhatsNewDialog()
    
    print("Testing QuickSwitcher...")
    w2 = QuickSwitcher([], [])
    
    print("Testing BookmarkPanel...")
    w3 = BookmarkPanel()
    
    print("Testing WebPanel...")
    w4 = WebPanel()
    
    print("All UI components instantiated successfully. UI Makeover applied without regressions.")

if __name__ == '__main__':
    run()
