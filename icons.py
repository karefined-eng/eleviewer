"""Load Lucide-style SVG icons from the icons/ directory."""

from pathlib import Path

from PySide6.QtCore import QByteArray, QSize, Qt
from PySide6.QtGui import QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer

from theme import ICON_SIZE_TOOLBAR

ICONS_DIR = Path(__file__).parent / "icons"
_cache: dict[tuple[str, int], QIcon] = {}


def icon(name: str, size: int = ICON_SIZE_TOOLBAR, color: str = "#e0e0e0") -> QIcon:
    key = (name, size)
    if key in _cache:
        return _cache[key]

    svg_path = ICONS_DIR / f"{name}.svg"
    if not svg_path.exists():
        return QIcon()

    svg_data = svg_path.read_text(encoding="utf-8")
    if "stroke=" not in svg_data:
        svg_data = svg_data.replace("<svg ", f'<svg stroke="{color}" ')

    renderer = QSvgRenderer(QByteArray(svg_data.encode("utf-8")))
    pixmap = QPixmap(QSize(size, size))
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()

    qicon = QIcon(pixmap)
    _cache[key] = qicon
    return qicon
