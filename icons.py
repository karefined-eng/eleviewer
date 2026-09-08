"""Load Lucide-style SVG icons from the icons/ directory."""

from pathlib import Path
import re

from PySide6.QtCore import QByteArray, QSize, Qt
from PySide6.QtGui import QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer

from theme import ICON_SIZE_TOOLBAR

import sys

if hasattr(sys, '_MEIPASS'):
    ICONS_DIR = Path(sys._MEIPASS) / "icons"
else:
    ICONS_DIR = Path(__file__).parent / "icons"

_cache: dict[tuple[str, int, str], QIcon] = {}


_ALIASES = {
    "circle-help": "help-circle",
    "folder": "folder-open",
    "folder-open": "folder",
    "sidebar": "panel-left",
    "file": "file-plus",
}


def icon(name: str, size: int = ICON_SIZE_TOOLBAR, color: str = "#c0c0c0") -> QIcon:
    key = (name, size, color)
    if key in _cache:
        return _cache[key]

    svg_path = ICONS_DIR / f"{name}.svg"
    if not svg_path.exists() and name in _ALIASES:
        svg_path = ICONS_DIR / f"{_ALIASES[name]}.svg"

    if not svg_path.exists():
        return QIcon()

    svg_data = svg_path.read_text(encoding="utf-8")

    # Normalise stroke colour so icons appear in the requested colour
    # (handles currentColor, hardcoded black #000000/#000, or missing stroke)
    svg_data = svg_data.replace('stroke="currentColor"', f'stroke="{color}"')
    svg_data = svg_data.replace("stroke='currentColor'", f"stroke='{color}'")
    svg_data = re.sub(r'stroke="(#000000?|black)"', f'stroke="{color}"', svg_data)
    svg_data = re.sub(r"stroke='(#000000?|black)'", f"stroke='{color}'", svg_data)

    if 'stroke=' not in svg_data:
        svg_data = svg_data.replace('<svg ', f'<svg stroke="{color}" ')

    # Render at 2× density then smooth-scale down for crisp HiDPI output.
    render_size = size * 2
    renderer = QSvgRenderer(QByteArray(svg_data.encode("utf-8")))
    hi_pixmap = QPixmap(QSize(render_size, render_size))
    hi_pixmap.fill(Qt.transparent)
    painter = QPainter(hi_pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setRenderHint(QPainter.SmoothPixmapTransform)
    renderer.render(painter)
    painter.end()

    pixmap = hi_pixmap.scaled(
        QSize(size, size),
        Qt.KeepAspectRatio,
        Qt.SmoothTransformation,
    )

    qicon = QIcon(pixmap)
    _cache[key] = qicon
    return qicon
