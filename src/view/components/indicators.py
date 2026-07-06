from PyQt6.QtWidgets import QSizePolicy, QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont, QPainter


class VerticalProgressBar(QWidget):
    """
    竖向进度条，百分比浮动在底部并根据背景自动计算差值颜色
    """
    def __init__(self, value, color, bg_color, parent=None):
        super().__init__(parent)
        self.value = value
        self.color = QColor(color)
        self.bg_color = QColor(bg_color)
        self.setMinimumWidth(40)
        self.setMinimumHeight(80)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()

        # 1. 绘制背景
        p.setBrush(self.bg_color)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(0, 0, w, h, 4, 4)

        # 2. 绘制填充 (从底部向上)
        fill_h = int((h - 4) * (self.value / 100.0))
        p.setBrush(self.color)
        p.drawRoundedRect(2, h - fill_h - 2, w - 4, fill_h, 3, 3)

        # 3. 绘制百分比文字 (核心：差值计算保证可见)
        font = QFont("YouSheBiaoTiHei", 12)
        font.setBold(True)
        p.setFont(font)
        
        # 使用 Difference 模式：白色在绿色/红色背景上会产生对比色
        p.setCompositionMode(QPainter.CompositionMode.CompositionMode_Difference)
        p.setPen(QColor(255, 255, 255))  # 用白色进行差值计算
        
        text = f"{self.value}%"
        # 居中绘制在底部
        fm = p.fontMetrics()
        tx = (w - fm.horizontalAdvance(text)) / 2
        ty = h - 10  # 距离底部10px
        p.drawText(int(tx), int(ty), text)
        
        p.end()


# ==================== 自定义数字键盘对话框 ====================


class StatusLamp(QWidget):
    """状态指示灯"""
    def __init__(self, color="#ccc", size=16, parent=None):
        super().__init__(parent)
        self.color = QColor(color)
        self.setFixedSize(size, size)

    def set_active(self, active=True):
        self.color = QColor("#52c41a") if active else QColor("#ccc")
        self.update()

    def set_error(self, error=True):
        self.color = QColor("#ff4d4f") if error else QColor("#ccc")
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(self.color)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(0, 0, self.width(), self.height())
