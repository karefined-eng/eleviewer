from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont, QPainterPath, QPen
from PySide6.QtCore import Qt, QRectF, QPointF

EXT_COLORS = {
    ".md": "#6cb6ff",     # Accent Blue
    ".pdf": "#ff6b6b",    # Red / Coral
    ".docx": "#4d96ff",   # Word Blue
    ".xlsx": "#6bcb77",   # Excel Green
    ".csv": "#2bcbba",    # Teal
    ".txt": "#a0a0a0",    # Muted Gray
    ".html": "#ff9f43",   # Orange
}

def file_type_icon(ext: str, size: int = 20) -> QIcon:
    """Generates a crisp document-page QIcon with a folded corner and colored brand accent."""
    ext = ext.lower()
    color_hex = EXT_COLORS.get(ext, "#888888")
    accent_color = QColor(color_hex)
    
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
    
    # Draw File Extension Text Badge in lower region
    text = ext.replace(".", "").upper()[:4]
    if not text:
        text = "FILE"
        
    font_size = max(5, int(size * 0.26))
    font = QFont("Segoe UI", font_size)
    font.setBold(True)
    painter.setFont(font)
    
    # Text rect positioned in lower half of page
    text_rect = QRectF(x, y + h * 0.35, w, h * 0.6)
    painter.setPen(accent_color)
    painter.drawText(text_rect, Qt.AlignCenter, text)
    
    painter.end()
    return QIcon(pixmap)
