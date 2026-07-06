from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, QRectF, Qt, pyqtProperty, pyqtSignal
from PyQt6.QtGui import QBrush, QColor, QFont, QLinearGradient, QPainter, QPainterPath


class CapsuleToggle(QWidget):
    """
    精确复刻 Vue TabsBtn 组件
    - 容器: white, border-radius: 15px
    - 滑块: 125×36px, 渐变 #3498db→#8e44ad
    - 切换带弹性滑动动画
    """
    tabChanged = pyqtSignal(int)  # 发射当前选中索引

    def __init__(self, tabs=None, parent=None):
        super().__init__(parent)
        self.tabs = tabs or [("手动", "manual"), ("自动", "gas")]
        self.active_index = 1  # 默认选中"自动"
        self._anim_x = self.active_index  # 动画用浮点位置

        # 尺寸参数 (来自 Vue: $slider-width: 125px, $slider-height: 36px)
        self.tab_w = 125
        self.tab_h = 36
        self.padding = 4
        self.radius = 15

        total_w = self.tab_w * len(self.tabs) + self.padding * 2
        total_h = self.tab_h + self.padding * 2
        self.setFixedSize(total_w, total_h)

        # 弹性滑动动画
        self._slider_anim = QPropertyAnimation(self, b"animX")
        self._slider_anim.setDuration(350)
        self._slider_anim.setEasingCurve(QEasingCurve.Type.OutBack)

    # --- Qt 属性: animX，驱动滑块位置 ---
    def _get_anim_x(self):
        return self._anim_x

    def _set_anim_x(self, val):
        self._anim_x = val
        self.update()

    animX = pyqtProperty(float, _get_anim_x, _set_anim_x)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()

        # 1) 容器背景 (Vue: rgba(129,129,129,0.8))
        p.setBrush(QColor(255, 255, 255, 204))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(0, 0, w, h, self.radius, self.radius)

        # 2) 滑块 (Vue: linear-gradient(90deg, #3498db, #8e44ad))
        sx = self.padding + self._anim_x * self.tab_w
        sy = self.padding
        sw = self.tab_w
        sh = self.tab_h

        slider_rect = QRectF(sx, sy, sw, sh)
        grad = QLinearGradient(sx, 0, sx + sw, 0)
        grad.setColorAt(0, QColor("#3498db"))
        grad.setColorAt(1, QColor("#8e44ad"))

        # 滑块阴影 (Vue: box-shadow: 0 4px 10px rgba(0,0,0,0.3))
        shadow_path = QPainterPath()
        shadow_path.addRoundedRect(slider_rect.adjusted(0, 2, 0, 2), self.radius, self.radius)
        p.setBrush(QColor(0, 0, 0, 50))
        p.drawPath(shadow_path)

        # 滑块主体
        p.setBrush(QBrush(grad))
        p.drawRoundedRect(slider_rect, self.radius, self.radius)

        # 3) 文字
        for i, (name, _) in enumerate(self.tabs):
            tx = self.padding + i * self.tab_w
            ty = self.padding
            rect = QRectF(tx, ty, self.tab_w, self.tab_h)

            if i == self.active_index:
                # Vue: active → color: white, font-size: 26px
                font = QFont("YouSheBiaoTiHei", 18)
                font.setBold(True)
                p.setFont(font)
                p.setPen(QColor("white"))
            else:
                # Vue: inactive → color: #bfbfbf, font-size: 18px
                font = QFont("YouSheBiaoTiHei", 13)
                p.setFont(font)
                p.setPen(QColor("#bfbfbf"))

            p.drawText(rect, Qt.AlignmentFlag.AlignCenter, name)

        p.end()

    def mousePressEvent(self, event):
        x = event.position().x()
        for i in range(len(self.tabs)):
            left = self.padding + i * self.tab_w
            if left <= x <= left + self.tab_w:
                if i != self.active_index:
                    self.active_index = i
                    self._slider_anim.stop()
                    self._slider_anim.setStartValue(self._anim_x)
                    self._slider_anim.setEndValue(float(i))
                    self._slider_anim.start()
                    self.tabChanged.emit(i)  # 发射信号
                break


# ==================== 自定义分割条手柄 ====================
