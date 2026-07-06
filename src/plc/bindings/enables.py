from src.plc.binding import PLCBinding


ENABLE_BINDINGS = [
    PLCBinding("enable.侧油",       "M", 9, 3, "bool", "write", "level", "UISetEnable侧油"),
    PLCBinding("enable.侧油",       "M", 9, 3, "bool", "read",  "none",  "ReadEnable侧油"),
    PLCBinding("enable.侧气",       "M", 9, 4, "bool", "write", "level", "UISetEnable侧气"),
    PLCBinding("enable.侧气",       "M", 9, 4, "bool", "read",  "none",  "ReadEnable侧气"),
    PLCBinding("enable.水箱",       "M", 9, 5, "bool", "write", "level", "UISetEnable水箱"),
    PLCBinding("enable.水箱",       "M", 9, 5, "bool", "read",  "none",  "ReadEnable水箱"),
    PLCBinding("enable.高压水气检", "M", 9, 6, "bool", "write", "level", "UISetEnable高压水气检"),
    PLCBinding("enable.低压水气检", "M", 9, 7, "bool", "write", "level", "UISetEnable低压水气检"),
    PLCBinding("enable.一切换二路", "M", 10, 0, "bool", "write", "level", "UISetEnable一切换二路"),
    PLCBinding("enable.启停气密仪", "M", 10, 1, "bool", "write", "level", "MaualVirtual启停气密仪"),
    PLCBinding("enable.扫码枪",     "M", 14, 6, "bool", "write", "level", "UISetEnable扫码枪"),
    PLCBinding("enable.扫码枪",     "M", 14, 6, "bool", "read",  "none",  "ReadEnable扫码枪"),
    PLCBinding("enable.销钉1",       "M", 11, 0, "bool", "write", "level", "UISetEnable销钉1"),
    PLCBinding("enable.销钉1",       "M", 11, 0, "bool", "read",  "none",  "ReadEnable销钉1"),
    PLCBinding("enable.销钉2",       "M", 17, 6, "bool", "write", "level", "UISetEnable销钉2"),
    PLCBinding("enable.销钉2",       "M", 17, 6, "bool", "read",  "none",  "ReadEnable销钉2"),
    PLCBinding("enable.销钉3",       "M", 17, 7, "bool", "write", "level", "UISetEnable销钉3"),
    PLCBinding("enable.销钉3",       "M", 17, 7, "bool", "read",  "none",  "ReadEnable销钉3"),
    PLCBinding("enable.销钉4",       "M", 18, 0, "bool", "write", "level", "UISetEnable销钉4"),
    PLCBinding("enable.销钉4",       "M", 18, 0, "bool", "read",  "none",  "ReadEnable销钉4"),
]

# ============================================================
#  伺服控制 — M 区 (bool 控制位)
# ============================================================
