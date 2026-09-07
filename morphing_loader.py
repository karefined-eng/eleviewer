import math
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QVariantAnimation, QRectF, QPointF
from PySide6.QtGui import QPainter, QPainterPath, QColor, QPen

class MorphingHamburger(QWidget):
    def __init__(self, parent=None, size=64, color="#2563eb", duration=3000):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self._color = QColor(color)
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
        
        cx, cy = self.width() / 2, self.height() / 2
        w = self.width() * 0.6
        h = self.height() * 0.08
        spacing = self.height() * 0.2
        
        # Base geometries
        # Hamburger: 
        # t_y = cy - spacing, rot = 0, len = w, alpha = 255
        # m_y = cy, rot = 0, len = w, alpha = 255
        # b_y = cy + spacing, rot = 0, len = w, alpha = 255
        
        p = self._progress
        
        # We divide 0.0 to 1.0 into 4 phases:
        # Phase 0: 0.00-0.25 -> Hamburger to >
        # Phase 1: 0.25-0.50 -> > to <
        # Phase 2: 0.50-0.75 -> < to !=
        # Phase 3: 0.75-1.00 -> != to Hamburger
        
        # For smooth pauses at the shapes, we use an easing curve or map the progress
        # Let's map local progress lp to be 0 for the first 20% of the phase, then ease to 1 for the rest 80%.
        
        phase = int(p * 4)
        if phase > 3: phase = 3
        
        local_p = (p * 4) - phase
        # Smooth step for local_p: hold at 0 for a bit, then move
        if local_p < 0.2:
            t = 0.0
        elif local_p > 0.8:
            t = 1.0
        else:
            t = (local_p - 0.2) / 0.6
            # ease in out cubic
            if t < 0.5:
                t = 4 * t * t * t
            else:
                t = 1 - math.pow(-2 * t + 2, 3) / 2
                
        def lerp(a, b, t):
            return a + (b - a) * t

        # Define the 4 keyframes: (y_offset, x_offset, rot, length_mult, alpha) for Top, Mid, Bot
        # 0: Hamburger
        kf0_t = (-spacing, 0, 0, 1.0, 255)
        kf0_m = (0, 0, 0, 1.0, 255)
        kf0_b = (spacing, 0, 0, 1.0, 255)
        
        # 1: Greater-than >
        # Top tilts down, right tip touches center-right
        kf1_t = (-spacing*0.7, spacing*0.5, 45, 0.8, 255)
        kf1_m = (0, 0, 0, 0.0, 0)
        kf1_b = (spacing*0.7, spacing*0.5, -45, 0.8, 255)
        
        # 2: Less-than <
        kf2_t = (-spacing*0.7, -spacing*0.5, -45, 0.8, 255)
        kf2_m = (0, 0, 0, 0.0, 0)
        kf2_b = (spacing*0.7, -spacing*0.5, 45, 0.8, 255)
        
        # 3: Not-equal !=
        kf3_t = (-spacing*0.4, 0, 0, 0.8, 255)
        kf3_m = (0, 0, 45, 1.2, 255)
        kf3_b = (spacing*0.4, 0, 0, 0.8, 255)
        
        keyframes = [
            (kf0_t, kf0_m, kf0_b),
            (kf1_t, kf1_m, kf1_b),
            (kf2_t, kf2_m, kf2_b),
            (kf3_t, kf3_m, kf3_b),
            (kf0_t, kf0_m, kf0_b) # wrap around
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
        
        def draw_bar(state):
            y_off, x_off, rot, l_mult, alpha = state
            if alpha <= 0 or l_mult <= 0:
                return
            painter.save()
            painter.translate(x_off, y_off)
            painter.rotate(rot)
            
            c = QColor(self._color)
            c.setAlpha(int(alpha))
            painter.setBrush(c)
            painter.setPen(Qt.NoPen)
            
            bar_w = w * l_mult
            rect = QRectF(-bar_w/2, -h/2, bar_w, h)
            painter.drawRoundedRect(rect, h/2, h/2)
            painter.restore()
            
        draw_bar(cur_t)
        draw_bar(cur_m)
        draw_bar(cur_b)
