from PyQt6.QtWidgets import QLineEdit, QWidget
from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, QRectF, Qt, pyqtProperty, pyqtSignal
from PyQt6.QtGui import QColor, QPainter

from .numeric_keypad import NumericKeypad
from .virtual_keyboard import FullVirtualKeyboard


class ClickableLineEdit(QLineEdit):
    """点击弹出特定键盘的输入框"""
    valueChanged = pyqtSignal(str)

    def __init__(self, value="", keyboard_type="numeric", parent=None):
        super().__init__(str(value), parent)
        self.keyboard_type = keyboard_type # "numeric" 或 "full"
        self.setReadOnly(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._apply_style()

    def _apply_style(self):
        self.setStyleSheet("""
            QLineEdit {
                border: 1px solid #d9d9d9;
                border-radius: 4px;
                padding: 4px 8px;
                background: white;
                font-size: 14px;
                color: #1890ff;
                font-weight: bold;
            }
            QLineEdit:hover {
                border-color: #40a9ff;
            }
        """)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.keyboard_type == "numeric":
                pad = NumericKeypad(self.text(), self.window())
            else:
                pad = FullVirtualKeyboard(self.text(), self.window())
            
            if pad.exec():
                new_val = pad.get_value()
                if new_val != self.text():
                    self.setText(new_val)
                    self.valueChanged.emit(new_val)
        super().mousePressEvent(event)


class SwitchButton(QWidget):
    """自定义切换开关 (Switch)"""
    toggled = pyqtSignal(bool)

    def __init__(self, parent=None, active_color="#52c41a", inactive_color="#d9d9d9"):
        super().__init__(parent)
        self.setFixedSize(50, 26)
        self._active = False
        self._active_color = QColor(active_color)
        self._inactive_color = QColor(inactive_color)
        
        # 动画属性
        self._thumb_pos = 3.0 # 左边距
        self._anim = QPropertyAnimation(self, b"thumb_pos")
        self._anim.setDuration(200)
        self._anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

    def _get_thumb_pos(self): return self._thumb_pos
    def _set_thumb_pos(self, pos):
        self._thumb_pos = pos
        self.update()
    thumb_pos = pyqtProperty(float, _get_thumb_pos, _set_thumb_pos)

    def is_active(self): return self._active

    def set_active(self, active, animate=True):
        if self._active == active: return
        self._active = active
        target = 27.0 if active else 3.0
        if animate:
            self._anim.stop()
            self._anim.setEndValue(target)
            self._anim.start()
        else:
            self._thumb_pos = target
            self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.set_active(not self._active)
            self.toggled.emit(self._active)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 轨道
        color = self._active_color if self._active else self._inactive_color
        p.setBrush(color)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(0, 0, self.width(), self.height(), self.height()/2, self.height()/2)
        
        # 滑块
        p.setBrush(Qt.GlobalColor.white)
        p.drawEllipse(QRectF(self._thumb_pos, 3, 20, 20))

