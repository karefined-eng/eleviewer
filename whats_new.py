from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextBrowser, QFrame
)
from PySide6.QtCore import Qt
from theme import BRAND_BACKGROUND, BRAND_PRIMARY, BRAND_BORDER, BRAND_MUTED_FG, get_brand_accent


class WhatsNewDialog(QDialog):
    def __init__(self, parent=None, app_version="1.3.0"):
        super().__init__(parent)
        self.setWindowTitle(f"What's New in v{app_version}")
        self.resize(550, 450)
        
        accent = get_brand_accent()
        self.setStyleSheet(f"""
            QDialog {{ background: {BRAND_BACKGROUND}; color: {BRAND_PRIMARY}; }}
            QLabel {{ color: {BRAND_PRIMARY}; font-family: 'Segoe UI', sans-serif; }}
            QTextBrowser {{ 
                background: #1a1a1a; 
                color: #e0e0e0; 
                border: 1px solid {BRAND_BORDER}; 
                border-radius: 6px; 
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
        title_label = QLabel(f"🎉 EleViewer updated to v{app_version}")
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
            Thank you for studying with EleViewer! Here is what we just shipped based entirely on anonymous community feedback:
            <br><br>
            <b>1. CSV Table Workstation & Editor</b>
            <ul>
                <li>Dual view modes: toggle instantly between <b>Table Grid View</b> (Excel/Sheets style) and <b>Raw Text View</b>.</li>
                <li>Add rows, add columns, delete selected cells, and override delimiters on-the-fly without corrupting leading zeroes!</li>
            </ul>

            <b>2. HTML Live Workstation & 1-Click Browser Migration</b>
            <ul>
                <li>Split-screen live webpage workstation with debounced preview and 3-way view switcher.</li>
                <li>Click the new <b>Open in Browser Tab</b> button to push local HTML or preview URLs directly into the right-hand Web Panel!</li>
            </ul>

            <b>3. Obsidian-Inspired Web Panel & Link Interception</b>
            <ul>
                <li>The Web Panel now features dedicated <b>Refresh</b> and <b>Bookmark</b> toolbar controls.</li>
                <li><b>Zero External Browser Launches:</b> Clicking web links across documents or slide notes now automatically opens inside EleViewer's Web Panel!</li>
            </ul>
            
            <b>4. Expanded Universal TTS & Robust Shortcuts</b>
            <ul>
                <li>Pressing <code>F9</code> now reads aloud CSV spreadsheets and HTML pages alongside PDFs, DOCX, and PPTX!</li>
                <li>Restored full reliability to <code>Alt+V</code> (Toggle Vault) and <code>Ctrl+W</code> tab closing with intelligent Web Panel focus detection.</li>
            </ul>
            
            <br>
            <i>Thank you to the students who anonymously reported these issues. Your feedback directly shapes EleViewer.</i>
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
