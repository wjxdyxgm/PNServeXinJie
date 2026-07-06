from src.plc.binding import PLCBinding


TORQUE_BINDINGS = [
    PLCBinding("torque.torque_1",           "V", 132, -1, "real",  "read",  "none",  "UIConv扭力1"),
    PLCBinding("torque.torque_2",           "V", 136, -1, "real",  "read",  "none",  "UIConv扭力2"),
    PLCBinding("torque.torque_3",           "V", 172, -1, "real",  "read",  "none",  "UIConv扭力3"),
    PLCBinding("torque.torque_4",           "V", 176, -1, "real",  "read",  "none",  "UIConv扭力4"),
    PLCBinding("settings.standby_time",     "V", 116, -1, "int16", "read",  "none",  "ReadUISet无操作待机"),
    PLCBinding("settings.standby_time",     "V", 116, -1, "int16", "write", "level", "UISet无操作待机"),
]
