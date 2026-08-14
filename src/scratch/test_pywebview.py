import sys
import webview
import threading
import time
import traceback

def close_window(window):
    time.sleep(3)
    window.destroy()

try:
    window = webview.create_window("Test", "https://google.com", frameless=True)
    t = threading.Thread(target=close_window, args=(window,))
    t.start()
    webview.start(gui='edgechromium')
    print("SUCCESS_WEBVIEW")
except Exception as e:
    print(f"FAILED_WEBVIEW: {e}")
    traceback.print_exc()
