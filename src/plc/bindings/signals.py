from src.plc.binding import PLCBinding


SIGNAL_BINDINGS = [
    PLCBinding("signals.顶缸上限", "M", 2, 1, "bool", "read", "none", "i顶缸上限位"),
    PLCBinding("signals.顶缸下限", "M", 2, 2, "bool", "read", "none", "i顶杆下限位"),
    PLCBinding("signals.水箱上限", "M", 1, 2, "bool", "read", "none", "i水箱升到位"),
    PLCBinding("signals.水箱下限", "M", 1, 3, "bool", "read", "none", "i水箱j降到位"),
    PLCBinding("signals.销钉1",    "M", 2, 3, "bool", "read", "none", "iHas销钉1"),
    PLCBinding("signals.销钉2",    "M", 2, 4, "bool", "read", "none", "iHas销钉2"),
    PLCBinding("signals.销钉3",    "M", 17, 4, "bool", "read", "none", "iHas销钉3"),
    PLCBinding("signals.销钉4",    "M", 17, 5, "bool", "read", "none", "iHas销钉4"),
    PLCBinding("signals.OK",       "M", 8, 1, "bool", "read", "none", "QOK"),
    PLCBinding("signals.NG",       "M", 8, 2, "bool", "read", "none", "QNG"),
]

# ============================================================
#  Q 输出状态 (PLC → Store, 只读)
# ============================================================
