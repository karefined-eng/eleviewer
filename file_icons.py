from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont, QPainterPath, QPen
from PySide6.QtCore import Qt, QRectF, QPointF

# All file icons now use the same unified accent color to fit the dark theme
ACCENT_COLOR_HEX = "#6cb6ff"

def file_type_icon(ext: str, size: int = 20) -> QIcon:
    """Generates a crisp document-page QIcon with a folded corner and a distinct monochrome symbol."""
    ext = ext.lower()
    accent_color = QColor(ACCENT_COLOR_HEX)
    
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    
    # Document Page Geometry
    margin = 1.5
    w = size - margin * 2
    h = size - margin * 2
    x = margin
    y = margin
    fold = max(3.5, size * 0.22)
    
    # Outer page path with folded top-right corner
    page_path = QPainterPath()
    page_path.moveTo(x, y)
    page_path.lineTo(x + w - fold, y)
    page_path.lineTo(x + w, y + fold)
    page_path.lineTo(x + w, y + h)
    page_path.lineTo(x, y + h)
    page_path.closeSubpath()
    
    # Fill page background (subtle dark panel color)
    bg_color = QColor(28, 28, 28, 230)
    painter.fillPath(page_path, bg_color)
    
    # Stroke page border with accent color
    pen = QPen(accent_color, 1.2)
    pen.setJoinStyle(Qt.MiterJoin)
    painter.setPen(pen)
    painter.drawPath(page_path)
    
    # Fold corner path
    fold_path = QPainterPath()
    fold_path.moveTo(x + w - fold, y)
    fold_path.lineTo(x + w - fold, y + fold)
    fold_path.lineTo(x + w, y + fold)
    fold_color = QColor(accent_color.red(), accent_color.green(), accent_color.blue(), 100)
    painter.fillPath(fold_path, fold_color)
    painter.drawPath(fold_path)
    
    # Draw internal glyph instead of extension text
    # Map extensions to specific symbols or glyphs
    glyph = "FILE"
    font_scale = 0.35
    if ext == ".md":
        glyph = "M↓"
        font_scale = 0.35
    elif ext == ".pdf":
        glyph = "≡" # horizontal lines
        font_scale = 0.5
    elif ext == ".docx":
        glyph = "W"
        font_scale = 0.4
    elif ext == ".xlsx":
        glyph = "⊞" # grid
        font_scale = 0.45
    elif ext == ".pptx":
        glyph = "▶"
        font_scale = 0.35
    elif ext == ".csv":
        glyph = ","
        font_scale = 0.5
    elif ext == ".txt":
        glyph = "T"
        font_scale = 0.4
    elif ext in (".html", ".htm"):
        glyph = "</>"
        font_scale = 0.25
    else:
        glyph = ext.replace(".", "").upper()[:3]
        font_scale = 0.25
        
    font = QFont("Segoe UI")
    font.setPixelSize(max(6, int(size * font_scale)))
    font.setBold(True)
    painter.setFont(font)
    
    # Glyph rect positioned in lower half of page, muted color
    text_rect = QRectF(x, y + h * 0.35, w, h * 0.6)
    glyph_color = QColor(accent_color.red(), accent_color.green(), accent_color.blue(), 180) # Slightly muted interior glyph
    painter.setPen(glyph_color)
    painter.drawText(text_rect, Qt.AlignCenter, glyph)
    
    painter.end()
    return QIcon(pixmap)
