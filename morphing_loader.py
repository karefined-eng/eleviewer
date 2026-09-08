import math
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QVariantAnimation, QRectF
from PySide6.QtGui import QPainter, QColor
from theme import BRAND_PRIMARY, get_brand_accent, BRAND_PANEL

class MorphingLogo(QWidget):
    def __init__(self, parent=None, size=64, duration=6500):
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
        
        # 10 phases: Logo → Э → л → е → В → и → е → в → е → р → Logo
        num_phases = 10
        phase = int(p * num_phases)
        if phase > num_phases - 1: phase = num_phases - 1
        
        local_p = (p * num_phases) - phase
        # Ease: hold at start/end, cubic in-out in middle
        if local_p < 0.15:
            t = 0.0
        elif local_p > 0.85:
            t = 1.0
        else:
            t = (local_p - 0.15) / 0.7
            if t < 0.5:
                t = 4 * t * t * t
            else:
                t = 1 - math.pow(-2 * t + 2, 3) / 2
                
        def lerp(a, b, t):
            return a + (b - a) * t

        # Each keyframe: (y_offset, x_offset, rotation, length_mult, alpha)
        s = spacing  # shorthand
        
        # 0: Logo — the EleViewer "E" (three horizontal bars)
        kf0_t = (-s,   0,        0,   1.0, 255)
        kf0_m = ( 0,   0,        0,   1.0, 255)
        kf0_b = ( s,   0,        0,   1.0, 255)
        
        # 1: Э — reversed E, bars shift right slightly, middle shorter
        kf1_t = (-s,   s*0.15,   0,   0.9, 255)
        kf1_m = ( 0,  -s*0.1,    0,   0.65, 255)
        kf1_b = ( s,   s*0.15,   0,   0.9, 255)
        
        # 2: л — Lambda / tent shape (two legs meeting at top)
        kf2_t = ( 0,  -s*0.5,   65,   1.1, 255)
        kf2_m = ( 0,   0,        0,   0.0,   0)
        kf2_b = ( 0,   s*0.5,  -65,   1.1, 255)
        
        # 3: е — three horizontal bars (same as logo — brand flash!)
        kf3_t = (-s,   0,        0,   1.0, 255)
        kf3_m = ( 0,   0,        0,   1.0, 255)
        kf3_b = ( s,   0,        0,   1.0, 255)
        
        # 4: В — vertical stem + two horizontal bumps (like B)
        kf4_t = ( 0,  -s*0.4,   90,   1.2, 255)
        kf4_m = (-s*0.4, s*0.2,  0,   0.7, 255)
        kf4_b = ( s*0.4, s*0.2,  0,   0.7, 255)
        
        # 5: и — two verticals + diagonal (reversed N)
        kf5_t = ( 0,  -s*0.5,   90,   1.1, 255)
        kf5_m = ( 0,   0,      -40,   1.3, 255)
        kf5_b = ( 0,   s*0.5,   90,   1.1, 255)
        
        # 6: е — three horizontal bars again (second brand flash)
        kf6_t = (-s,   0,        0,   1.0, 255)
        kf6_m = ( 0,   0,        0,   1.0, 255)
        kf6_b = ( s,   0,        0,   1.0, 255)
        
        # 7: в — vertical stem + two smaller bumps (lowercase в)
        kf7_t = ( 0,  -s*0.3,   90,   1.0, 255)
        kf7_m = (-s*0.3, s*0.15, 0,   0.55, 255)
        kf7_b = ( s*0.3, s*0.15, 0,   0.55, 255)
        
        # 8: е — three horizontal bars (third brand flash)
        kf8_t = (-s,   0,        0,   1.0, 255)
        kf8_m = ( 0,   0,        0,   1.0, 255)
        kf8_b = ( s,   0,        0,   1.0, 255)
        
        # 9: р — vertical stem + top-right arm (like P)
        kf9_t = (-s*0.4, s*0.3,  0,   0.7, 255)
        kf9_m = ( 0,     0,      0,   0.0,   0)
        kf9_b = ( 0,    -s*0.3, 90,   1.2, 255)
        
        keyframes = [
            (kf0_t, kf0_m, kf0_b),  # Logo
            (kf1_t, kf1_m, kf1_b),  # Э
            (kf2_t, kf2_m, kf2_b),  # л
            (kf3_t, kf3_m, kf3_b),  # е
            (kf4_t, kf4_m, kf4_b),  # В
            (kf5_t, kf5_m, kf5_b),  # и
            (kf6_t, kf6_m, kf6_b),  # е
            (kf7_t, kf7_m, kf7_b),  # в
            (kf8_t, kf8_m, kf8_b),  # е
            (kf9_t, kf9_m, kf9_b),  # р
            (kf0_t, kf0_m, kf0_b),  # Logo (loop)
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

