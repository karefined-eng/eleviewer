import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QFrame, QLabel, QPushButton, 
                               QTextEdit, QSplitter, QStatusBar)
from PySide6.QtGui import QFont, QColor, QIcon, QAction  # Fixed: Import from QtGui
from PySide6.QtCore import Qt

class MockWebView(QWidget):
    """Simulates the Web Panel for Sakai/STS/MIS"""
    def __init__(self):
        super().__init__()
        self.setFixedWidth(200)
        self.setStyleSheet("background-color: #1e1e1e; color: white;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        label = QLabel("PORTALS")
        label.setFont(QFont("Segoe UI", 9, QFont.Bold))
        label.setStyleSheet("color: #aaaaaa; margin-bottom: 10px;")
        layout.addWidget(label)
        
        portals = [
            ("🎓 Sakai", "#3b82f6"),
            ("🛠️ STS", "#10b981"),
            ("📊 MIS", "#f59e0b")
        ]
        
        for name, color in portals:
            btn = QPushButton(name)
            btn.setFixedHeight(40)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    border-radius: 6px;
                    font-size: 14px;
                    border: none;
                    text-align: left;
                    padding-left: 15px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {color}dd;
                }}
            """)
            layout.addWidget(btn)
            
        layout.addStretch()
        
        book_label = QLabel("BOOKMARKS")
        book_label.setFont(QFont("Segoe UI", 8))
        book_label.setStyleSheet("color: #666; margin-top: 20px;")
        layout.addWidget(book_label)

class MockEditor(QWidget):
    """Simulates the Document Viewer Area"""
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #ffffff;")
        
        layout = QVBoxLayout(self)
        
        self.editor = QTextEdit()
        self.editor.setReadOnly(True)
        self.editor.setText("""
        <h1>CS261: Data Structures - Week 5</h1>
        <p><strong>Lecture Topic:</strong> Binary Search Trees</p>
        <hr/>
        <p>In today's lecture, we covered the fundamental operations of BSTs...</p>
        <p>1. Insertion</p>
        <p>2. Deletion</p>
        <p>3. Traversal Methods</p>
        """)
        self.editor.setFont(QFont("Consolas", 11))
        layout.addWidget(self.editor)
        
        toolbar_layout = QHBoxLayout()
        btn_style = "padding: 5px 15px; border-radius: 4px; font-size: 12px; font-weight: bold; border: none;"
        
        actions = [
            ("📌 Pin", "#ff9900"),
            ("💾 Save", "#4caf50"),
            ("✂️ Split View", "#2196f3"),
            ("➕ Add Note", "#9c27b0")
        ]
        
        for name, color in actions:
            btn = QPushButton(name)
            btn.setStyleSheet(f"{btn_style} background-color: {color}; color: white;")
            toolbar_layout.addWidget(btn)
            
        toolbar_widget = QWidget()
        toolbar_widget.setLayout(toolbar_layout)
        toolbar_widget.setFixedHeight(45)
        toolbar_widget.setStyleSheet("background-color: #f5f5f5; border-top: 1px solid #ddd;")
        layout.addWidget(toolbar_widget)

class MockRightPanel(QWidget):
    """Simulates the Right Context Panel"""
    def __init__(self):
        super().__init__()
        self.setFixedWidth(220)
        self.setStyleSheet("background-color: #f9f9f9; border-left: 1px solid #ddd;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        course_lbl = QLabel("Current Course")
        course_lbl.setFont(QFont("Segoe UI", 10, QFont.Bold))
        layout.addWidget(course_lbl)
        
        course_val = QLabel("CS261 - Data Structures")
        course_val.setStyleSheet("color: #555; font-size: 13px;")
        layout.addWidget(course_val)
        
        layout.addSpacing(20)
        
        dead_lbl = QLabel("Upcoming")
        dead_lbl.setFont(QFont("Segoe UI", 10, QFont.Bold))
        layout.addWidget(dead_lbl)
        
        deadline_box = QLabel("🔥 Quiz: Today @ 2:00 PM<br><br>📅 Assignment: Fri @ 11:59 PM")
        deadline_box.setStyleSheet("color: #d32f2f; font-size: 13px; background: #ffebee; padding: 10px; border-radius: 6px;")
        layout.addWidget(deadline_box)
        
        layout.addStretch()

class MainWindowPreview(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EleViewer - UI Preview for UG Students")
        self.resize(1200, 800)
        
        self.setStyleSheet("""
            QMainWindow { background-color: #121212; }
            QMenuBar { background-color: #1e1e1e; color: white; border-bottom: 1px solid #333; }
            QMenuBar::item:selected { background-color: #333; }
            QStatusBar { background-color: #1e1e1e; color: #aaa; border-top: 1px solid #333; }
        """)
        
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        splitter = QSplitter(Qt.Horizontal)
        
        web_panel = MockWebView()
        splitter.addWidget(web_panel)
        
        editor = MockEditor()
        splitter.addWidget(editor)
        
        right_panel = MockRightPanel()
        splitter.addWidget(right_panel)
        
        splitter.setSizes([200, 800, 220])
        
        main_layout.addWidget(splitter)
        
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        file_menu.addAction("New")
        file_menu.addAction("Open")
        file_menu.addAction("Save")
        
        self.statusBar().showMessage("Ready • Connected to Sakai • CS261 • Last saved: Just now")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindowPreview()
    window.show()
    sys.exit(app.exec())