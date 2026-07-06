from PyQt6.QtWidgets import (
    QWidget, QSizePolicy, QDialog, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QGridLayout, QLineEdit, QFrame, QCalendarWidget,
    QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QRectF, QEasingCurve, QPropertyAnimation, pyqtProperty, pyqtSignal, QSize, QDate
from PyQt6.QtGui import QColor, QFont, QPainter, QLinearGradient, QPen, QBrush, QPainterPath


# ==================== 自定义胶囊切换组件 ====================
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
class NumericKeypad(QDialog):
    """
    工业级数字键盘对话框
    """
    def __init__(self, initial_value="", parent=None):
        super().__init__(parent)
        self.setWindowTitle("数字输入")
        self.setFixedSize(320, 550) # 同步高度
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.value = initial_value
        self.is_first_input = True # 标记是否为打开后的第一次输入
        self._build_ui()

    def _build_ui(self):
        container = QFrame(self)
        container.setObjectName("KeypadContainer")
        container.setFixedSize(320, 550) # 维持高度，确保空间充足
        container.setStyleSheet("""
            #KeypadContainer {
                background: white;
                border: 2px solid #597EF7;
                border-radius: 12px;
            }
            QPushButton {
                background: #F8F9FA;
                border: 1px solid #D9D9D9;
                border-radius: 8px;
                font-size: 22px;
                font-weight: bold;
                color: #262626;
                padding: 0;
                margin: 0; /* 移除 margin，靠 spacing 控制 */
            }
            QPushButton:pressed {
                background: #E6F4FF;
                border-color: #1890FF;
            }
            #FuncBtn {
                background: #597EF7;
                color: white;
                border: none;
            }
            #FuncBtn:pressed {
                background: #40A9FF;
            }
            #ClearBtn {
                background: #FFF1F0;
                color: #FF4D4F;
                border: 1px solid #FFA39E;
            }
            #ClearBtn:pressed {
                background: #FFCCC7;
            }
        """)
        
        main_lay = QVBoxLayout(container)
        main_lay.setContentsMargins(20, 20, 20, 20)
        main_lay.setSpacing(15)

        # 显示区域
        self.display = QLineEdit(self.value)
        self.display.setReadOnly(True)
        self.display.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.display.setFixedHeight(65)
        self.display.setStyleSheet("""
            font-size: 36px;
            font-weight: bold;
            color: #1890FF;
            background: #FAFAFA;
            border: 1px solid #D9D9D9;
            border-radius: 6px;
            padding: 0 15px;
        """)
        main_lay.addWidget(self.display)

        # 键盘格
        grid_widget = QWidget()
        grid = QGridLayout(grid_widget)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(10) # 统一 10px 间距

        btns = [
            ('7', 0, 0), ('8', 0, 1), ('9', 0, 2),
            ('4', 1, 0), ('5', 1, 1), ('6', 1, 2),
            ('1', 2, 0), ('2', 2, 1), ('3', 2, 2),
            ('.', 3, 0), ('0', 3, 1), ('←', 3, 2)
        ]

        for text, r, c in btns:
            btn = QPushButton(text)
            btn.setFixedSize(85, 60) # 固定按钮大小确保整齐
            btn.clicked.connect(lambda ch, t=text: self._on_key_clicked(t))
            grid.addWidget(btn, r, c)

        main_lay.addWidget(grid_widget)

        # 底部操作
        action_lay = QVBoxLayout()
        action_lay.setSpacing(10)
        
        clear_btn = QPushButton("全部清空 (Clear)")
        clear_btn.setObjectName("ClearBtn")
        clear_btn.setFixedHeight(45)
        clear_btn.setStyleSheet("font-size: 16px;")
        clear_btn.clicked.connect(lambda: self._on_key_clicked('C'))

        ctrl_lay = QHBoxLayout()
        ctrl_lay.setSpacing(10)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.setFixedHeight(50)
        cancel_btn.clicked.connect(self.reject)
        
        ok_btn = QPushButton("确认输入")
        ok_btn.setObjectName("FuncBtn")
        ok_btn.setFixedHeight(50)
        ok_btn.clicked.connect(self.accept)
        
        ctrl_lay.addWidget(cancel_btn, 1)
        ctrl_lay.addWidget(ok_btn, 1)

        action_lay.addWidget(clear_btn)
        action_lay.addLayout(ctrl_lay)
        
        main_lay.addLayout(action_lay)

    def _on_key_clicked(self, key):
        if key == 'C':
            self.value = ""
            self.is_first_input = False
        elif key == '←':
            self.value = self.value[:-1]
            self.is_first_input = False
        elif key == '.':
            if self.is_first_input:
                self.value = "0."
            elif '.' not in self.value:
                self.value += '.'
            self.is_first_input = False
        else:
            # 输入数字
            if self.is_first_input:
                self.value = key
            else:
                self.value += key
            self.is_first_input = False
        
        self.display.setText(self.value)

    def get_value(self):
        return self.value


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


try:
    from Pinyin2Hanzi import DefaultDagParams, dag, all_pinyin
    _PINYIN_ENGINE_AVAILABLE = True
except ImportError:
    _PINYIN_ENGINE_AVAILABLE = False


class FullVirtualKeyboard(QDialog):
    """
    全功能虚拟键盘 (QWERTY + 数字 + 中法拼音输入)
    """
    RECENT_USERS = []  # 静态变量，记录最近输入的操作员

    def __init__(self, initial_value="", parent=None):
        super().__init__(parent)
        self.setWindowTitle("标准输入")
        self.setFixedSize(850, 480) # 缩减高度以适应内容
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.value = str(initial_value)
        self.pinyin_buffer = ""
        self.candidates = []
        self.candidate_page = 0
        self.page_size = 8
        self.is_caps = False
        self.is_first_input = True
        self.is_chinese_mode = True 
        
        if _PINYIN_ENGINE_AVAILABLE:
            self.dag_params = DefaultDagParams()
            self.all_pinyins = set(all_pinyin())
        else:
            self.dag_params = None

        self._build_ui()

    def _build_ui(self):
        container = QFrame(self)
        container.setObjectName("KbContainer")
        container.setFixedSize(850, 480)
        container.setStyleSheet("""
            #KbContainer {
                background: #F0F2F5;
                border: 2px solid #597EF7;
                border-radius: 12px;
            }
            QPushButton {
                background: white;
                border: 1px solid #D9D9D9;
                border-radius: 6px;
                font-size: 18px;
                font-weight: bold;
                min-height: 50px;
                color: #333;
            }
            QPushButton:pressed {
                background: #E6F4FF;
                border-color: #1890FF;
            }
            #ActionBtn {
                background: #597EF7;
                color: white;
                border: none;
            }
            #ClearBtn {
                background: #FFF1F0;
                color: #FF4D4F;
                border: 1px solid #FFA39E;
            }
            .CandidateBtn {
                background: transparent;
                border: none;
                color: #1890FF;
                font-size: 22px;
                padding: 0 10px;
                min-height: 40px;
            }
            .CandidateBtn:hover {
                background: #E6F4FF;
                border-radius: 4px;
            }
            #PageBtn {
                background: #E8E8E8;
                color: #666;
                font-size: 20px;
                min-width: 40px;
                min-height: 40px;
                max-width: 40px;
                border: none;
                border-radius: 20px;
            }
        """)
        
        main_lay = QVBoxLayout(container)
        main_lay.setContentsMargins(20, 15, 20, 15)
        main_lay.setSpacing(8)

        # 1. 顶部显示内容
        self.display = QLineEdit(self.value)
        self.display.setReadOnly(True)
        self.display.setFixedHeight(60)
        self.display.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            color: #1890FF;
            background: white;
            border: 1px solid #D9D9D9;
            border-radius: 6px;
            padding: 0 15px;
        """)
        main_lay.addWidget(self.display)

        main_lay.addWidget(self.display)

        # 1.5 最近操作员标签 (快捷输入)
        self.recent_area = QWidget()
        self.recent_lay = QHBoxLayout(self.recent_area)
        self.recent_lay.setContentsMargins(0, 0, 0, 0)
        self.recent_lay.setSpacing(10)
        self.recent_lay.addStretch()
        main_lay.addWidget(self.recent_area)

        # 2. 拼音显示 & 候选词栏 (紧凑排列)
        mid_container = QWidget()
        mid_lay = QVBoxLayout(mid_container)
        mid_lay.setContentsMargins(5, 0, 5, 0)
        mid_lay.setSpacing(2)

        self.pinyin_display = QLabel("")
        self.pinyin_display.setStyleSheet("color: #888; font-size: 16px; font-weight: bold;")
        mid_lay.addWidget(self.pinyin_display)

        # 候选词区域带翻页
        self.candidate_area = QWidget()
        self.candidate_area.setFixedHeight(40)
        self.candidate_lay = QHBoxLayout(self.candidate_area)
        self.candidate_lay.setContentsMargins(0, 0, 0, 0)
        self.candidate_lay.setSpacing(5)
        
        # 翻页按钮 - 左
        self.prev_btn = QPushButton("<")
        self.prev_btn.setObjectName("PageBtn")
        self.prev_btn.clicked.connect(self._prev_page)
        self.prev_btn.hide()
        
        # 翻页按钮 - 右
        self.next_btn = QPushButton(">")
        self.next_btn.setObjectName("PageBtn")
        self.next_btn.clicked.connect(self._next_page)
        self.next_btn.hide()

        # 候选词容器
        self.cand_container = QWidget()
        self.cand_lay = QHBoxLayout(self.cand_container)
        self.cand_lay.setContentsMargins(0, 0, 0, 0)
        self.cand_lay.setSpacing(2)
        self.cand_lay.addStretch()

        self.candidate_lay.addWidget(self.prev_btn)
        self.candidate_lay.addWidget(self.cand_container, 1)
        self.candidate_lay.addWidget(self.next_btn)
        
        mid_lay.addWidget(self.candidate_area)
        main_lay.addWidget(mid_container)

        # 3. 键盘区域
        rows_lay = QVBoxLayout()
        rows_lay.setSpacing(6)

        # 第一行: 数字
        r1 = QHBoxLayout()
        for k in "1234567890":
            r1.addWidget(self._create_btn(k))
        btn_back = self._create_btn("←", True)
        btn_back.clicked.connect(lambda: self._handle_key("←"))
        r1.addWidget(btn_back)
        rows_lay.addLayout(r1)

        # 第二行: Q-P
        r2 = QHBoxLayout()
        for k in "QWERTYUIOP":
            r2.addWidget(self._create_btn(k))
        rows_lay.addLayout(r2)

        # 第三行: A-L
        r3 = QHBoxLayout()
        r3.addSpacing(25)
        for k in "ASDFGHJKL":
            r3.addWidget(self._create_btn(k))
        r3.addSpacing(25)
        rows_lay.addLayout(r3)

        # 第四行: Caps, Z-M, Clear
        r4 = QHBoxLayout()
        self.caps_btn = self._create_btn("Caps", True)
        self.caps_btn.setFixedWidth(80)
        self.caps_btn.clicked.connect(self._toggle_caps)
        r4.addWidget(self.caps_btn)
        for k in "ZXCVBNM":
            r4.addWidget(self._create_btn(k))
        
        btn_clear = self._create_btn("Clear", False)
        btn_clear.setObjectName("ClearBtn")
        btn_clear.setFixedWidth(80)
        btn_clear.clicked.connect(lambda: self._handle_key("C"))
        r4.addWidget(btn_clear)
        rows_lay.addLayout(r4)

        # 第五行: 切换, 空格, 取消, 确定
        r5 = QHBoxLayout()
        self.lang_btn = self._create_btn("中文", True)
        self.lang_btn.setFixedWidth(120)
        self.lang_btn.clicked.connect(self._toggle_lang)
        self.lang_btn.setStyleSheet("background: #BAE7FF;") 
        r5.addWidget(self.lang_btn)
        
        btn_space = self._create_btn("Space", True)
        btn_space.clicked.connect(lambda: self._handle_key(" "))
        r5.addWidget(btn_space, 4)

        btn_cancel = self._create_btn("取消")
        btn_cancel.clicked.connect(self.reject)
        r5.addWidget(btn_cancel, 1)

        btn_ok = self._create_btn("确认输入", False)
        btn_ok.setObjectName("ActionBtn")
        btn_ok.clicked.connect(self._commit_and_accept)
        r5.addWidget(btn_ok, 2)
        
        rows_lay.addLayout(r5)
        main_lay.addLayout(rows_lay)

    def _commit_and_accept(self):
        """确认输入前，将拼音缓冲区残留内容追加到 value"""
        if self.pinyin_buffer:
            self.value += self.pinyin_buffer
            self.pinyin_buffer = ""
        self.accept()

    def _create_btn(self, text, is_special=False):
        btn = QPushButton(text)
        if is_special:
            btn.setStyleSheet(btn.styleSheet() + " background: #F5F5F5;")
        
        if len(text) == 1 and text not in "←C":
            btn.clicked.connect(lambda: self._handle_key(text))
        return btn

    def _handle_key(self, key):
        if key == "C":
            self.value = ""
            self.pinyin_buffer = ""
        elif key == "←":
            if self.pinyin_buffer:
                self.pinyin_buffer = self.pinyin_buffer[:-1]
            else:
                self.value = self.value[:-1]
        elif key == " ":
            if self.candidates:
                # 空格选择当前页首个词
                start = self.candidate_page * self.page_size
                if start < len(self.candidates):
                    self._on_candidate_selected(self.candidates[start])
                    return
            self.value += " "
        else:
            char = key
            if not self.is_caps and char.isalpha():
                char = char.lower()
            
            # 中文模式核心逻辑
            if self.is_chinese_mode and char.isalpha():
                if self.is_first_input:
                    self.value = "" # 输入中文前清空默认值
                self.pinyin_buffer += char
                self.candidate_page = 0 # 重置页码
            else:
                if self.is_first_input:
                    self.value = char
                else:
                    self.value += char
        
        self.is_first_input = False
        self._update_display()

    def _update_display(self):
        self.display.setText(self.value)
        self.pinyin_display.setText(self.pinyin_buffer)
        self._refresh_candidates_data() # 仅在拼音变化时重新生成数据

    def _refresh_candidates_data(self):
        self.candidates = []
        if not self.pinyin_buffer or not _PINYIN_ENGINE_AVAILABLE:
            self._update_candidate_ui()
            return

        try:
            pinyin_list = self._split_pinyin(self.pinyin_buffer)
            if pinyin_list:
                # 获取更多候选词（如30个）以供翻页
                result = dag(self.dag_params, pinyin_list, path_num=30)
                self.candidates = ["".join(item.path) for item in result]
        except Exception as e:
            print(f"Pinyin query error: {e}")
        
        self._update_candidate_ui()

    def _update_candidate_ui(self):
        # 清除旧候选词
        while self.cand_lay.count() > 1:
            item = self.cand_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not self.candidates:
            self.prev_btn.hide()
            self.next_btn.hide()
            return

        # 分页逻辑
        start = self.candidate_page * self.page_size
        end = start + self.page_size
        current_page_cands = self.candidates[start:end]

        # 显示
        for cand in current_page_cands:
            btn = QPushButton(cand)
            btn.setProperty("class", "CandidateBtn")
            btn.setStyleSheet("background: transparent; border: none; color: #1890FF; font-size: 22px; font-weight: bold;")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda ch, c=cand: self._on_candidate_selected(c))
            self.cand_lay.insertWidget(self.cand_lay.count() - 1, btn)

        # 翻页按钮可见性
        self.prev_btn.setVisible(self.candidate_page > 0)
        self.next_btn.setVisible(len(self.candidates) > end)

    def _next_page(self):
        self.candidate_page += 1
        self._update_candidate_ui()

    def _prev_page(self):
        if self.candidate_page > 0:
            self.candidate_page -= 1
            self._update_candidate_ui()

    def _split_pinyin(self, s):
        """简单贪婪拼音切分"""
        res = []
        idx = 0
        while idx < len(s):
            found = False
            for length in range(max(6, len(s)-idx), 0, -1):
                part = s[idx : idx + length]
                if part in self.all_pinyins:
                    res.append(part)
                    idx += length
                    found = True
                    break
            if not found:
                res.append(s[idx])
                idx += 1
        return res

    def _on_candidate_selected(self, cand):
        self.value += cand
        self.pinyin_buffer = ""
        self.candidate_page = 0
        self._update_display()

    def _toggle_caps(self):
        self.is_caps = not self.is_caps
        self.caps_btn.setStyleSheet("background: #BAE7FF; border-color: #69C0FF;" if self.is_caps else "background: #F5F5F5;")
        
    def _toggle_lang(self):
        self.is_chinese_mode = not self.is_chinese_mode
        self.pinyin_buffer = "" 
        self.candidate_page = 0
        self.lang_btn.setText("中文" if self.is_chinese_mode else "English")
        self.lang_btn.setStyleSheet("background: #BAE7FF;" if self.is_chinese_mode else "background: #F5F5F5;")
        self._update_display()

    def showEvent(self, event):
        super().showEvent(event)
        self._update_recent_ui()

    def _update_recent_ui(self):
        """刷新最近操作员显示"""
        # 清空旧内容 (保留最后的 stretch)
        while self.recent_lay.count() > 1:
            item = self.recent_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # 添加标题文本
        if self.RECENT_USERS:
            title = QLabel("最近输入:")
            title.setStyleSheet("color: #888; font-size: 14px; font-weight: bold;")
            self.recent_lay.insertWidget(0, title)

        # 添加名字标签
        for name in reversed(self.RECENT_USERS):
            btn = QPushButton(name)
            btn.setStyleSheet("""
                QPushButton {
                    background: #E6F4FF; color: #1890FF; border: 1px solid #91CAFF;
                    border-radius: 4px; padding: 2px 10px; font-size: 16px;
                    min-height: 25px;
                }
                QPushButton:hover { background: #BAE7FF; }
            """)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda ch, n=name: self._on_recent_clicked(n))
            self.recent_lay.insertWidget(self.recent_lay.count() - 1, btn)

    def _on_recent_clicked(self, name):
        self.value = name
        self.is_first_input = False
        self._update_display()

    def accept(self):
        # 点击确定时，记录最近使用的操作员
        val = self.display.text().strip()
        if val and val not in self.RECENT_USERS:
            self.RECENT_USERS.append(val)
            if len(self.RECENT_USERS) > 5:
                self.RECENT_USERS.pop(0)
        super().accept()

    def get_value(self):
        return self.value


class MonthView(QWidget):
    """单月日历视图"""
    dateClicked = pyqtSignal(QDate)
    hoveredDateChanged = pyqtSignal(QDate)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_date = QDate.currentDate()
        self.start_date = None
        self.end_date = None
        self.hover_date = None
        self.setMouseTracking(True)
        self.setFixedSize(280, 240)

    def set_month(self, year, month):
        self.current_date = QDate(year, month, 1)
        self.update()

    def set_range(self, start, end, hover=None):
        self.start_date = start
        self.end_date = end
        self.hover_date = hover
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 绘制周标题
        p.setFont(QFont("Microsoft YaHei", 9))
        weeks = ["一", "二", "三", "四", "五", "六", "日"]
        cell_w = self.width() / 7
        cell_h = 32
        
        p.setPen(QColor("#999"))
        for i, w in enumerate(weeks):
            p.drawText(QRectF(i*cell_w, 0, cell_w, cell_h), Qt.AlignmentFlag.AlignCenter, w)

        # 绘制日期
        first_day = QDate(self.current_date.year(), self.current_date.month(), 1)
        # 计算日历起始日期 (如果是周一则向前偏)
        start_date = first_day.addDays(-(first_day.dayOfWeek() - 1))
        
        p.setFont(QFont("Microsoft YaHei", 9))
        for r in range(6):
            for c in range(7):
                d = start_date.addDays(r * 7 + c)
                rect = QRectF(c * cell_w, (r + 1) * cell_h, cell_w, cell_h)
                
                is_curr_month = (d.month() == self.current_date.month())
                
                # 计算各种状态
                is_start = (d == self.start_date)
                is_end = (d == self.end_date)
                
                # 范围高亮逻辑
                in_range = False
                if self.start_date:
                    if self.end_date:
                        in_range = self.start_date < d < self.end_date
                    elif self.hover_date:
                        s, e = sorted([self.start_date, self.hover_date])
                        in_range = s < d < e

                # 1. 绘制范围背景
                if in_range:
                    p.setBrush(QColor("#e6f4ff"))
                    p.setPen(Qt.PenStyle.NoPen)
                    p.drawRect(rect)
                elif is_start or is_end:
                    # 选中端点背景
                    p.setBrush(QColor("#1890ff"))
                    p.setPen(Qt.PenStyle.NoPen)
                    p.drawRoundedRect(rect.adjusted(4,4,-4,-4), 4, 4)

                # 2. 绘制文字
                if not is_curr_month:
                    p.setPen(QColor("#ccc"))
                elif is_start or is_end:
                    p.setPen(QColor("white"))
                else:
                    p.setPen(QColor("#333"))
                    
                p.drawText(rect, Qt.AlignmentFlag.AlignCenter, str(d.day()))

    def mousePressEvent(self, event):
        d = self._date_at(event.position())
        if d:
            self.dateClicked.emit(d)

    def mouseMoveEvent(self, event):
        d = self._date_at(event.position())
        if d != self.hover_date:
            self.hover_date = d
            self.hoveredDateChanged.emit(d)

    def _date_at(self, pos):
        cell_w = self.width() / 7
        cell_h = 32
        c = int(pos.x() // cell_w)
        r = int(pos.y() // cell_h) - 1
        if 0 <= r < 6 and 0 <= c < 7:
            first_day = QDate(self.current_date.year(), self.current_date.month(), 1)
            start_date = first_day.addDays(-(first_day.dayOfWeek() - 1))
            return start_date.addDays(r * 7 + c)
        return None

class AntdDateRangePopup(QDialog):
    """Ant Design 风格双月选择弹出层"""
    def __init__(self, start, end, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.start_date = start
        self.end_date = end
        self.hover_date = None
        
        # UI 状态: 显示的起始月份
        self.view_date = QDate(start.year(), start.month(), 1)
        
        self._setup_ui()
        self._update_all()

    def paintEvent(self, event):
        """绘制顶部小三角"""
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(QColor("white"))
        p.setPen(QColor("#f0f0f0"))
        
        # 三角形路径
        path = QPainterPath()
        path.moveTo(25, 10)
        path.lineTo(30, 2)
        path.lineTo(35, 10)
        path.closeSubpath()
        p.drawPath(path)
        # 补一下白线消除接缝
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRect(25, 9, 10, 2)

    def _setup_ui(self):
        self.container = QFrame(self)
        self.container.setStyleSheet("""
            QFrame {
                background: white; border-radius: 4px;
                border: 1px solid #f0f0f0;
            }
        """)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0,0,0,60))
        shadow.setOffset(0, 4)
        self.container.setGraphicsEffect(shadow)

        main_v = QVBoxLayout(self.container)
        main_v.setContentsMargins(15, 15, 15, 15)

        # 导航头部
        nav_lay = QHBoxLayout()
        self.btn_prev_y = self._nav_btn("<<")
        self.btn_prev_m = self._nav_btn("<")
        self.title_l = QLabel()
        self.title_r = QLabel()
        self.btn_next_m = self._nav_btn(">")
        self.btn_next_y = self._nav_btn(">>")
        
        nav_lay.addWidget(self.btn_prev_y)
        nav_lay.addWidget(self.btn_prev_m)
        nav_lay.addStretch()
        nav_lay.addWidget(self.title_l)
        nav_lay.addStretch()
        nav_lay.addWidget(self.title_r)
        nav_lay.addStretch()
        nav_lay.addWidget(self.btn_next_m)
        nav_lay.addWidget(self.btn_next_y)
        
        main_v.addLayout(nav_lay)

        # 日历平铺区
        calendars = QHBoxLayout()
        self.mv_left = MonthView()
        self.mv_right = MonthView()
        calendars.addWidget(self.mv_left)
        calendars.addWidget(self.mv_right)
        main_v.addLayout(calendars)

        # 信号
        self.btn_prev_y.clicked.connect(lambda: self._adj_view(y=-1))
        self.btn_prev_m.clicked.connect(lambda: self._adj_view(m=-1))
        self.btn_next_m.clicked.connect(lambda: self._adj_view(m=1))
        self.btn_next_y.clicked.connect(lambda: self._adj_view(y=1))
        
        self.mv_left.dateClicked.connect(self._on_click)
        self.mv_right.dateClicked.connect(self._on_click)
        self.mv_left.hoveredDateChanged.connect(self._update_hovers)
        self.mv_right.hoveredDateChanged.connect(self._update_hovers)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 10, 0, 10) # 顶部留出 10px 给小三角
        lay.addWidget(self.container)

    def _nav_btn(self, text):
        b = QPushButton(text)
        b.setFixedSize(24, 24)
        b.setStyleSheet("QPushButton { border:none; color:#999; font-weight:bold; } QPushButton:hover { color:#1890ff; }")
        return b

    def _adj_view(self, y=0, m=0):
        self.view_date = self.view_date.addYears(y).addMonths(m)
        self._update_all()

    def _update_all(self):
        # 更新标题
        self.title_l.setText(f"{self.view_date.year()}年 {self.view_date.month()}月")
        next_m = self.view_date.addMonths(1)
        self.title_r.setText(f"{next_m.year()}年 {next_m.month()}月")
        
        # 更新视图
        self.mv_left.set_month(self.view_date.year(), self.view_date.month())
        self.mv_right.set_month(next_m.year(), next_m.month())
        self._refresh_ranges()

    def _update_hovers(self, hover):
        self.hover_date = hover
        self._refresh_ranges()

    def _refresh_ranges(self):
        self.mv_left.set_range(self.start_date, self.end_date, self.hover_date)
        self.mv_right.set_range(self.start_date, self.end_date, self.hover_date)

    def _on_click(self, d):
        if not self.start_date or (self.start_date and self.end_date):
            # 开始新选择
            self.start_date = d
            self.end_date = None
        else:
            # 闭合选择
            if d < self.start_date:
                # 如果点选的日期早于已选起始日，则交换或重置
                self.start_date, self.end_date = d, self.start_date
            else:
                self.end_date = d
            self.accept()
        self.hover_date = None
        self._refresh_ranges()

    def get_range(self):
        return self.start_date, self.end_date

class AntdDateRangePicker(QFrame):
    """Ant Design 风格日期范围选择器控件"""
    valueChanged = pyqtSignal(QDate, QDate)

    def __init__(self, start=None, end=None, parent=None):
        super().__init__(parent)
        self.start_date = start or QDate.currentDate().addDays(-7)
        self.end_date = end or QDate.currentDate()
        self.setFixedSize(260, 32)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._setup_ui()

    def _setup_ui(self):
        self.setObjectName("Picker")
        self.setStyleSheet("""
            #Picker {
                background: white; border: 1px solid #d9d9d9; border-radius: 2px;
            }
            #Picker:hover { border-color: #40a9ff; }
            QLabel { color: #555; font-size: 13px; font-family: 'Segoe UI', 'Microsoft YaHei'; }
        """)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(10, 0, 10, 0)
        lay.setSpacing(12)
        
        self.lbl_start = QLabel(self.start_date.toString("yyyy-MM-dd"))
        
        arrow_lbl = QLabel("→")
        arrow_lbl.setStyleSheet("color: #bfbfbf;")
        
        self.lbl_end = QLabel(self.end_date.toString("yyyy-MM-dd"))
        
        icon = QLabel("📅")
        icon.setStyleSheet("color: #ccc; font-size: 14px;")
        
        lay.addWidget(self.lbl_start)
        lay.addWidget(arrow_lbl)
        lay.addWidget(self.lbl_end)
        lay.addStretch()
        lay.addWidget(icon)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.setStyleSheet(self.styleSheet() + " #Picker { border-color: #1890ff; outline: none; }")
            popup = AntdDateRangePopup(self.start_date, self.end_date, self.window())
            # 计算位置 (显示在控件下方)
            pos = self.mapToGlobal(self.rect().bottomLeft())
            popup.move(pos.x(), pos.y() + 5)
            
            if popup.exec():
                s, e = popup.get_range()
                if s and e:
                    self.start_date, self.end_date = s, e
                    self.lbl_start.setText(s.toString("yyyy-MM-dd"))
                    self.lbl_end.setText(e.toString("yyyy-MM-dd"))
                    self.valueChanged.emit(s, e)
            
            self.setStyleSheet(self.styleSheet().replace("border-color: #1890ff;", "border-color: #d9d9d9;"))
