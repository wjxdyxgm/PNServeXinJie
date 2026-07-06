"""
Application settings store.
"""
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot


# 扭力 / 伺服距离 OK 上下限参数的 config key 列表
LIMIT_SETTING_KEYS = [
    "torque_ok_low_1",
    "torque_ok_high_1",
    "torque_ok_low_2",
    "torque_ok_high_2",
    "torque_ok_low_3",
    "torque_ok_high_3",
    "torque_ok_low_4",
    "torque_ok_high_4",
    "servo_dist_ok_low_1",
    "servo_dist_ok_high_1",
    "servo_dist_ok_low_2",
    "servo_dist_ok_high_2",
    "servo_dist_ok_low_3",
    "servo_dist_ok_high_3",
    "servo_dist_ok_low_4",
    "servo_dist_ok_high_4",
]

LIMIT_SETTING_PAIRS = [
    ("torque_ok_low_1", "torque_ok_high_1"),
    ("torque_ok_low_2", "torque_ok_high_2"),
    ("torque_ok_low_3", "torque_ok_high_3"),
    ("torque_ok_low_4", "torque_ok_high_4"),
    ("servo_dist_ok_low_1", "servo_dist_ok_high_1"),
    ("servo_dist_ok_low_2", "servo_dist_ok_high_2"),
    ("servo_dist_ok_low_3", "servo_dist_ok_high_3"),
    ("servo_dist_ok_low_4", "servo_dist_ok_high_4"),
]

RUN_MODE_OPTIONS = {
    1: "全功能",
    2: "压装",
    3: "气检",
}

_LIMIT_PAIR_BY_KEY = {}
for low_key, high_key in LIMIT_SETTING_PAIRS:
    _LIMIT_PAIR_BY_KEY[low_key] = (low_key, high_key)
    _LIMIT_PAIR_BY_KEY[high_key] = (low_key, high_key)


class SettingsStore(QObject):
    dataChanged = pyqtSignal()
    writeRequested = pyqtSignal(str, object)
    serialPortChanged = pyqtSignal(str)

    # ---------- PLC 路径映射 ----------
    SETTING_WRITE_PATHS = {
        "standby_time": "settings.standby_time",
        "run_mode": "settings.run_mode",
        "scan_code": "enable.扫码枪",
        "side_oil": "enable.侧油",
        "side_air": "enable.侧气",
        "water_tank": "enable.水箱",
        "pin_1": "enable.销钉1",
        "pin_2": "enable.销钉2",
        "pin_3": "enable.销钉3",
        "pin_4": "enable.销钉4",
        # 扭力 / 伺服距离 OK 上下限
        "torque_ok_low_1": "settings.torque_ok_low_1",
        "torque_ok_high_1": "settings.torque_ok_high_1",
        "torque_ok_low_2": "settings.torque_ok_low_2",
        "torque_ok_high_2": "settings.torque_ok_high_2",
        "torque_ok_low_3": "settings.torque_ok_low_3",
        "torque_ok_high_3": "settings.torque_ok_high_3",
        "torque_ok_low_4": "settings.torque_ok_low_4",
        "torque_ok_high_4": "settings.torque_ok_high_4",
        "servo_dist_ok_low_1": "settings.servo_dist_ok_low_1",
        "servo_dist_ok_high_1": "settings.servo_dist_ok_high_1",
        "servo_dist_ok_low_2": "settings.servo_dist_ok_low_2",
        "servo_dist_ok_high_2": "settings.servo_dist_ok_high_2",
        "servo_dist_ok_low_3": "settings.servo_dist_ok_low_3",
        "servo_dist_ok_high_3": "settings.servo_dist_ok_high_3",
        "servo_dist_ok_low_4": "settings.servo_dist_ok_low_4",
        "servo_dist_ok_high_4": "settings.servo_dist_ok_high_4",
    }

    SETTING_READBACK_PATHS = {
        "standby_time": "settings.standby_time",
        "run_mode": "settings.run_mode",
        # 功能开关
        "scan_code": "enable.扫码枪",
        "side_oil": "enable.侧油",
        "side_air": "enable.侧气",
        "water_tank": "enable.水箱",
        "pin_1": "enable.销钉1",
        "pin_2": "enable.销钉2",
        "pin_3": "enable.销钉3",
        "pin_4": "enable.销钉4",
        # 扭力 / 伺服距离 OK 上下限
        "torque_ok_low_1": "settings.torque_ok_low_1",
        "torque_ok_high_1": "settings.torque_ok_high_1",
        "torque_ok_low_2": "settings.torque_ok_low_2",
        "torque_ok_high_2": "settings.torque_ok_high_2",
        "torque_ok_low_3": "settings.torque_ok_low_3",
        "torque_ok_high_3": "settings.torque_ok_high_3",
        "torque_ok_low_4": "settings.torque_ok_low_4",
        "torque_ok_high_4": "settings.torque_ok_high_4",
        "servo_dist_ok_low_1": "settings.servo_dist_ok_low_1",
        "servo_dist_ok_high_1": "settings.servo_dist_ok_high_1",
        "servo_dist_ok_low_2": "settings.servo_dist_ok_low_2",
        "servo_dist_ok_high_2": "settings.servo_dist_ok_high_2",
        "servo_dist_ok_low_3": "settings.servo_dist_ok_low_3",
        "servo_dist_ok_high_3": "settings.servo_dist_ok_high_3",
        "servo_dist_ok_low_4": "settings.servo_dist_ok_low_4",
        "servo_dist_ok_high_4": "settings.servo_dist_ok_high_4",
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = {
            "standby_time": 60,
            "run_mode": 1,
            "scan_code": False,
            "side_oil": False,
            "side_air": False,
            "water_tank": False,
            "pin_1": False,
            "pin_2": False,
            "pin_3": False,
            "pin_4": False,
            "serial_port": "",
            # 扭力 / 伺服距离 OK 上下限(real)
            "torque_ok_low_1": 0.0,
            "torque_ok_high_1": 0.0,
            "torque_ok_low_2": 0.0,
            "torque_ok_high_2": 0.0,
            "torque_ok_low_3": 0.0,
            "torque_ok_high_3": 0.0,
            "torque_ok_low_4": 0.0,
            "torque_ok_high_4": 0.0,
            "servo_dist_ok_low_1": 0.0,
            "servo_dist_ok_high_1": 0.0,
            "servo_dist_ok_low_2": 0.0,
            "servo_dist_ok_high_2": 0.0,
            "servo_dist_ok_low_3": 0.0,
            "servo_dist_ok_high_3": 0.0,
            "servo_dist_ok_low_4": 0.0,
            "servo_dist_ok_high_4": 0.0,
        }
        # store_path -> config key 反向索引
        self._path_to_key: dict[str, str] = {}
        for key, store_path in self.SETTING_WRITE_PATHS.items():
            self._path_to_key[store_path] = key
        for key, store_path in self.SETTING_READBACK_PATHS.items():
            self._path_to_key[store_path] = key

    # ---------- 属性 ----------

    @property
    def plc_write_paths(self) -> dict[str, str]:
        return dict(self.SETTING_WRITE_PATHS)

    @property
    def plc_readback_paths(self) -> dict[str, str]:
        return dict(self.SETTING_READBACK_PATHS)

    @property
    def plc_managed_keys(self) -> set[str]:
        return set(self.plc_write_paths) | set(self.plc_readback_paths)

    @property
    def unmanaged_keys(self) -> set[str]:
        return set(self.config) - self.plc_managed_keys

    @property
    def write_only_keys(self) -> set[str]:
        return set(self.plc_write_paths) - set(self.plc_readback_paths)

    # ---------- 数据更新 ----------

    def update_config(self, **kwargs):
        """批量更新 config 字段，有变更则 emit dataChanged。"""
        changed = False
        for key, value in kwargs.items():
            if key in self.config and self.config[key] != value:
                self.config[key] = value
                changed = True

        if changed:
            self.dataChanged.emit()

    def set_standby_time(self, value: int, write: bool = False):
        """设置无操作待机时间。"""
        self.update_config(standby_time=value)
        if write:
            self._write_setting("standby_time", value)

    def set_feature_enabled(self, key: str, enabled: bool, write: bool = True):
        """切换功能开关(扫码/侧油/侧气/水箱)。"""
        self.update_config(**{key: enabled})
        if write:
            self._write_setting(key, enabled)

    def set_run_mode(self, mode: int, write: bool = True) -> bool:
        """设置运行模式: 1=全功能, 2=压装, 3=自动。"""
        try:
            mode = int(mode)
        except (TypeError, ValueError):
            print(f"[Settings] 无效运行模式: {mode}")
            return False

        if mode not in RUN_MODE_OPTIONS:
            print(f"[Settings] 无效运行模式: {mode}")
            return False

        self.update_config(run_mode=mode)
        if write:
            self._write_setting("run_mode", mode)
        return True

    def set_serial_port(self, port: str):
        """设置扫码枪串口号，仅保存在本地配置。"""
        port = str(port or "")
        if self.config["serial_port"] == port:
            return

        self.config["serial_port"] = port
        self.dataChanged.emit()
        self.serialPortChanged.emit(port)

    def set_limit_value(self, key: str, value: float, write: bool = False) -> bool:
        """设置扭力 / 伺服距离 OK 上下限参数(real 类型)。"""
        reason = self.validate_limit_value(key, value)
        if reason:
            print(f"[Settings] 写入被拒绝: {key}={value}, 原因: {reason}")
            return False

        self.update_config(**{key: value})
        if write:
            self._write_setting(key, value)
        return True

    # ---------- PLC 写入 ----------

    def write_plc(self, store_path: str, value):
        """请求 PLCBridge 将 value 写入 PLC。"""
        print(f"[Settings] writeRequested emit: {store_path}={value}")
        self.writeRequested.emit(store_path, value)

    # ---------- PLC 回读 ----------

    @pyqtSlot(str, object)
    def apply_plc_value(self, store_path: str, value):
        """PLCBridge 周期轮询读回数据后调用，更新 config。"""
        key = self._resolve_store_key(store_path)
        if not key:
            return

        if key == "run_mode":
            try:
                value = int(value)
            except (TypeError, ValueError):
                return
            if value not in RUN_MODE_OPTIONS:
                return

        if self.config[key] != value:
            self.config[key] = value
            self.dataChanged.emit()

    # ---------- 序列化 ----------

    def to_dict(self) -> dict:
        return {"config": dict(self.config)}

    # ---------- 内部工具 ----------

    def _write_setting(self, key: str, value):
        store_path = self.plc_write_paths.get(key)
        if store_path:
            self.write_plc(store_path, value)

    def get_limit_pair(self, key: str) -> tuple[str, str] | None:
        return _LIMIT_PAIR_BY_KEY.get(key)

    def validate_limit_value(self, key: str, value: float) -> str | None:
        pair = self.get_limit_pair(key)
        if pair is None:
            return f"unknown limit key: {key}"

        low_key, high_key = pair
        low_value = value if key == low_key else float(self.config[low_key])
        high_value = value if key == high_key else float(self.config[high_key])

        if low_value > high_value:
            return f"{low_key}>{high_key}"
        return None

    def _resolve_store_key(self, store_path: str) -> str | None:
        parts = store_path.split(".")
        if len(parts) == 2 and parts[0] == "settings" and parts[1] in self.config:
            return parts[1]
        return self._path_to_key.get(store_path)
