from PySide6.QtWidgets import QTextEdit

from theme import editor_stylesheet


class EditorTab(QTextEdit):

    def __init__(self):
        super().__init__()
        self.file_path = None
        self.is_modified = False
        self.textChanged.connect(self.mark_modified)
        self.setStyleSheet(editor_stylesheet())

    def mark_modified(self):
        self.is_modified = True

    def setPlainText(self, text):
        self.blockSignals(True)
        super().setPlainText(text)
        self.blockSignals(False)
        self.is_modified = False
