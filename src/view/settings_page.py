from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from src.store.settings_store import LIMIT_SETTING_KEYS, RUN_MODE_OPTIONS, SettingsStore
from src.view.components import ClickableLineEdit, SwitchButton


# 扭力 / 伺服距离 OK 上下限 UI 配置: (中文标签, config key)
_TORQUE_LIMIT_FIELDS = [
    ("扭力OK下限1", "torque_ok_low_1"),
    ("扭力OK上限1", "torque_ok_high_1"),
    ("扭力OK下限2", "torque_ok_low_2"),
    ("扭力OK上限2", "torque_ok_high_2"),
    ("扭力OK下限3", "torque_ok_low_3"),
    ("扭力OK上限3", "torque_ok_high_3"),
    ("扭力OK下限4", "torque_ok_low_4"),
    ("扭力OK上限4", "torque_ok_high_4"),
]

_SERVO_DIST_LIMIT_FIELDS = [
    ("伺服距离OK下限1", "servo_dist_ok_low_1"),
    ("伺服距离OK上限1", "servo_dist_ok_high_1"),
    ("伺服距离OK下限2", "servo_dist_ok_low_2"),
    ("伺服距离OK上限2", "servo_dist_ok_high_2"),
    ("伺服距离OK下限3", "servo_dist_ok_low_3"),
    ("伺服距离OK上限3", "servo_dist_ok_high_3"),
    ("伺服距离OK下限4", "servo_dist_ok_low_4"),
    ("伺服距离OK上限4", "servo_dist_ok_high_4"),
]

_LIMIT_FIELD_LABELS = {key: label for label, key in _TORQUE_LIMIT_FIELDS + _SERVO_DIST_LIMIT_FIELDS}


def _list_serial_ports_from_pyserial() -> list[str]:
    try:
        from serial.tools import list_ports
    except ImportError:
        return []

    try:
        return [
            str(port.device).strip()
            for port in list_ports.comports()
            if getattr(port, "device", "")
        ]
    except Exception:
        return []


def _list_serial_ports_from_registry() -> list[str]:
    try:
        import winreg
    except ImportError:
        return []

    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DEVICEMAP\SERIALCOMM") as key:
            ports = []
            index = 0
            while True:
                try:
                    _, value, _ = winreg.EnumValue(key, index)
                except OSError:
                    break

                if value:
                    ports.append(str(value).strip())
                index += 1
    except OSError:
        return []

    return ports


class SettingsPage(QFrame):
    """系统设置页面"""

    SERIAL_PORT_REFRESH_MS = 2000

    def __init__(self, store: SettingsStore = None, parent=None):
        super().__init__(parent)
        self.store = store
        self.setStyleSheet("background: #f0f2f5;")
        self._build_ui()
        self._connect_signals()
        self._refresh_serial_ports()
        self._update_ui_from_store()

        self._serial_port_timer = QTimer(self)
        self._serial_port_timer.timeout.connect(self._refresh_serial_ports)
        self._serial_port_timer.start(self.SERIAL_PORT_REFRESH_MS)

    # ------------------------------------------------------------------
    #  UI 构建
    # ------------------------------------------------------------------

    def _build_ui(self):
        root_lay = QVBoxLayout(self)
        root_lay.setContentsMargins(0, 0, 0, 0)
        root_lay.setSpacing(0)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        content = QWidget()
        scroll_area.setWidget(content)
        root_lay.addWidget(scroll_area)

        main_lay = QVBoxLayout(content)
        main_lay.setContentsMargins(40, 40, 40, 40)
        main_lay.setSpacing(30)

        header_lay = QHBoxLayout()
        title = QLabel("系统参数设置")
        title.setStyleSheet(
            """
            font-size: 24px; font-weight: bold;
            font-family: 'YouSheBiaoTiHei';
            color: #1890ff;
            """
        )
        header_lay.addWidget(title)
        header_lay.addStretch()
        main_lay.addLayout(header_lay)

        basic_card = self._create_card()
        basic_grid = QGridLayout(basic_card)
        basic_grid.setContentsMargins(30, 30, 30, 30)
        basic_grid.setHorizontalSpacing(40)
        basic_grid.setVerticalSpacing(25)

        basic_grid.addWidget(QLabel("无操作待机时间(秒)"), 0, 0)
        self.standby_input = ClickableLineEdit("60", keyboard_type="numeric")
        self.standby_input.setFixedWidth(120)
        basic_grid.addWidget(self.standby_input, 0, 1)

        basic_grid.addWidget(QLabel("串口号"), 0, 2)
        self.serial_port_combo = QComboBox()
        self.serial_port_combo.setFixedWidth(160)
        self.serial_port_combo.setEditable(False)
        self.serial_port_combo.setStyleSheet(
            """
            QComboBox {
                border: 1px solid #d9d9d9;
                border-radius: 4px;
                padding: 4px 8px;
                background: white;
                font-size: 14px;
                color: #1890ff;
                font-weight: bold;
            }
            QComboBox:hover {
                border-color: #40a9ff;
            }
            QComboBox::drop-down {
                border: none;
                width: 24px;
            }
            """
        )
        basic_grid.addWidget(self.serial_port_combo, 0, 3)

        switch_rows = [
            ("扫码功能", "scan_code", 1, 0),
            ("侧油功能", "side_oil", 1, 2),
            ("侧气功能", "side_air", 2, 0),
            ("水箱功能", "water_tank", 2, 2),
            ("销钉1", "pin_1", 3, 0),
            ("销钉2", "pin_2", 3, 2),
            ("销钉3", "pin_3", 3, 4),
            ("销钉4", "pin_4", 3, 6),
        ]

        self.switches: dict[str, SwitchButton] = {}
        for label_text, key, row, col in switch_rows:
            basic_grid.addWidget(QLabel(label_text), row, col)
            switch = SwitchButton()
            self.switches[key] = switch
            basic_grid.addWidget(switch, row, col + 1)

        basic_grid.addWidget(QLabel("运行模式"), 4, 0)
        self.run_mode_group = QButtonGroup(self)
        self.run_mode_group.setExclusive(True)
        self.run_mode_buttons: dict[int, QPushButton] = {}

        run_mode_widget = QWidget()
        run_mode_widget.setStyleSheet("background: transparent;")
        run_mode_lay = QHBoxLayout(run_mode_widget)
        run_mode_lay.setContentsMargins(0, 0, 0, 0)
        run_mode_lay.setSpacing(0)

        modes = sorted(RUN_MODE_OPTIONS.items())
        count = len(modes)

        for i, (mode, label) in enumerate(modes):
            button = QPushButton(label)
            button.setCheckable(True)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setFixedSize(92, 34)

            if count == 1:
                radius = "border-radius: 4px;"
            elif i == 0:
                radius = "border-top-left-radius: 4px; border-bottom-left-radius: 4px; border-top-right-radius: 0px; border-bottom-right-radius: 0px;"
            elif i == count - 1:
                radius = "border-top-left-radius: 0px; border-bottom-left-radius: 0px; border-top-right-radius: 4px; border-bottom-right-radius: 4px;"
            else:
                radius = "border-radius: 0px;"

            margin = "margin-left: -1px;" if i > 0 else ""

            button.setStyleSheet(
                f"""
                QPushButton {{
                    background: #ffffff;
                    border: 1px solid #d9d9d9;
                    {radius}
                    {margin}
                    color: #555;
                    font-size: 14px;
                }}
                QPushButton:hover {{
                    color: #1890ff;
                }}
                QPushButton:checked {{
                    background: #1890ff;
                    border-color: #1890ff;
                    color: white;
                }}
                """
            )
            
            button.toggled.connect(lambda checked, btn=button: btn.raise_() if checked else None)

            self.run_mode_group.addButton(button, mode)
            self.run_mode_buttons[mode] = button
            run_mode_lay.addWidget(button)

        run_mode_lay.addStretch()
        basic_grid.addWidget(run_mode_widget, 4, 1, 1, 3)

        basic_grid.setColumnStretch(1, 1)
        basic_grid.setColumnStretch(3, 1)
        main_lay.addWidget(basic_card)

        limits_card = self._create_card()
        limits_grid = QGridLayout(limits_card)
        limits_grid.setContentsMargins(30, 30, 30, 30)
        limits_grid.setHorizontalSpacing(40)
        limits_grid.setVerticalSpacing(25)

        self.limit_inputs: dict[str, ClickableLineEdit] = {}
        max_rows = max(len(_TORQUE_LIMIT_FIELDS), len(_SERVO_DIST_LIMIT_FIELDS))
        for row in range(max_rows):
            # 左列: 扭力OK
            if row < len(_TORQUE_LIMIT_FIELDS):
                left_label, left_key = _TORQUE_LIMIT_FIELDS[row]
                limits_grid.addWidget(QLabel(left_label), row, 0)
                left_input = ClickableLineEdit("0", keyboard_type="numeric")
                left_input.setFixedWidth(120)
                self.limit_inputs[left_key] = left_input
                limits_grid.addWidget(left_input, row, 1)
            # 右列: 伺服距离OK
            if row < len(_SERVO_DIST_LIMIT_FIELDS):
                right_label, right_key = _SERVO_DIST_LIMIT_FIELDS[row]
                limits_grid.addWidget(QLabel(right_label), row, 2)
                right_input = ClickableLineEdit("0", keyboard_type="numeric")
                right_input.setFixedWidth(120)
                self.limit_inputs[right_key] = right_input
                limits_grid.addWidget(right_input, row, 3)

        limits_grid.setColumnStretch(1, 1)
        limits_grid.setColumnStretch(3, 1)
        main_lay.addWidget(limits_card)

        main_lay.addStretch()
        self._validate_limit_inputs()

    # ------------------------------------------------------------------
    #  信号连接
    # ------------------------------------------------------------------

    def _connect_signals(self):
        if not self.store:
            return

        self.standby_input.valueChanged.connect(
            lambda v: self.store.set_standby_time(int(v or 0), write=True)
        )

        for key, switch in self.switches.items():
            switch.toggled.connect(lambda v, k=key: self.store.set_feature_enabled(k, v))

        for mode, button in self.run_mode_buttons.items():
            button.clicked.connect(
                lambda _checked=False, m=mode: self.store.set_run_mode(m, write=True)
            )

        self.serial_port_combo.currentTextChanged.connect(self.store.set_serial_port)

        for key, inp in self.limit_inputs.items():
            inp.valueChanged.connect(
                lambda v, k=key: self._on_limit_value_changed(k, v)
            )

        self.store.dataChanged.connect(self._update_ui_from_store)

    # ------------------------------------------------------------------
    #  UI 刷新
    # ------------------------------------------------------------------

    def _update_ui_from_store(self):
        if not self.store:
            return

        config = self.store.config

        if self.standby_input.text() != str(config["standby_time"]):
            self.standby_input.blockSignals(True)
            self.standby_input.setText(str(config["standby_time"]))
            self.standby_input.blockSignals(False)

        self._set_serial_port_selection(config["serial_port"])

        for key, switch in self.switches.items():
            switch.set_active(config[key], animate=True)

        mode = int(config.get("run_mode", 1))
        button = self.run_mode_buttons.get(mode)
        if button and not button.isChecked():
            button.setChecked(True)

        for key, inp in self.limit_inputs.items():
            display_str = (
                f"{config[key]:.2f}"
                if isinstance(config[key], float)
                else str(config[key])
            )
            if inp.text() != display_str:
                inp.blockSignals(True)
                inp.setText(display_str)
                inp.blockSignals(False)

    def _refresh_serial_ports(self):
        current_port = self.serial_port_combo.currentText()
        preferred_port = current_port
        if self.store:
            preferred_port = self.store.config.get("serial_port", "")

        ports = self._enumerate_serial_ports()
        if preferred_port and preferred_port not in ports:
            ports.append(preferred_port)
        ports = sorted(set(ports))

        combo_items = [self.serial_port_combo.itemText(index) for index in range(self.serial_port_combo.count())]
        if combo_items == ports:
            self._set_serial_port_selection(preferred_port or current_port)
            return

        self.serial_port_combo.blockSignals(True)
        self.serial_port_combo.clear()
        self.serial_port_combo.addItems(ports)
        self.serial_port_combo.blockSignals(False)
        self._set_serial_port_selection(preferred_port or current_port)

    @staticmethod
    def _enumerate_serial_ports() -> list[str]:
        ports = set(_list_serial_ports_from_pyserial())
        ports.update(_list_serial_ports_from_registry())
        return sorted(port for port in ports if port)

    def _set_serial_port_selection(self, port: str):
        port = str(port or "")
        if port and self.serial_port_combo.findText(port) < 0:
            self.serial_port_combo.blockSignals(True)
            self.serial_port_combo.addItem(port)
            self.serial_port_combo.model().sort(0)
            self.serial_port_combo.blockSignals(False)

        self.serial_port_combo.blockSignals(True)
        if not port:
            self.serial_port_combo.setCurrentIndex(-1)
        else:
            index = self.serial_port_combo.findText(port)
            self.serial_port_combo.setCurrentIndex(index)
        self.serial_port_combo.blockSignals(False)

    # ------------------------------------------------------------------
    #  内部工具
    # ------------------------------------------------------------------

    def _on_limit_value_changed(self, key: str, raw_value: str):
        value = float(raw_value or 0)
        print(f"[SettingsPage] 用户修改: {key}={value}")
        if self.store.set_limit_value(key, value, write=True):
            return

        self._update_ui_from_store()
        pair = self.store.get_limit_pair(key)
        if pair is None:
            return

        low_key, high_key = pair
        QMessageBox.warning(
            self,
            "参数范围无效",
            f"{_LIMIT_FIELD_LABELS[low_key]} 不能大于 {_LIMIT_FIELD_LABELS[high_key]}。",
        )

    def _validate_limit_inputs(self):
        actual_keys = set(self.limit_inputs)
        expected_keys = set(LIMIT_SETTING_KEYS)
        if actual_keys == expected_keys:
            return

        missing = sorted(expected_keys - actual_keys)
        extra = sorted(actual_keys - expected_keys)
        raise ValueError(
            f"limit input definitions out of sync: missing={missing}, extra={extra}"
        )

    @staticmethod
    def _create_card() -> QFrame:
        """创建统一风格的白色圆角卡片。"""
        card = QFrame()
        card.setStyleSheet(
            """
            QFrame {
                background: white;
                border-radius: 12px;
            }
            QLabel {
                font-size: 16px;
                color: #555;
                font-weight: bold;
            }
            """
        )
        return card
