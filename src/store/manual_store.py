"""
Manual page store.
"""
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot


class ManualStore(QObject):
    dataChanged = pyqtSignal()
    actionExecuted = pyqtSignal(str)
    writeRequested = pyqtSignal(str, object)
    MANUAL_MODE_PATH = "mode.手动模式"
    AUTO_GAS_MODE_PATH = "mode.自动气检"
    PAGE_MODE_WRITES = {
        "manual": (
            (MANUAL_MODE_PATH, True),
            (AUTO_GAS_MODE_PATH, False),
        ),
        "gas": (
            (MANUAL_MODE_PATH, False),
            (AUTO_GAS_MODE_PATH, True),
        ),
    }

    def __init__(self, parent=None):
        super().__init__(parent)

        self.signals = {
            "顶缸上限": False,
            "顶缸下限": False,
            "水箱上限": False,
            "水箱下限": False,
            "销钉1": False,
            "销钉2": False,
            "销钉3": False,
            "销钉4": False,
            "OK": False,
            "NG": False,
        }

        self.q_status = {
            "顶缸伸出": False,
            "顶缸缩回": False,
            "侧顶油伸出": False,
            "侧顶油缩回": False,
            "侧气顶出": False,
            "侧气缩回": False,
            "高压气检": False,
            "低压气检": False,
            "打点伸出": False,
            "打点缩回": False,
            "水箱上升": False,
            "水箱下降": False,
            "高压水检": False,
            "低压水检": False,
            "工作台推出": False,
            "工作台退回": False,
            "启动气密仪": False,
            "停止气密仪": False,
            "Error报警": False,
            "启动运行灯": False,
            "三色绿运行": False,
            "三色红故障": False,
            "三色黄等待": False,
            "原位指示": False,
        }

        self.mode_status = {
            "手动模式": False,
            "自动气检": False,
            "自动水检": False,
            "急停": False,
            "工作台推出": False,
            "工作台缩回": False,
        }

        self.button_actions = [
            "顶缸伸出",
            "顶缸缩回",
            "侧气顶出",
            "侧气缩回",
            "侧顶油伸出",
            "侧顶油缩回",
            "高压气检启停",
            "低压气检启停",
            "打点伸出",
            "打点缩回",
            "启动气密",
            "停止气密",
        ]

        self.servo_data = {
            1: {
                "enable": False,
                "execute": False,
                "done": False,
                "mode": 0,
                "target_pos": 0.0,
                "mdi": 0,
                "zero_offset": 0.0,
                "fly_ref": False,
                "current_pos": 0,
                "error_id": 0,
            },
            2: {
                "enable": False,
                "execute": False,
                "done": False,
                "mode": 0,
                "target_pos": 0.0,
                "mdi": 0,
                "zero_offset": 0.0,
                "fly_ref": False,
                "current_pos": 0,
                "error_id": 0,
            },
            3: {
                "enable": False,
                "execute": False,
                "done": False,
                "mode": 0,
                "target_pos": 0.0,
                "mdi": 0,
                "zero_offset": 0.0,
                "fly_ref": False,
                "current_pos": 0,
                "error_id": 0,
            },
            4: {
                "enable": False,
                "execute": False,
                "done": False,
                "mode": 0,
                "target_pos": 0.0,
                "mdi": 0,
                "zero_offset": 0.0,
                "fly_ref": False,
                "current_pos": 0,
                "error_id": 0,
            },
        }

        self.torque_data = {
            "torque_1": 0.0,
            "torque_2": 0.0,
            "torque_3": 0.0,
            "torque_4": 0.0,
        }

    def execute_action(self, action_name: str):
        self.actionExecuted.emit(action_name)

    def write_plc(self, store_path: str, value):
        self.writeRequested.emit(store_path, value)

    def set_page_mode(self, page_name: str) -> bool:
        writes = self.PAGE_MODE_WRITES.get(str(page_name or ""))
        if not writes:
            return False

        for store_path, value in writes:
            self.write_plc(store_path, value)
        return True

    def _set_mapping_value(self, mapping: dict, key: str, value) -> bool:
        if key not in mapping or mapping[key] == value:
            return False
        mapping[key] = value
        return True

    def update_servo_param(self, servo_id: int, **kwargs):
        if servo_id not in self.servo_data:
            return

        changed = False
        for key, value in kwargs.items():
            if key in self.servo_data[servo_id] and self.servo_data[servo_id][key] != value:
                self.servo_data[servo_id][key] = value
                changed = True

        if changed:
            self.dataChanged.emit()

    def set_servo_value(self, servo_id: int, field_name: str, value, write: bool = False):
        if servo_id not in self.servo_data or field_name not in self.servo_data[servo_id]:
            return

        changed = self.servo_data[servo_id][field_name] != value
        if changed:
            self.servo_data[servo_id][field_name] = value
            self.dataChanged.emit()

        if write:
            self.write_plc(f"servo.{servo_id}.{field_name}", value)

    def get_servo_value(self, servo_id: int, field_name: str, default=None):
        if servo_id not in self.servo_data:
            return default
        return self.servo_data[servo_id].get(field_name, default)

    def get_servo_snapshot(self, servo_id: int) -> dict:
        if servo_id not in self.servo_data:
            return {}
        return dict(self.servo_data[servo_id])

    def reset_fault(self, servo_id: int):
        if servo_id in self.servo_data:
            self.writeRequested.emit(f"servo.{servo_id}.reset_err", True)

    @pyqtSlot(str, object)
    def apply_plc_value(self, store_path: str, value):
        parts = store_path.split(".")
        category = parts[0]
        changed = False

        if category == "signals" and len(parts) >= 2:
            changed = self._set_mapping_value(self.signals, parts[1], value)
        elif category == "q_status" and len(parts) >= 2:
            changed = self._set_mapping_value(self.q_status, parts[1], value)
        elif category == "mode" and len(parts) >= 2:
            changed = self._set_mapping_value(self.mode_status, parts[1], value)
        elif category == "servo" and len(parts) >= 3:
            try:
                servo_id = int(parts[1])
            except ValueError:
                return
            if servo_id in self.servo_data:
                changed = self._set_mapping_value(self.servo_data[servo_id], parts[2], value)
        elif category == "torque" and len(parts) >= 2:
            changed = self._set_mapping_value(self.torque_data, parts[1], value)

        if changed:
            self.dataChanged.emit()

    def to_dict(self) -> dict:
        return {
            "signals": self.signals,
            "q_status": self.q_status,
            "mode_status": self.mode_status,
            "servo_data": self.servo_data,
            "torque_data": self.torque_data,
        }
