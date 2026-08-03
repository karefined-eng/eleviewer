"""EleViewer branding logo generator."""

from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QPainterPath
from PySide6.QtCore import Qt, QRect, QRectF

from theme import get_brand_accent, get_active_palette


import os

def _get_base_path():
    """Get absolute path to resource, works for dev and for Nuitka"""
    return os.path.dirname(os.path.abspath(__file__))

def create_eleviewer_icon(size: int = 32, rounded: bool = False) -> QIcon:
    """
    Load the native EleViewer logo icon (which has a transparent background).
    """
    icon_path = os.path.join(_get_base_path(), "icons", "eleviewer.png")
    if os.path.exists(icon_path):
        if not rounded:
            return QIcon(icon_path)
        
        pix = QPixmap(icon_path)
        target = QPixmap(pix.size())
        target.fill(Qt.transparent)
        painter = QPainter(target)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        # 20% border radius for a standard app icon look
        radius = min(pix.width(), pix.height()) * 0.2
        path.addRoundedRect(QRectF(target.rect()), radius, radius)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, pix)
        painter.end()
        return QIcon(target)
    
    # Fallback to a simple transparent icon if file is missing
    p = get_active_palette()
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    scale = size / 32.0
    def scaled(val): return val * scale

    painter.setPen(Qt.NoPen)
    painter.setBrush(QColor(p['BRAND_PRIMARY']))
    painter.drawRoundedRect(QRectF(scaled(9), scaled(9), scaled(14), scaled(3)), scaled(1.5), scaled(1.5))
    painter.setBrush(QColor(get_brand_accent()))
    painter.drawRoundedRect(QRectF(scaled(11), scaled(14.5), scaled(10), scaled(3)), scaled(1.5), scaled(1.5))
    painter.setBrush(QColor(p['BRAND_PRIMARY']))
    painter.drawRoundedRect(QRectF(scaled(9), scaled(20), scaled(14), scaled(3)), scaled(1.5), scaled(1.5))
    painter.end()
    
    return QIcon(pixmap)


def create_eleviewer_pixmap(size: int = 32) -> QPixmap:
    """Create the EleViewer logo as a QPixmap."""
    return create_eleviewer_icon(size).pixmap(size, size)
