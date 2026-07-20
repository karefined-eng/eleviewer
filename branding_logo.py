"""EleViewer branding logo generator."""

from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor
from PySide6.QtCore import Qt, QRect, QRectF

from theme import BRAND_PANEL, BRAND_PRIMARY, BRAND_ACCENT


def create_eleviewer_icon(size: int = 32) -> QIcon:
    """
    Create the EleViewer "E" logo icon.
    The logo consists of three horizontal bars:
    - Top bar: white (#f2f2f0)
    - Middle bar: accent blue (#6cb6ff)
    - Bottom bar: white (#f2f2f0)
    """
    pixmap = QPixmap(size, size)
    pixmap.fill(QColor(BRAND_PANEL))

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Calculate scale factor relative to 32x32 reference
    scale = size / 32.0

    def scaled(val):
        return val * scale

    # Background is already filled with BRAND_PANEL
    
    # Border (optional but good for consistency with SVG)
    painter.setPen(QColor("#2c2c2c"))
    painter.setBrush(Qt.NoBrush)
    painter.drawRoundedRect(
        QRectF(scaled(0.5), scaled(0.5), scaled(31), scaled(31)),
        scaled(6.5), scaled(6.5)
    )

    # Top bar (white)
    painter.setPen(Qt.NoPen)
    painter.setBrush(QColor(BRAND_PRIMARY))
    painter.drawRoundedRect(
        QRectF(scaled(9), scaled(9), scaled(14), scaled(3)),
        scaled(1.5), scaled(1.5)
    )

    # Middle bar (accent blue)
    painter.setBrush(QColor(BRAND_ACCENT))
    painter.drawRoundedRect(
        QRectF(scaled(11), scaled(14.5), scaled(10), scaled(3)),
        scaled(1.5), scaled(1.5)
    )

    # Bottom bar (white)
    painter.setBrush(QColor(BRAND_PRIMARY))
    painter.drawRoundedRect(
        QRectF(scaled(9), scaled(20), scaled(14), scaled(3)),
        scaled(1.5), scaled(1.5)
    )

    painter.end()
    return QIcon(pixmap)


def create_eleviewer_pixmap(size: int = 32) -> QPixmap:
    """Create the EleViewer logo as a QPixmap."""
    return create_eleviewer_icon(size).pixmap(size, size)
