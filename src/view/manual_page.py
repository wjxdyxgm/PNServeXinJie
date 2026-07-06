from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
    QPushButton, QGridLayout, QLineEdit, QCheckBox, QScrollArea
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QPainter, QLinearGradient, QBrush

from src.view.components import NumericKeypad, ClickableLineEdit, StatusLamp

# === 按钮名称 → PLC 绑定路径映射 ===
# 按钮在 UI 上的显示名称 → binding_config 中 btn.{key} 路径
BUTTON_BINDING_MAP = {
    "顶缸伸出": "btn.顶缸伸出",
    "顶缸缩回": "btn.顶缸缩回",
    "侧气顶出": "btn.侧气顶出",
    "侧气缩回": "btn.侧气缩回",
    "侧顶油伸出": "btn.侧顶油伸出",
    "侧顶油缩回": "btn.侧顶油缩回",
    "高压气检启停": "btn.高压气检启停",
    "低压气检启停": "btn.低压气检启停",
    "打点伸出": "btn.打点伸出",
    "打点缩回": "btn.打点缩回",
    "启动气密": "btn.启动气密",
    "停止气密": "btn.停止气密",
}


class ServoCard(QFrame):
    """伺服控制卡片 — 适配 PLC 绑定"""
    def __init__(self, title="伺服", servo_id=1, store=None, parent=None):
        super().__init__(parent)
        self.servo_id = servo_id
        self.store = store
        self.setStyleSheet("""
            ServoCard {
                background: white;
                border-radius: 8px;
                border: 1px solid #e8e8e8;
            }
        """)
        self._build_ui(title)
        self._connect_signals()

    def _build_ui(self, title):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(15, 15, 15, 15)
        lay.setSpacing(12)

        # 标题、错误码和状态灯
        header = QHBoxLayout()
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("font-size: 18px; font-weight: bold; font-family: 'YouSheBiaoTiHei'; color: #333;")
        header.addWidget(title_lbl)

        # 错误码 (移至顶部)
        err_label = QLabel("错误码:")
        err_label.setStyleSheet("color: #999; font-size: 13px; margin-left: 12px;")
        header.addWidget(err_label)
        self.error_code = QLabel("0")
        self.error_code.setStyleSheet("font-family: 'Consolas'; color: #666; font-size: 13px;")
        header.addWidget(self.error_code)

        abs_label = QLabel("编码器绝对值:")
        abs_label.setStyleSheet("color: #999; font-size: 13px; margin-left: 12px;")
        header.addWidget(abs_label)
        self.abs_pos_value = QLabel("0")
        self.abs_pos_value.setStyleSheet("font-family: 'Consolas'; color: #1890ff; font-size: 13px;")
        header.addWidget(self.abs_pos_value)

        header.addStretch()
        
        self.state_lamp = StatusLamp(size=14)
        header.addWidget(QLabel("运动状态"))
        header.addWidget(self.state_lamp)
        lay.addLayout(header)

        # 参数输入行
        grid = QGridLayout()
        grid.setSpacing(10)
        
        # 目标位置
        grid.addWidget(QLabel("伸出高度:"), 0, 0)
        self.pos_input = ClickableLineEdit("0")
        self.pos_input.setFixedWidth(80)
        grid.addWidget(self.pos_input, 0, 1)
        pos_unit = QLabel("mm")
        pos_unit.setStyleSheet("color: #999; font-size: 12px;")
        grid.addWidget(pos_unit, 0, 2)

        # MDI 值
        grid.addWidget(QLabel("速度:"), 1, 0)
        self.mdi_input = ClickableLineEdit("0")
        self.mdi_input.setFixedWidth(80)
        grid.addWidget(self.mdi_input, 1, 1)

        # 反馈显示
        grid.addWidget(QLabel("位置反馈:"), 0, 3)
        self.pos_fb = QLabel("0.000")
        self.pos_fb.setStyleSheet("font-weight: bold; color: #1890ff; font-size: 14px;")
        grid.addWidget(self.pos_fb, 0, 4)
        pos_fb_unit = QLabel("mm")
        pos_fb_unit.setStyleSheet("color: #999; font-size: 12px;")
        grid.addWidget(pos_fb_unit, 0, 5)

        grid.addWidget(QLabel("零位补偿:"), 1, 3)
        self.zero_offset_input = ClickableLineEdit("0")
        self.zero_offset_input.setFixedWidth(80)
        grid.addWidget(self.zero_offset_input, 1, 4)
        offset_unit = QLabel("mm")
        offset_unit.setStyleSheet("color: #999; font-size: 12px;")
        grid.addWidget(offset_unit, 1, 5)

        lay.addLayout(grid)

        # 控制按钮行
        ctrl_lay = QHBoxLayout()
        self.enable_cb = QCheckBox("使能")
        ctrl_lay.addWidget(self.enable_cb)
        
        self.home_btn = QPushButton("回零")
        self.home_btn.setFixedSize(70, 32)
        self._set_home_btn_style(active=True)  # 默认蓝色 (PLC=0)
        ctrl_lay.addWidget(self.home_btn)

        self.fault_reset_btn = QPushButton("故障复位")
        self.fault_reset_btn.setFixedSize(90, 32)
        self.fault_reset_btn.setStyleSheet("""
            QPushButton {
                background: #FA8C16; color: white; border-radius: 4px;
                font-weight: bold; border: none;
            }
            QPushButton:hover { background: #FFA940; }
            QPushButton:pressed { background: #D46B08; }
        """)
        ctrl_lay.addWidget(self.fault_reset_btn)

        self.run_btn = QPushButton("启动运行")
        self.run_btn.setFixedHeight(32)
        self.run_btn.setStyleSheet("""
            QPushButton {
                background: #597EF7; color: white; border-radius: 4px; font-weight: bold;
            }
            QPushButton:pressed { background: #40a9ff; }
        """)
        ctrl_lay.addWidget(self.run_btn, 1)
        
        lay.addLayout(ctrl_lay)

    def _connect_signals(self):
        """绑定 UI 到 Store (PLC 写通过 writeRequested 信号)"""
        if not self.store: return
        sid = self.servo_id

        # UI → Store → PLC: 目标位置 (real)
        def _on_pos_changed(v, s=sid):
            val = float(v or 0)
            self.store.set_servo_value(s, "target_pos", val, write=True)
        self.pos_input.valueChanged.connect(_on_pos_changed)
        # UI → Store → PLC: MDI (int32)
        def _on_mdi_changed(v, s=sid):
            val = int(v or 0)
            self.store.set_servo_value(s, "mdi", val, write=True)
        self.mdi_input.valueChanged.connect(_on_mdi_changed)
        # UI → Store → PLC: 零位补偿
        def _on_zero_offset_changed(v, s=sid):
            val = float(v or 0)
            self.store.set_servo_value(s, "zero_offset", val, write=True)
        self.zero_offset_input.valueChanged.connect(_on_zero_offset_changed)
        # UI → Store → PLC: 使能 (电平保持, 需同时更新本地 Store + 写 PLC)
        def _on_enable_toggled(v, s=sid):
            self.store.set_servo_value(s, "enable", v, write=True)
        self.enable_cb.toggled.connect(_on_enable_toggled)
        
        # 回零按钮: FlyRef 电平保持 (toggle 切换)
        def _on_home_clicked(checked=False, s=sid):
            current = self.store.get_servo_value(s, "fly_ref", False)
            new_val = not current
            self.store.set_servo_value(s, "fly_ref", new_val, write=True)
        self.home_btn.clicked.connect(_on_home_clicked)
        # 故障复位: reset_err 脉冲 (press=True, release=False)
        self.fault_reset_btn.pressed.connect(
            lambda: self.store.write_plc(f"servo.{sid}.reset_err", True)
        )
        self.fault_reset_btn.released.connect(
            lambda: self.store.write_plc(f"servo.{sid}.reset_err", False)
        )
        # 启动运行: Execute 脉冲 (press=True, release=False)
        self.run_btn.pressed.connect(
            lambda: self.store.write_plc(f"servo.{sid}.execute", True)
        )
        self.run_btn.released.connect(
            lambda: self.store.write_plc(f"servo.{sid}.execute", False)
        )

        # Store → UI
        self.store.dataChanged.connect(self._update_ui_from_store)

    def _update_ui_from_store(self):
        data = self.store.get_servo_snapshot(self.servo_id)
        current_pos = data.get("current_pos", 0)
        self.abs_pos_value.setText(str(current_pos))
        self.pos_fb.setText(f"{float(current_pos) / 1000:.3f}")
        self.error_code.setText(str(data.get("error_id", 0)))
        # 定位值输入框 (阻塞信号防止循环触发)
        self.pos_input.blockSignals(True)
        self.pos_input.setText(str(data.get("target_pos", 0)))
        self.pos_input.blockSignals(False)
        # MDI 输入框 (阻塞信号防止循环触发)
        self.mdi_input.blockSignals(True)
        self.mdi_input.setText(str(data.get("mdi", 0)))
        self.mdi_input.blockSignals(False)
        # 零位补偿输入框 (阻塞信号防止循环触发)
        self.zero_offset_input.blockSignals(True)
        self.zero_offset_input.setText(str(data.get("zero_offset", 0.0)))
        self.zero_offset_input.blockSignals(False)
        # 使能复选框 (阻塞信号防止循环触发)
        self.enable_cb.blockSignals(True)
        self.enable_cb.setChecked(data.get("enable", False))
        self.enable_cb.blockSignals(False)
        # Done 状态灯: 错误时红, done 时绿, 否则灰
        if data.get("error_id", 0) != 0:
            self.state_lamp.set_error(True)
        else:
            self.state_lamp.set_active(data.get("done", False))
        # 回零按钮状态: PLC=0(蓝色), PLC=1(灰色)
        self._set_home_btn_style(active=not data.get("fly_ref", False))

    def _set_home_btn_style(self, active: bool):
        """设置回零按钮颜色: active=True 蓝色, active=False 灰色"""
        if active:
            self.home_btn.setStyleSheet("""
                QPushButton {
                    background: #0958d9; color: white; border-radius: 4px;
                    font-weight: bold; border: none;
                }
                QPushButton:pressed { background: #003eb3; }
            """)
        else:
            self.home_btn.setStyleSheet("""
                QPushButton {
                    background: #f5f5f5; color: #333; border-radius: 4px;
                    border: 1px solid #d9d9d9;
                }
                QPushButton:pressed { background: #e0e0e0; }
            """)


class ManualPage(QFrame):
    """手动模式页面 — 包含按钮矩阵和伺服控制"""

    def __init__(self, store=None, parent=None):
        super().__init__(parent)
        self.store = store
        self.signal_lamps = {} # 保存信号灯引用: {name: StatusLamp}
        self.setStyleSheet("background: #f0f2f5;")
        self._build_ui()
        self._connect_signals()

    def _build_ui(self):
        main_lay = QVBoxLayout(self)
        main_lay.setContentsMargins(15, 15, 15, 15)
        main_lay.setSpacing(15)

        # 1. 顶部信号指示 (对应图片第一行)
        header_lay = self._build_signal_header()
        main_lay.addLayout(header_lay)

        # 2. 中间按钮矩阵 (4列排布)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        scroll_lay = QVBoxLayout(scroll_content)
        scroll_lay.setContentsMargins(0, 0, 0, 0)
        scroll_lay.setSpacing(20)

        # 按钮网格
        grid_panel = self._build_button_grid()
        scroll_lay.addWidget(grid_panel)

        # 3. 底部伺服控制卡片 (水平滚动，支持触屏滑动)
        servo_scroll = QScrollArea()
        servo_scroll.setWidgetResizable(False)
        servo_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        servo_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        servo_scroll.setStyleSheet("""
            QScrollArea { background: transparent; border: none; }
            QScrollBar:horizontal {
                height: 8px; background: #e8e8e8; border-radius: 4px;
            }
            QScrollBar::handle:horizontal {
                background: #bbb; border-radius: 4px; min-width: 40px;
            }
            QScrollBar::handle:horizontal:hover { background: #999; }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
        """)
        servo_scroll.setFixedHeight(220)

        servo_container = QWidget()
        servo_container.setStyleSheet("background: transparent;")
        servo_lay = QHBoxLayout(servo_container)
        servo_lay.setContentsMargins(0, 0, 0, 0)
        servo_lay.setSpacing(12)
        for sid, title in [(1, "伺服 1"), (2, "伺服 2"), (3, "伺服 3"), (4, "伺服 4")]:
            card = ServoCard(title, sid, self.store)
            card.setFixedWidth(460)
            servo_lay.addWidget(card)

        servo_container.setFixedWidth(
            460 * 4 + 12 * 3 + 4  # 卡片宽度 × 4 + 间距 × 3 + 余量
        )
        servo_scroll.setWidget(servo_container)
        scroll_lay.addWidget(servo_scroll)
        
        scroll_lay.addStretch()
        scroll.setWidget(scroll_content)
        main_lay.addWidget(scroll, 1)

    def _build_signal_header(self):
        lay = QHBoxLayout()
        lay.setSpacing(10)

        title = QLabel("信号指示")
        title.setStyleSheet("font-weight: bold; font-size: 16px; margin-right: 10px;")
        lay.addWidget(title)

        signals = ["顶缸上限", "顶缸下限", "OK", "NG"]
        signals = list(self.store.signals) if self.store else ["椤剁几涓婇檺", "椤剁几涓嬮檺", "销钉1", "销钉2", "OK", "NG"]
        for s in signals:
            item = QFrame()
            item.setStyleSheet("background: white; border-radius: 2px; padding: 2px 8px;")
            h = QHBoxLayout(item)
            h.setContentsMargins(4, 2, 4, 2)
            
            lamp = StatusLamp(size=12)
            self.signal_lamps[s] = lamp # 保存引用
            
            lbl = QLabel(s)
            lbl.setStyleSheet("font-size: 13px; color: #333;")
            
            h.addWidget(lamp)
            h.addWidget(lbl)
            lay.addWidget(item)

        lay.addStretch()

        return lay

    def _build_button_grid(self):
        panel = QWidget()
        grid = QGridLayout(panel)
        grid.setSpacing(15)
        grid.setContentsMargins(0, 0, 0, 0)

        btns = self.store.button_actions if self.store else list(BUTTON_BINDING_MAP.keys())

        style = """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FFFFFF, stop:1 #E0E0E0);
                border: 1px solid #C0C0C0;
                border-radius: 8px;
                font-size: 18px;
                font-weight: bold;
                font-family: 'Microsoft YaHei';
                color: #333;
                min-height: 50px;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #E0E0E0, stop:1 #D0D0D0);
            }
        """

        for i, text in enumerate(btns):
            btn = QPushButton(text)
            btn.setStyleSheet(style)
            # 绑定: 瞬时脉冲 (pressed=True, released=False)
            if self.store:
                binding_path = BUTTON_BINDING_MAP.get(text, "")
                if binding_path:
                    btn.pressed.connect(
                        lambda p=binding_path: self.store.write_plc(p, True)
                    )
                    btn.released.connect(
                        lambda p=binding_path: self.store.write_plc(p, False)
                    )
                else:
                    # 暂无 PLC 绑定的按钮, 仅触发旧逻辑
                    btn.clicked.connect(lambda ch, t=text: self.store.execute_action(t))
            grid.addWidget(btn, i // 4, i % 4)

        return panel

    def _connect_signals(self):
        if not self.store: return
        self.store.dataChanged.connect(self._update_all_ui)
        self._update_all_ui()

    def _update_all_ui(self):
        """同步所有 Store 状态到 UI"""
        if not self.store: return
        
        # 1. 更新信号灯
        for name, state in self.store.signals.items():
            if name in self.signal_lamps:
                lamp = self.signal_lamps[name]
                if name == "NG":
                    lamp.set_error(state)
                else:
                    lamp.set_active(state)
