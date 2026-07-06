from src.plc.binding import PLCBinding


SERVO_M_BINDINGS = [
    # 伺服 1
    PLCBinding("servo.1.enable",  "M", 10, 2, "bool", "write", "level", "UISetEnable1"),
    PLCBinding("servo.1.enable",  "M", 10, 2, "bool", "read",  "none",  "ReadEnable1"),
    PLCBinding("servo.1.execute", "M", 10, 3, "bool", "write", "pulse", "UIBtnExecute1"),
    PLCBinding("servo.1.done",    "M", 10, 4, "bool", "read",  "none",  "UISinaPosDone1"),
    # 伺服 2
    PLCBinding("servo.2.enable",  "M", 10, 5, "bool", "write", "level", "UISetEnable2"),
    PLCBinding("servo.2.enable",  "M", 10, 5, "bool", "read",  "none",  "ReadEnable2"),
    PLCBinding("servo.2.execute", "M", 10, 6, "bool", "write", "pulse", "UIBtnExecute2"),
    PLCBinding("servo.2.done",    "M", 10, 7, "bool", "read",  "none",  "UISinaPosDone2"),
    # 伺服 3
    PLCBinding("servo.3.enable",  "M", 16, 2, "bool", "write", "level", "UISetEnable3"),
    PLCBinding("servo.3.enable",  "M", 16, 2, "bool", "read",  "none",  "ReadEnable3"),
    PLCBinding("servo.3.execute", "M", 16, 3, "bool", "write", "pulse", "UIBtnExecute3"),
    PLCBinding("servo.3.done",    "M", 16, 4, "bool", "read",  "none",  "UISinaPosDone3"),
    # 伺服 4
    PLCBinding("servo.4.enable",  "M", 16, 5, "bool", "write", "level", "UISetEnable4"),
    PLCBinding("servo.4.enable",  "M", 16, 5, "bool", "read",  "none",  "ReadEnable4"),
    PLCBinding("servo.4.execute", "M", 16, 6, "bool", "write", "pulse", "UIBtnExecute4"),
    PLCBinding("servo.4.done",    "M", 16, 7, "bool", "read",  "none",  "UISinaPosDone4"),
]

# ============================================================
#  伺服控制 — V 区 (写入参数 + 读取反馈)
# ============================================================


SERVO_V_BINDINGS = [
    # 伺服 1 写入
    PLCBinding("servo.1.mode",       "V", 500, -1, "int16", "write", "level", "UISetServeMode1"),
    PLCBinding("servo.1.target_pos", "V", 502, -1, "real",  "write", "level", "UISetServePos1"),
    PLCBinding("servo.1.mdi",        "V", 506, -1, "int32", "write", "level", "UISetMDI1"),
    PLCBinding("servo.1.zero_offset","V", 520, -1, "real",  "write", "level", "UISetZeroOffset1"),
    # 伺服 1 读取 (从 PLC 同步回 Store)
    PLCBinding("servo.1.target_pos", "V", 502, -1, "real",  "read",  "none",  "ReadServePos1"),
    PLCBinding("servo.1.mdi",        "V", 506, -1, "int32", "read",  "none",  "ReadMDI1"),
    PLCBinding("servo.1.zero_offset","V", 520, -1, "real",  "read",  "none",  "ReadZeroOffset1"),
    PLCBinding("servo.1.fly_ref",    "V", 600, 4,  "bool",  "write", "level", "UIBtnFlyRef1"),
    PLCBinding("servo.1.fly_ref",    "V", 600, 4,  "bool",  "read",  "none",  "ReadFlyRef1"),
    PLCBinding("servo.1.reset_err",  "V", 600, 5,  "bool",  "write", "pulse", "UISetResetErr1"),
    PLCBinding("servo.1.current_pos","V", 612, -1, "int32", "read",  "none",  "ActPosition1"),
    PLCBinding("servo.1.error_id",   "V", 651, -1, "byte",  "read",  "none",  "ErrorID1"),

    # 伺服 2 写入
    PLCBinding("servo.2.mode",       "V", 510, -1, "int16", "write", "level", "UISetServeMode2"),
    PLCBinding("servo.2.target_pos", "V", 512, -1, "real",  "write", "level", "UISetServePos2"),
    PLCBinding("servo.2.mdi",        "V", 516, -1, "int32", "write", "level", "UISetMDI2"),
    PLCBinding("servo.2.zero_offset","V", 524, -1, "real",  "write", "level", "UISetZeroOffset2"),
    # 伺服 2 读取 (从 PLC 同步回 Store)
    PLCBinding("servo.2.target_pos", "V", 512, -1, "real",  "read",  "none",  "ReadServePos2"),
    PLCBinding("servo.2.mdi",        "V", 516, -1, "int32", "read",  "none",  "ReadMDI2"),
    PLCBinding("servo.2.zero_offset","V", 524, -1, "real",  "read",  "none",  "ReadZeroOffset2"),
    PLCBinding("servo.2.fly_ref",    "V", 700, 4,  "bool",  "write", "level", "UIBtnFlyRef2"),
    PLCBinding("servo.2.fly_ref",    "V", 700, 4,  "bool",  "read",  "none",  "ReadFlyRef2"),
    PLCBinding("servo.2.reset_err",  "V", 700, 5,  "bool",  "write", "pulse", "UISetResetErr2"),
    PLCBinding("servo.2.current_pos","V", 712, -1, "int32", "read",  "none",  "ActPosition2"),
    PLCBinding("servo.2.error_id",   "V", 751, -1, "byte",  "read",  "none",  "ErrorID2"),

    # 伺服 3 写入
    PLCBinding("servo.3.mode",       "V", 528, -1, "int16", "write", "level", "UISetServeMode3"),
    PLCBinding("servo.3.target_pos", "V", 532, -1, "real",  "write", "level", "UISetServePos3"),
    PLCBinding("servo.3.mdi",        "V", 540, -1, "int32", "write", "level", "UISetMDI3"),
    PLCBinding("servo.3.zero_offset","V", 548, -1, "real",  "write", "level", "UISetZeroOffset3"),
    # 伺服 3 读取
    PLCBinding("servo.3.target_pos", "V", 532, -1, "real",  "read",  "none",  "ReadServePos3"),
    PLCBinding("servo.3.mdi",        "V", 540, -1, "int32", "read",  "none",  "ReadMDI3"),
    PLCBinding("servo.3.zero_offset","V", 548, -1, "real",  "read",  "none",  "ReadZeroOffset3"),
    PLCBinding("servo.3.fly_ref",    "V", 900, 4,  "bool",  "write", "level", "UIBtnFlyRef3"),
    PLCBinding("servo.3.fly_ref",    "V", 900, 4,  "bool",  "read",  "none",  "ReadFlyRef3"),
    PLCBinding("servo.3.reset_err",  "V", 900, 5,  "bool",  "write", "pulse", "UISetResetErr3"),
    PLCBinding("servo.3.current_pos","V", 912, -1, "int32", "read",  "none",  "ActPosition3"),
    PLCBinding("servo.3.error_id",   "V", 951, -1, "byte",  "read",  "none",  "ErrorID3"),

    # 伺服 4 写入
    PLCBinding("servo.4.mode",       "V", 530, -1, "int16", "write", "level", "UISetServeMode4"),
    PLCBinding("servo.4.target_pos", "V", 536, -1, "real",  "write", "level", "UISetServePos4"),
    PLCBinding("servo.4.mdi",        "V", 544, -1, "int32", "write", "level", "UISetMDI4"),
    PLCBinding("servo.4.zero_offset","V", 552, -1, "real",  "write", "level", "UISetZeroOffset4"),
    # 伺服 4 读取
    PLCBinding("servo.4.target_pos", "V", 536, -1, "real",  "read",  "none",  "ReadServePos4"),
    PLCBinding("servo.4.mdi",        "V", 544, -1, "int32", "read",  "none",  "ReadMDI4"),
    PLCBinding("servo.4.zero_offset","V", 552, -1, "real",  "read",  "none",  "ReadZeroOffset4"),
    PLCBinding("servo.4.fly_ref",    "V", 1100, 4,  "bool",  "write", "level", "UIBtnFlyRef4"),
    PLCBinding("servo.4.fly_ref",    "V", 1100, 4,  "bool",  "read",  "none",  "ReadFlyRef4"),
    PLCBinding("servo.4.reset_err",  "V", 1100, 5,  "bool",  "write", "pulse", "UISetResetErr4"),
    PLCBinding("servo.4.current_pos","V", 1112, -1, "int32", "read",  "none",  "ActPosition4"),
    PLCBinding("servo.4.error_id",   "V", 1151, -1, "byte",  "read",  "none",  "ErrorID4"),
]

# ============================================================
#  扭力数据 (VD132/VD136 只读) + 设置参数
# ============================================================
