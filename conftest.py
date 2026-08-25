import pytest
from PySide6.QtWidgets import QApplication


@pytest.fixture(scope="session", autouse=True)
def close_qt_windows_at_session_end():
    yield
    app = QApplication.instance()
    if app is None:
        return
    for window in list(app.topLevelWidgets()):
        window.close()
    app.processEvents()
    app.quit()
    app.processEvents()
