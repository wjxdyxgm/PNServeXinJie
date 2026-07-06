from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QWidget

from src.view.components import ClickableLineEdit, SwitchButton
from src.view.settings.run_mode_selector import RunModeSelector
from src.view.settings.serial_port_selector import SerialPortSelector
from src.view.settings.styles import create_settings_card


class BasicSettingsPanel(QWidget):
    standbyTimeChanged = pyqtSignal(int)
    featureToggled = pyqtSignal(str, bool)
    runModeSelected = pyqtSignal(int)
    serialPortChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.switches: dict[str, SwitchButton] = {}
        self.run_mode_buttons = {}
        self._build_ui()

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        card = create_settings_card()
        layout.addWidget(card)

        grid = QGridLayout(card)
        grid.setContentsMargins(30, 30, 30, 30)
        grid.setHorizontalSpacing(40)
        grid.setVerticalSpacing(25)

        grid.addWidget(QLabel("无操作待机时间(秒)"), 0, 0)
        self.standby_input = ClickableLineEdit("60", keyboard_type="numeric")
        self.standby_input.setFixedWidth(120)
        self.standby_input.valueChanged.connect(self._on_standby_changed)
        grid.addWidget(self.standby_input, 0, 1)

        grid.addWidget(QLabel("串口号"), 0, 2)
        self.serial_port_combo = SerialPortSelector()
        self.serial_port_combo.currentTextChanged.connect(self.serialPortChanged)
        grid.addWidget(self.serial_port_combo, 0, 3)

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
        for label_text, key, row, col in switch_rows:
            grid.addWidget(QLabel(label_text), row, col)
            switch = SwitchButton()
            switch.toggled.connect(lambda value, k=key: self.featureToggled.emit(k, value))
            self.switches[key] = switch
            grid.addWidget(switch, row, col + 1)

        grid.addWidget(QLabel("运行模式"), 4, 0)
        self.run_mode_selector = RunModeSelector()
        self.run_mode_selector.modeSelected.connect(self.runModeSelected)
        self.run_mode_buttons = self.run_mode_selector.buttons
        grid.addWidget(self.run_mode_selector, 4, 1, 1, 3)

        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(3, 1)

    def set_config(self, config: dict):
        if self.standby_input.text() != str(config["standby_time"]):
            self.standby_input.blockSignals(True)
            self.standby_input.setText(str(config["standby_time"]))
            self.standby_input.blockSignals(False)

        self.set_serial_port_selection(config["serial_port"])

        for key, switch in self.switches.items():
            switch.set_active(config[key], animate=True)

        self.run_mode_selector.set_mode(int(config.get("run_mode", 1)))

    def refresh_serial_ports(self, preferred_port: str = ""):
        self.serial_port_combo.refresh_ports(preferred_port)

    def set_serial_port_selection(self, port: str):
        self.serial_port_combo.set_selection(port)

    def _on_standby_changed(self, value: str):
        self.standbyTimeChanged.emit(int(value or 0))
