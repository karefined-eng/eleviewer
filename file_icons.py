from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QPen, QPainterPath
from PySide6.QtCore import Qt, QRectF, QPointF

# Unified colors matching the website live demo (interactive-demo.tsx)
ACCENT_COLOR_HEX = "#6cb6ff"  # Active / Selected state
MUTED_COLOR_HEX = "#888888"   # Normal / Inactive state


def _draw_icon_pixmap(ext: str, size: int, color_hex: str) -> QPixmap:
    """Draws a minimalist, Lucide-inspired line-art document icon without background fill or text clutter."""
    ext = ext.lower()
    if ext and not ext.startswith("."):
        ext = "." + ext

    stroke_color = QColor(color_hex)
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    # Calculate proportional line width and padding (matching Lucide 1.5px stroke on 24px grid)
    stroke_width = max(1.2, size * 0.075)
    margin = max(2.0, size * 0.12)
    w = size - margin * 2
    h = size - margin * 2
    x = margin
    y = margin
    fold = max(3.5, w * 0.30)

    # 1. Outer page outline with top-right folded corner (pure line art, NO background fill)
    page_path = QPainterPath()
    page_path.moveTo(x, y)
    page_path.lineTo(x + w - fold, y)
    page_path.lineTo(x + w, y + fold)
    page_path.lineTo(x + w, y + h)
    page_path.lineTo(x, y + h)
    page_path.closeSubpath()

    pen = QPen(stroke_color, stroke_width)
    pen.setCapStyle(Qt.RoundCap)
    pen.setJoinStyle(Qt.RoundJoin)
    painter.setPen(pen)
    painter.drawPath(page_path)

    # 2. Fold flap line (from top edge down and right to edge)
    fold_path = QPainterPath()
    fold_path.moveTo(x + w - fold, y)
    fold_path.lineTo(x + w - fold, y + fold)
    fold_path.lineTo(x + w, y + fold)
    painter.drawPath(fold_path)

    # 3. Minimalist internal vector geometry (matching Lucide React icons in demo)
    if ext in (".md", ".docx", ".txt", ".rtf"):
        # Lucide FileText: 3 horizontal lines (top, middle, and shorter bottom line)
        l1_y = y + h * 0.42
        l2_y = y + h * 0.58
        l3_y = y + h * 0.74
        painter.drawLine(QPointF(x + w * 0.28, l1_y), QPointF(x + w * 0.72, l1_y))
        painter.drawLine(QPointF(x + w * 0.28, l2_y), QPointF(x + w * 0.72, l2_y))
        painter.drawLine(QPointF(x + w * 0.28, l3_y), QPointF(x + w * 0.55, l3_y))

    elif ext == ".pdf":
        # Lucide File: pure uncluttered page outline with folded corner (exactly like lecture-04.pdf in demo)
        pass

    elif ext in (".xlsx", ".xls", ".csv", ".tsv"):
        # Lucide FileSpreadsheet: clean 2x2 table grid in lower half
        gx = x + w * 0.25
        gy = y + h * 0.42
        gw = w * 0.50
        gh = h * 0.40
        painter.drawRect(QRectF(gx, gy, gw, gh))
        painter.drawLine(QPointF(gx, gy + gh * 0.5), QPointF(gx + gw, gy + gh * 0.5))
        painter.drawLine(QPointF(gx + gw * 0.5, gy), QPointF(gx + gw * 0.5, gy + gh))

    elif ext in (".pptx", ".ppt"):
        # Lucide Presentation / FilePlay: clean play triangle outline
        tri_path = QPainterPath()
        tri_path.moveTo(x + w * 0.40, y + h * 0.45)
        tri_path.lineTo(x + w * 0.68, y + h * 0.60)
        tri_path.lineTo(x + w * 0.40, y + h * 0.75)
        tri_path.closeSubpath()
        painter.drawPath(tri_path)

    elif ext in (".html", ".htm", ".xml", ".json"):
        # Lucide FileCode: clean left/right angle brackets < >
        left_path = QPainterPath()
        left_path.moveTo(x + w * 0.42, y + h * 0.48)
        left_path.lineTo(x + w * 0.28, y + h * 0.60)
        left_path.lineTo(x + w * 0.42, y + h * 0.72)
        painter.drawPath(left_path)

        right_path = QPainterPath()
        right_path.moveTo(x + w * 0.58, y + h * 0.48)
        right_path.lineTo(x + w * 0.72, y + h * 0.60)
        right_path.lineTo(x + w * 0.58, y + h * 0.72)
        painter.drawPath(right_path)

    else:
        # Default fallback: Lucide FileText style (3 lines)
        l1_y = y + h * 0.42
        l2_y = y + h * 0.58
        l3_y = y + h * 0.74
        painter.drawLine(QPointF(x + w * 0.28, l1_y), QPointF(x + w * 0.72, l1_y))
        painter.drawLine(QPointF(x + w * 0.28, l2_y), QPointF(x + w * 0.72, l2_y))
        painter.drawLine(QPointF(x + w * 0.28, l3_y), QPointF(x + w * 0.55, l3_y))

    painter.end()
    return pixmap


def file_type_icon(ext: str, size: int = 20, active: bool = False) -> QIcon:
    """
    Generates a multi-state QIcon matching the minimalist Lucide line-art aesthetic of the website live demo.
    When active=True (or when Qt renders in Active/Selected mode), uses vibrant #6cb6ff accent.
    When active=False, uses calm gray (#888888) for Normal mode.
    """
    icon = QIcon()
    primary_color = ACCENT_COLOR_HEX if active else MUTED_COLOR_HEX
    pix_normal = _draw_icon_pixmap(ext, size, primary_color)
    pix_active = _draw_icon_pixmap(ext, size, ACCENT_COLOR_HEX)

    icon.addPixmap(pix_normal, QIcon.Normal, QIcon.Off)
    icon.addPixmap(pix_active, QIcon.Active, QIcon.Off)
    icon.addPixmap(pix_active, QIcon.Selected, QIcon.Off)
    return icon


