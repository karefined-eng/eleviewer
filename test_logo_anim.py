import sys
from PySide6.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLabel
from morphing_loader import MorphingLogo, GlowingLogo

def main():
    app = QApplication(sys.argv)
    
    win = QWidget()
    win.setWindowTitle("Logo Animations Test")
    win.resize(400, 250)
    win.setStyleSheet("background-color: #161616; color: white;")
    
    layout = QHBoxLayout(win)
    
    # Morphing Logo
    vbox1 = QVBoxLayout()
    lbl1 = QLabel("MorphingLogo")
    lbl1.setStyleSheet("text-align: center;")
    morph = MorphingLogo(size=120)
    morph.start()
    vbox1.addWidget(lbl1)
    vbox1.addWidget(morph)
    
    # Glowing Logo
    vbox2 = QVBoxLayout()
    lbl2 = QLabel("GlowingLogo (Current Splash)")
    lbl2.setStyleSheet("text-align: center;")
    glow = GlowingLogo(size=120)
    glow.start()
    vbox2.addWidget(lbl2)
    vbox2.addWidget(glow)
    
    layout.addLayout(vbox1)
    layout.addLayout(vbox2)
    
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
