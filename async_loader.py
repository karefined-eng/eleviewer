"""Reusable Qt worker for document parsing that must not block the UI thread."""

from PySide6.QtCore import QThread, Signal


class AsyncLoadWorker(QThread):
    result_ready = Signal(object)
    error_occurred = Signal(str)

    def __init__(self, loader, parent=None):
        super().__init__(parent)
        self._loader = loader

    def run(self):
        try:
            self.result_ready.emit(self._loader())
        except Exception as error:
            self.error_occurred.emit(str(error))

    def cancel(self):
        self.requestInterruption()
