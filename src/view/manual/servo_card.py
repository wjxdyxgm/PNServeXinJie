from __future__ import annotations

from PyQt6.QtWidgets import QFrame, QVBoxLayout

from src.view.manual.servo_card_styles import CARD_STYLE
from src.view.manual.servo_controls import ServoControls
from src.view.manual.servo_header import ServoHeader
from src.view.manual.servo_param_grid import ServoParamGrid


class ServoCard(QFrame):
    """伺服控制卡片，适配 PLC 绑定。"""

    def __init__(self, title="伺服", servo_id=1, store=None, parent=None):
        super().__init__(parent)
        self.servo_id = servo_id
        self.store = store
        self.setStyleSheet(CARD_STYLE)
        self._build_ui(title)
        self._connect_signals()

    def _build_ui(self, title):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)

        self.header = ServoHeader(title)
        self.params = ServoParamGrid()
        self.controls = ServoControls()

        layout.addWidget(self.header)
        layout.addWidget(self.params)
        layout.addWidget(self.controls)

        self.pos_input = self.params.pos_input
        self.mdi_input = self.params.mdi_input
        self.zero_offset_input = self.params.zero_offset_input
        self.enable_cb = self.controls.enable_cb
        self.home_btn = self.controls.home_btn
        self.fault_reset_btn = self.controls.fault_reset_btn
        self.run_btn = self.controls.run_btn

    def _connect_signals(self):
        if not self.store:
            return
        sid = self.servo_id

        self.pos_input.valueChanged.connect(
            lambda value, servo_id=sid: self.store.set_servo_value(
                servo_id, "target_pos", float(value or 0), write=True
            )
        )
        self.mdi_input.valueChanged.connect(
            lambda value, servo_id=sid: self.store.set_servo_value(
                servo_id, "mdi", int(value or 0), write=True
            )
        )
        self.zero_offset_input.valueChanged.connect(
            lambda value, servo_id=sid: self.store.set_servo_value(
                servo_id, "zero_offset", float(value or 0), write=True
            )
        )
        self.enable_cb.toggled.connect(
            lambda enabled, servo_id=sid: self.store.set_servo_value(
                servo_id, "enable", enabled, write=True
            )
        )

        self.home_btn.clicked.connect(lambda _checked=False, servo_id=sid: self._toggle_home(servo_id))
        self.fault_reset_btn.pressed.connect(lambda servo_id=sid: self.store.write_plc(f"servo.{servo_id}.reset_err", True))
        self.fault_reset_btn.released.connect(lambda servo_id=sid: self.store.write_plc(f"servo.{servo_id}.reset_err", False))
        self.run_btn.pressed.connect(lambda servo_id=sid: self.store.write_plc(f"servo.{servo_id}.execute", True))
        self.run_btn.released.connect(lambda servo_id=sid: self.store.write_plc(f"servo.{servo_id}.execute", False))

        self.store.dataChanged.connect(self._update_ui_from_store)

    def _toggle_home(self, servo_id: int):
        current = self.store.get_servo_value(servo_id, "fly_ref", False)
        self.store.set_servo_value(servo_id, "fly_ref", not current, write=True)

    def _update_ui_from_store(self):
        data = self.store.get_servo_snapshot(self.servo_id)
        current_pos = data.get("current_pos", 0)
        self.header.set_feedback(current_pos, data.get("error_id", 0), data.get("done", False))
        self.params.set_values(data)
        self.controls.set_enabled_checked(data.get("enable", False))
        self.controls.set_home_active(active=not data.get("fly_ref", False))
