"""Application-level services used by the Qt shell.

Keeping persistence and viewer construction behind this boundary lets the
MainWindow coordinate workflows without owning every implementation detail.
"""

from file_handler import create_viewer_widget
from session_manager import clear_session, load_session, save_session
from settings import load_settings, save_settings


class WorkspaceServices:
    def load_settings(self):
        return load_settings()

    def save_settings(self, settings):
        return save_settings(settings)

    def create_viewer(self, file_path, content=None):
        return create_viewer_widget(file_path, content=content)

    def load_session(self):
        return load_session()

    def save_session(self, tabs_info, bookmarks_panel_visible=False):
        return save_session(tabs_info, bookmarks_panel_visible=bookmarks_panel_visible)

    def clear_session(self):
        return clear_session()
