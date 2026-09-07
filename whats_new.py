from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextBrowser, QFrame
)
from PySide6.QtCore import Qt
from theme import get_active_palette, get_brand_accent


class WhatsNewDialog(QDialog):
    def __init__(self, parent=None, app_version="1.4.0"):
        super().__init__(parent)
        self.setWindowTitle(f"What's New in v{app_version}")
        self.resize(550, 450)
        
        accent = get_brand_accent()
        p = get_active_palette()
        self.setStyleSheet(f"""
            QDialog {{ background: {p['BRAND_BACKGROUND']}; color: {p['BRAND_PRIMARY']}; }}
            QLabel {{ color: {p['BRAND_PRIMARY']}; font-family: 'Segoe UI', sans-serif; }}
            QTextBrowser {{ 
                background: transparent; 
                border: none; 
                border-top: 1px solid {p['BRAND_BORDER']}; 
                border-bottom: 1px solid {p['BRAND_BORDER']}; 
                color: #e0e0e0; 
                padding: 15px; 
                font-family: 'Segoe UI', sans-serif; 
                font-size: 14px; 
                line-height: 1.6;
            }}
            QPushButton {{
                background: {accent};
                color: #131313;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background: #559be6; }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        header_layout = QHBoxLayout()
        title_label = QLabel(f"EleViewer updated to v{app_version}")
        title_label.setStyleSheet("font-size: 22px; font-weight: bold; color: #ffffff;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)

        content = QTextBrowser()
        content.setOpenExternalLinks(True)
        html = f"""
        <style>
            ul {{ margin-top: 5px; margin-bottom: 15px; }}
            li {{ margin-bottom: 8px; }}
            b {{ color: {accent}; }}
        </style>
        <div>
            Thank you for studying with EleViewer! Here is what we just shipped to make your workspace even better:
            <br><br>
            <b>1. Enhanced Split-Screen Web Browser</b>
            <ul>
                <li><b>Smooth Page Zoom:</b> Scale web pages easily with <code>Ctrl + +</code>, <code>Ctrl + -</code>, <code>Ctrl + 0</code>, or hold <code>Ctrl</code> while scrolling. A live zoom badge in the top bar keeps you informed.</li>
                <li><b>Integrated File Downloads:</b> Download course slides, PDFs, and data files directly into your Downloads folder with an animated progress bar.</li>
                <li><b>Quick Right-Click Menu:</b> Right-click any link or page to open in a new tab, copy web links or selected text, bookmark pages, or adjust your zoom.</li>
                <li><b>Tab Preview Tooltips:</b> Hover over any web tab to view the complete title and web address without cluttering your screen.</li>
            </ul>

            <b>2. Intuitive Toolbar with Clear Labels</b>
            <ul>
                <li>Clear, readable labels directly under icons ("New File", "Vault", "Bookmarks", "Open", "Save", "Read Aloud", "Web", "Settings") so every tool is immediately obvious.</li>
                <li>Fully customizable in Settings: choose between <i>Icons with text labels</i>, <i>Icons only</i>, or <i>Icons beside text</i>.</li>
            </ul>

            <b>3. Expanded Settings & Preferences</b>
            <ul>
                <li>Six dedicated tabs to personalize your study workspace: customize your Web Panel downloads destination, set default zoom levels, adjust editor font sizes and line wrapping, configure PDF viewing modes, choose Text-to-Speech reading speeds, and adjust vault search scopes.</li>
            </ul>

            <b>4. Visual Bookmarks</b>
            <ul>
                <li>Bookmarks now show dedicated icons for web links and document files so you can find what you need instantly.</li>
                <li>Added a simple one-click button to remove bookmarks when you are done studying a topic.</li>
            </ul>
            
            <br>
            <i>Thank you to everyone who shared ideas and feedback. Your suggestions directly shape EleViewer.</i>
        </div>
        """
        content.setHtml(html)
        layout.addWidget(content)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_close = QPushButton("Awesome, let's get back to studying")
        btn_close.clicked.connect(self.accept)
        btn_layout.addWidget(btn_close)
        
        layout.addLayout(btn_layout)
