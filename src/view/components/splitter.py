from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPainter, QPen


class GripSplitterHandle(QWidget):
    """带抓手纹路的分割条手柄，明确提示可拖拽"""
    def __init__(self, orientation, parent=None):
        super().__init__(parent)
        self.orientation = orientation
        self._hovered = False
        self.setFixedHeight(12)
        self.setCursor(Qt.CursorShape.SplitVCursor)
        self.setMouseTracking(True)

    def enterEvent(self, event):
        self._hovered = True
        self.update()

    def leaveEvent(self, event):
        self._hovered = False
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()

        # 背景
        bg = QColor("#597EF7") if self._hovered else QColor("#e0e0e0")
        p.setBrush(bg)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(0, 0, w, h, 4, 4)

        # 三条横纹线 (抓手标识)
        line_color = QColor("white") if self._hovered else QColor("#aaa")
        pen = QPen(line_color, 1.5)
        p.setPen(pen)
        cx = w / 2
        grip_w = 30  # 纹线宽度
        for dy in [-2.5, 0, 2.5]:
            y = h / 2 + dy
            p.drawLine(int(cx - grip_w / 2), int(y), int(cx + grip_w / 2), int(y))

        # 上下箭头
        arrow_color = QColor("white") if self._hovered else QColor("#999")
        p.setPen(QPen(arrow_color, 1.5))
        # 上箭头
        ax = cx - grip_w / 2 - 12
        p.drawLine(int(ax), int(h / 2), int(ax - 4), int(h / 2 - 3))
        p.drawLine(int(ax), int(h / 2), int(ax + 4), int(h / 2 - 3))
        # 下箭头
        ax2 = cx + grip_w / 2 + 12
        p.drawLine(int(ax2), int(h / 2), int(ax2 - 4), int(h / 2 + 3))
        p.drawLine(int(ax2), int(h / 2), int(ax2 + 4), int(h / 2 + 3))

        p.end()


# ==================== 自定义竖向进度条 ====================
