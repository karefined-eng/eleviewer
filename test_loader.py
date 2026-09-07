import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from morphing_loader import MorphingHamburger

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Morphing Hamburger Test")
        self.resize(300, 300)
        
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        
        self.loader = MorphingHamburger(size=120)
        layout.addWidget(self.loader)
        
        self.setCentralWidget(main_widget)
        self.loader.start()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())
