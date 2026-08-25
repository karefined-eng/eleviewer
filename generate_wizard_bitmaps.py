import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPixmap, QPainter, QColor, QPen
from PySide6.QtCore import Qt, QRect

# Add current directory to path so we can import theme and branding_logo
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from theme import BRAND_PANEL, get_brand_accent
from branding_logo import create_eleviewer_pixmap

def generate_bitmaps():
    app = QApplication(sys.argv)
    icons_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons")
    os.makedirs(icons_dir, exist_ok=True)
    
    # 1. WizardBanner (164x314)
    banner_w, banner_h = 164, 314
    banner_pixmap = QPixmap(banner_w, banner_h)
    banner_pixmap.fill(QColor(BRAND_PANEL))
    
    painter = QPainter(banner_pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    # Draw a subtle accent line on the right edge
    pen = QPen(QColor(get_brand_accent()))
    pen.setWidth(4)
    painter.setPen(pen)
    painter.drawLine(banner_w - 2, 0, banner_w - 2, banner_h)
    
    # Draw logo in the center
    logo_size = 96
    logo_pixmap = create_eleviewer_pixmap(logo_size)
    x = (banner_w - logo_size) // 2
    y = (banner_h - logo_size) // 2 - 20 # slightly above center
    painter.drawPixmap(x, y, logo_pixmap)
    painter.end()
    
    banner_path = os.path.join(icons_dir, "wizard_banner.bmp")
    banner_pixmap.save(banner_path, "BMP")
    print(f"Generated {banner_path}")
    
    # 2. WizardSmallLogo (55x55)
    small_w, small_h = 55, 55
    small_pixmap = QPixmap(small_w, small_h)
    small_pixmap.fill(QColor(BRAND_PANEL)) # Inno Setup uses background color of standard windows, but dark mode panel is fine
    
    painter = QPainter(small_pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    logo_size_small = 45
    logo_pixmap_small = create_eleviewer_pixmap(logo_size_small)
    x_small = (small_w - logo_size_small) // 2
    y_small = (small_h - logo_size_small) // 2
    painter.drawPixmap(x_small, y_small, logo_pixmap_small)
    painter.end()
    
    small_path = os.path.join(icons_dir, "wizard_logo.bmp")
    small_pixmap.save(small_path, "BMP")
    print(f"Generated {small_path}")

if __name__ == "__main__":
    generate_bitmaps()
