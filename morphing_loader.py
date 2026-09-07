import math
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QVariantAnimation, QRectF
from PySide6.QtGui import QPainter, QColor
from theme import BRAND_PRIMARY, get_brand_accent, BRAND_PANEL

class MorphingLogo(QWidget):
    def __init__(self, parent=None, size=64, duration=4500):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self._progress = 0.0
        
        self.anim = QVariantAnimation(self)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.setDuration(duration)
        self.anim.valueChanged.connect(self._on_progress)
        self.anim.setLoopCount(-1)  # Infinite
        
    def start(self):
        self.anim.start()
        
    def stop(self):
        self.anim.stop()
        
    def _on_progress(self, p):
        self._progress = p
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw background rounded rect
        painter.setBrush(QColor(BRAND_PANEL))
        painter.setPen(QColor("#2c2c2c"))
        painter.drawRoundedRect(
            1, 1, self.width()-2, self.height()-2,
            self.width() * 0.2, self.height() * 0.2
        )
        
        cx, cy = self.width() / 2, self.height() / 2
        scale = self.width() / 32.0
        
        h = 3 * scale
        spacing = 5.5 * scale
        top_w = 14 * scale
        mid_w = 10 * scale
        
        p = self._progress
        
        # 6 phases instead of 4
        phase = int(p * 6)
        if phase > 5: phase = 5
        
        local_p = (p * 6) - phase
        if local_p < 0.2:
            t = 0.0
        elif local_p > 0.8:
            t = 1.0
        else:
            t = (local_p - 0.2) / 0.6
            if t < 0.5:
                t = 4 * t * t * t
            else:
                t = 1 - math.pow(-2 * t + 2, 3) / 2
                
        def lerp(a, b, t):
            return a + (b - a) * t

        # Keyframes: (y_offset, x_offset, rot, length_mult, alpha)
        # 0: Logo
        kf0_t = (-spacing, 0, 0, 1.0, 255)
        kf0_m = (0, 0, 0, 1.0, 255)
        kf0_b = (spacing, 0, 0, 1.0, 255)
        
        # 1: Plus +
        kf1_t = (0, 0, 90, 1.2, 255)
        kf1_m = (0, 0, 0, 1.4, 255)
        kf1_b = (0, 0, 0, 0.0, 0)
        
        # 2: Greater-than >
        kf2_t = (-spacing*0.7, spacing*0.5, 45, 0.8, 255)
        kf2_m = (0, 0, 0, 0.0, 0)
        kf2_b = (spacing*0.7, spacing*0.5, -45, 0.8, 255)
        
        # 3: Less-than <
        kf3_t = (-spacing*0.7, -spacing*0.5, -45, 0.8, 255)
        kf3_m = (0, 0, 0, 0.0, 0)
        kf3_b = (spacing*0.7, -spacing*0.5, 45, 0.8, 255)
        
        # 4: Equal =
        kf4_t = (-spacing*0.5, 0, 0, 1.0, 255)
        kf4_m = (0, 0, 0, 0.0, 0)
        kf4_b = (spacing*0.5, 0, 0, 1.0, 255)
        
        # 5: Not-equal !=
        kf5_t = (-spacing*0.4, 0, 0, 0.8, 255)
        kf5_m = (0, 0, 45, 1.4, 255)
        kf5_b = (spacing*0.4, 0, 0, 0.8, 255)
        
        keyframes = [
            (kf0_t, kf0_m, kf0_b),
            (kf1_t, kf1_m, kf1_b),
            (kf2_t, kf2_m, kf2_b),
            (kf3_t, kf3_m, kf3_b),
            (kf4_t, kf4_m, kf4_b),
            (kf5_t, kf5_m, kf5_b),
            (kf0_t, kf0_m, kf0_b)
        ]
        
        start_kf = keyframes[phase]
        end_kf = keyframes[phase+1]
        
        def interp_bar(k1, k2, t):
            return (
                lerp(k1[0], k2[0], t),
                lerp(k1[1], k2[1], t),
                lerp(k1[2], k2[2], t),
                lerp(k1[3], k2[3], t),
                lerp(k1[4], k2[4], t)
            )
            
        cur_t = interp_bar(start_kf[0], end_kf[0], t)
        cur_m = interp_bar(start_kf[1], end_kf[1], t)
        cur_b = interp_bar(start_kf[2], end_kf[2], t)
        
        painter.translate(cx, cy)
        
        def draw_bar(state, is_middle=False):
            y_off, x_off, rot, l_mult, alpha = state
            if alpha <= 0 or l_mult <= 0:
                return
            painter.save()
            painter.translate(x_off, y_off)
            painter.rotate(rot)
            
            base_color = QColor(get_brand_accent() if is_middle else BRAND_PRIMARY)
            base_color.setAlpha(int(alpha))
            painter.setBrush(base_color)
            painter.setPen(Qt.NoPen)
            
            bar_w = (mid_w if is_middle else top_w) * l_mult
            rect = QRectF(-bar_w/2, -h/2, bar_w, h)
            painter.drawRoundedRect(rect, h/2, h/2)
            painter.restore()
            
        draw_bar(cur_t, is_middle=False)
        draw_bar(cur_m, is_middle=True)
        draw_bar(cur_b, is_middle=False)
