import math
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QVariantAnimation, QRectF
from PySide6.QtGui import QPainter, QColor
from theme import BRAND_PRIMARY, get_brand_accent, BRAND_PANEL

class MorphingLogo(QWidget):
    def __init__(self, parent=None, size=64, duration=5000):
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
        
        # 8 phases: Logo → + → * → > → < → = → != → - → Logo
        num_phases = 8
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
        
        # 0: Logo (E)
        kf0_t = (-s, 0, 0, 1.0, 255)
        kf0_m = (0, 0, 0, 1.0, 255)
        kf0_b = (s, 0, 0, 1.0, 255)
        
        # 1: + (Plus)
        kf1_t = (0, 0, 90, 1.2, 255)
        kf1_m = (0, 0, 0, 1.4, 255)
        kf1_b = (0, 0, 0, 0.0, 0)
        
        # 2: * (Asterisk)
        kf2_t = (0, 0, 60, 1.4, 255)
        kf2_m = (0, 0, 0, 1.4, 255)
        kf2_b = (0, 0, -60, 1.4, 255)
        
        # 3: > (Greater-than)
        kf3_t = (-s*0.7, s*0.5, 45, 0.8, 255)
        kf3_m = (0, 0, 0, 0.0, 0)
        kf3_b = (s*0.7, s*0.5, -45, 0.8, 255)
        
        # 4: < (Less-than)
        kf4_t = (-s*0.7, -s*0.5, -45, 0.8, 255)
        kf4_m = (0, 0, 0, 0.0, 0)
        kf4_b = (s*0.7, -s*0.5, 45, 0.8, 255)
        
        # 5: = (Equal)
        kf5_t = (-s*0.5, 0, 0, 1.0, 255)
        kf5_m = (0, 0, 0, 0.0, 0)
        kf5_b = (s*0.5, 0, 0, 1.0, 255)
        
        # 6: != (Not-equal)
        kf6_t = (-s*0.4, 0, 0, 0.8, 255)
        kf6_m = (0, 0, 45, 1.4, 255)
        kf6_b = (s*0.4, 0, 0, 0.8, 255)
        
        # 7: - (Minus)
        kf7_t = (0, 0, 0, 0.0, 0)
        kf7_m = (0, 0, 0, 1.0, 255)
        kf7_b = (0, 0, 0, 0.0, 0)
        
        keyframes = [
            (kf0_t, kf0_m, kf0_b),  # Logo
            (kf1_t, kf1_m, kf1_b),  # +
            (kf2_t, kf2_m, kf2_b),  # *
            (kf3_t, kf3_m, kf3_b),  # >
            (kf4_t, kf4_m, kf4_b),  # <
            (kf5_t, kf5_m, kf5_b),  # =
            (kf6_t, kf6_m, kf6_b),  # !=
            (kf7_t, kf7_m, kf7_b),  # -
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


class GlowingLogo(QWidget):
    """A fast, elegant 'sweeping light' animation for the splash screen."""
    def __init__(self, parent=None, size=64, duration=1500):
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
        from PySide6.QtGui import QLinearGradient, QPainterPath
        
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
        
        painter.translate(cx, cy)
        
        # Create a path for the logo bars so we can mask the glow
        logo_path = QPainterPath()
        
        # Top
        logo_path.addRoundedRect(QRectF(-top_w/2, -spacing - h/2, top_w, h), h/2, h/2)
        # Middle
        logo_path.addRoundedRect(QRectF(-mid_w/2, -h/2, mid_w, h), h/2, h/2)
        # Bottom
        logo_path.addRoundedRect(QRectF(-top_w/2, spacing - h/2, top_w, h), h/2, h/2)
        
        # Draw the base logo
        painter.setPen(Qt.NoPen)
        # We need to draw them with their respective colors
        painter.setBrush(QColor(BRAND_PRIMARY))
        painter.drawRoundedRect(QRectF(-top_w/2, -spacing - h/2, top_w, h), h/2, h/2)
        painter.drawRoundedRect(QRectF(-top_w/2, spacing - h/2, top_w, h), h/2, h/2)
        
        painter.setBrush(QColor(get_brand_accent()))
        painter.drawRoundedRect(QRectF(-mid_w/2, -h/2, mid_w, h), h/2, h/2)
        
        # Draw the sweeping glow
        # The glow moves from top-left to bottom-right across the logo
        painter.setClipPath(logo_path)
        
        # Calculate gradient position based on progress
        # We want the glow to sweep fully across, so start before the logo and end after
        offset = (self._progress * 3.0) - 1.0  # Range -1.0 to +2.0
        
        y_pos = offset * self.height() - (self.height() / 2)
        
        # Tilted gradient
        grad = QLinearGradient(0, y_pos - 20, 0, y_pos + 20)
        grad.setColorAt(0.0, QColor(255, 255, 255, 0))
        grad.setColorAt(0.5, QColor(255, 255, 255, 180)) # Bright center
        grad.setColorAt(1.0, QColor(255, 255, 255, 0))
        
        # Add a slight tilt to the gradient
        painter.rotate(25)
        painter.setBrush(grad)
        painter.drawRect(-self.width(), -self.height(), self.width()*2, self.height()*2)
        painter.rotate(-25)

