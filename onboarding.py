import os
from PySide6.QtCore import QObject, QTimer

class OnboardingManager(QObject):
    """
    An action-first interactive onboarding manager.
    Instead of showing a slide deck, this drops the user into an interactive 
    Playground document and listens to their actions (like opening a quick note, 
    adding a bookmark, etc.), providing immediate visual toast feedback.
    """
    def __init__(self, window):
        super().__init__(window)
        self.window = window
        self.playground_path = os.path.join(os.path.dirname(__file__), "getting_started", "Playground.md")
        
        self.note_opened = False
        self.bookmark_added = False
        self.web_opened = False
        
    def start(self):
        # Open Web Panel immediately to showcase the split-screen layout
        if self.window._web_dock is None or not self.window._web_dock.isVisible():
            self.window.toggle_web_panel()
            
        # Open the interactive Playground document
        if os.path.exists(self.playground_path):
            self.window._open_vault_file(self.playground_path)
            
        # Hook into window actions for feedback
        self._hook_actions()
        
        # Show welcome toast
        self.window.statusBar().showMessage("👋 Welcome to EleViewer! Try the actions in the Playground.", 8000)

    def _hook_actions(self):
        # Hook Alt+E (bring_to_front_and_new_note)
        orig_bring_to_front = self.window.bring_to_front_and_new_note
        def hooked_bring_to_front():
            orig_bring_to_front()
            if not self.note_opened:
                self.note_opened = True
                self._show_success("Quick Note Opened (Alt+E)")
        self.window.bring_to_front_and_new_note = hooked_bring_to_front
        
        # Hook Bookmark (add_bookmark_from_editor)
        orig_add_bookmark = self.window._add_bookmark_from_editor
        def hooked_add_bookmark(editor, data):
            orig_add_bookmark(editor, data)
            if not self.bookmark_added:
                self.bookmark_added = True
                self._show_success("Bookmark Added (Ctrl+D)")
        self.window._add_bookmark_from_editor = hooked_add_bookmark

        # Hook Web Panel toggle (just in case they close and reopen it)
        orig_toggle_web = self.window.toggle_web_panel
        def hooked_toggle_web():
            orig_toggle_web()
            if not self.web_opened and self.window._web_dock and self.window._web_dock.isVisible():
                self.web_opened = True
                self._show_success("Web Panel Opened (Ctrl+T)")
        self.window.toggle_web_panel = hooked_toggle_web

    def _show_success(self, msg):
        # Temporarily make the status bar text green and bold
        self.window.statusBar().setStyleSheet("QStatusBar { color: #4ade80; font-weight: bold; }")
        self.window.statusBar().showMessage(f"✅ Awesome! {msg}", 5000)
        
        # Reset color after 5 seconds
        QTimer.singleShot(5000, lambda: self.window.statusBar().setStyleSheet(""))
