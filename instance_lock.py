import sys
import os
from PySide6.QtNetwork import QLocalServer, QLocalSocket
from PySide6.QtCore import QObject, Signal, QByteArray

SERVER_NAME = "EleViewerInstanceLock"

class SingleInstanceServer(QObject):
    file_opened = Signal(str)
    new_note_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.server = None

    def try_to_start(self):
        # First try to connect to an existing instance
        socket = QLocalSocket()
        socket.connectToServer(SERVER_NAME)

        if socket.waitForConnected(500):
            # Another instance is running
            if len(sys.argv) > 1:
                arg = sys.argv[1].strip()
                if arg in ("--new", "-n", "--new-note"):
                    socket.write(b"__NEW_NOTE__")
                else:
                    file_path = os.path.abspath(arg)
                    socket.write(file_path.encode('utf-8'))
                socket.waitForBytesWritten(1000)
            socket.disconnectFromServer()
            return False  # Failed to start as primary instance

        # No other instance is running, or it crashed and left a stale socket.
        # Clean up any stale socket and start our server.
        QLocalServer.removeServer(SERVER_NAME)
        self.server = QLocalServer(self)
        self.server.newConnection.connect(self._handle_new_connection)

        if not self.server.listen(SERVER_NAME):
            print(f"Failed to start single instance server: {self.server.errorString()}")

        return True

    def _handle_new_connection(self):
        socket = self.server.nextPendingConnection()
        if not socket:
            return

        socket.waitForReadyRead(1000)
        data = socket.readAll()

        if data:
            msg = bytes(data).decode('utf-8')
            if msg == "__NEW_NOTE__":
                self.new_note_requested.emit()
            elif os.path.exists(msg):
                self.file_opened.emit(msg)

        socket.disconnectFromServer()
        socket.deleteLater()

