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
            <b>1. Native PowerPoint (.pptx) Integration</b>
            <ul>
                <li>EleViewer can now instantly extract slide text and speaker notes from PPTX files!</li>
                <li>Flip through slides cleanly and use the Text-to-Speech (TTS) reader on PowerPoint lectures.</li>
            </ul>
            
            <b>2. Active Reading Focus Mode</b>
            <ul>
                <li>When the TTS engine is reading aloud, the active reader bar now glows with the accent color to indicate active reading mode.</li>
            </ul>
            
            <b>3. License Upgraded to GNU GPLv3</b>
            <ul>
                <li>We transitioned our license from MIT to GPLv3. This guarantees EleViewer remains free, open-source, and protected against corporate piracy forever.</li>
            </ul>
            
            <b>4. Deep System Integration</b>
            <ul>
                <li>The Windows installer now fully associates EleViewer as the default editor for .docx, .xlsx, .pptx, .csv, .md, and .pdf files.</li>
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
