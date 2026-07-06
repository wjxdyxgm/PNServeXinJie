from src.plc.binding import PLCBinding


SETTINGS_RUN_MODE_BINDINGS = [
    PLCBinding("settings.run_mode", "V", 28, -1, "int16", "read", "none", "ReadUIRunMode"),
    PLCBinding("settings.run_mode", "V", 28, -1, "int16", "write", "level", "UIRunMode"),
]

# ============================================================
#  设置参数 — 扭力OK / 伺服距离OK 上下限 (VD140–VD168, real, 读写)
# ============================================================


SETTINGS_LIMIT_BINDINGS = [
    # 扭力OK (2路)
    PLCBinding("settings.torque_ok_low_1",      "V", 140, -1, "real", "read",  "none",  "ReadUISet扭力OK下限1"),
    PLCBinding("settings.torque_ok_low_1",      "V", 140, -1, "real", "write", "level", "UISet扭力OK下限1"),
    PLCBinding("settings.torque_ok_high_1",     "V", 144, -1, "real", "read",  "none",  "ReadUISet扭力OK上限1"),
    PLCBinding("settings.torque_ok_high_1",     "V", 144, -1, "real", "write", "level", "UISet扭力OK上限1"),
    PLCBinding("settings.torque_ok_low_2",      "V", 148, -1, "real", "read",  "none",  "ReadUISet扭力OK下限2"),
    PLCBinding("settings.torque_ok_low_2",      "V", 148, -1, "real", "write", "level", "UISet扭力OK下限2"),
    PLCBinding("settings.torque_ok_high_2",     "V", 152, -1, "real", "read",  "none",  "ReadUISet扭力OK上限2"),
    PLCBinding("settings.torque_ok_high_2",     "V", 152, -1, "real", "write", "level", "UISet扭力OK上限2"),
    # 伺服距离OK (2路)
    PLCBinding("settings.servo_dist_ok_low_1",  "V", 156, -1, "real", "read",  "none",  "ReadUISet伺服距离OK下限1"),
    PLCBinding("settings.servo_dist_ok_low_1",  "V", 156, -1, "real", "write", "level", "UISet伺服距离OK下限1"),
    PLCBinding("settings.servo_dist_ok_high_1", "V", 160, -1, "real", "read",  "none",  "ReadUISet伺服距离OK上限1"),
    PLCBinding("settings.servo_dist_ok_high_1", "V", 160, -1, "real", "write", "level", "UISet伺服距离OK上限1"),
    PLCBinding("settings.servo_dist_ok_low_2",  "V", 164, -1, "real", "read",  "none",  "ReadUISet伺服距离OK下限2"),
    PLCBinding("settings.servo_dist_ok_low_2",  "V", 164, -1, "real", "write", "level", "UISet伺服距离OK下限2"),
    PLCBinding("settings.servo_dist_ok_high_2", "V", 168, -1, "real", "read",  "none",  "ReadUISet伺服距离OK上限2"),
    PLCBinding("settings.servo_dist_ok_high_2", "V", 168, -1, "real", "write", "level", "UISet伺服距离OK上限2"),
    # 伺服距离OK (3/4路)
    PLCBinding("settings.servo_dist_ok_low_3",  "V", 364, -1, "real", "read",  "none",  "ReadUISet伺服距离OK下限3"),
    PLCBinding("settings.servo_dist_ok_low_3",  "V", 364, -1, "real", "write", "level", "UISet伺服距离OK下限3"),
    PLCBinding("settings.servo_dist_ok_high_3", "V", 360, -1, "real", "read",  "none",  "ReadUISet伺服距离OK上限3"),
    PLCBinding("settings.servo_dist_ok_high_3", "V", 360, -1, "real", "write", "level", "UISet伺服距离OK上限3"),
    PLCBinding("settings.servo_dist_ok_low_4",  "V", 372, -1, "real", "read",  "none",  "ReadUISet伺服距离OK下限4"),
    PLCBinding("settings.servo_dist_ok_low_4",  "V", 372, -1, "real", "write", "level", "UISet伺服距离OK下限4"),
    PLCBinding("settings.servo_dist_ok_high_4", "V", 368, -1, "real", "read",  "none",  "ReadUISet伺服距离OK上限4"),
    PLCBinding("settings.servo_dist_ok_high_4", "V", 368, -1, "real", "write", "level", "UISet伺服距离OK上限4"),
    # 扭力OK (3/4路)
    PLCBinding("settings.torque_ok_low_3",      "V", 376, -1, "real", "read",  "none",  "ReadUISet扭力OK下限3"),
    PLCBinding("settings.torque_ok_low_3",      "V", 376, -1, "real", "write", "level", "UISet扭力OK下限3"),
    PLCBinding("settings.torque_ok_high_3",     "V", 380, -1, "real", "read",  "none",  "ReadUISet扭力OK上限3"),
    PLCBinding("settings.torque_ok_high_3",     "V", 380, -1, "real", "write", "level", "UISet扭力OK上限3"),
    PLCBinding("settings.torque_ok_low_4",      "V", 384, -1, "real", "read",  "none",  "ReadUISet扭力OK下限4"),
    PLCBinding("settings.torque_ok_low_4",      "V", 384, -1, "real", "write", "level", "UISet扭力OK下限4"),
    PLCBinding("settings.torque_ok_high_4",     "V", 388, -1, "real", "read",  "none",  "ReadUISet扭力OK上限4"),
    PLCBinding("settings.torque_ok_high_4",     "V", 388, -1, "real", "write", "level", "UISet扭力OK上限4"),
]
