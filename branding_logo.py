"""EleViewer branding logo generator."""

from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor
from PySide6.QtCore import Qt, QRect

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

    # Calculate bar dimensions
    bar_height = max(3, size // 10)
    bar_x = size // 4
    bar_width = size // 2

    # Top bar (white)
    painter.fillRect(
        QRect(bar_x, size // 4, bar_width, bar_height),
        QColor(BRAND_PRIMARY)
    )

    # Middle bar (accent blue) - centered and slightly narrower
    middle_bar_width = bar_width - (bar_width // 5)
    middle_bar_x = bar_x + (bar_width - middle_bar_width) // 2
    painter.fillRect(
        QRect(middle_bar_x, (size // 2) - (bar_height // 2), middle_bar_width, bar_height),
        QColor(BRAND_ACCENT)
    )

    # Bottom bar (white)
    painter.fillRect(
        QRect(bar_x, (size * 3) // 4, bar_width, bar_height),
        QColor(BRAND_PRIMARY)
    )

    painter.end()
    return QIcon(pixmap)


def create_eleviewer_pixmap(size: int = 32) -> QPixmap:
    """Create the EleViewer logo as a QPixmap."""
    return create_eleviewer_icon(size).pixmap(size, size)
