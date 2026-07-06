from src.plc.binding import PLCBinding


BUTTON_BINDINGS = [
    PLCBinding("btn.顶缸伸出",     "M", 3, 0, "bool", "write", "pulse", "Btn顶缸伸出"),
    PLCBinding("btn.顶缸缩回",     "M", 3, 1, "bool", "write", "pulse", "Btn顶缸缩回"),
    PLCBinding("btn.侧顶油伸出",   "M", 3, 5, "bool", "write", "pulse", "Btn侧顶油伸出"),
    PLCBinding("btn.侧顶油缩回",   "M", 3, 6, "bool", "write", "pulse", "Btn侧顶油缩回"),
    PLCBinding("btn.侧气顶出",     "M", 4, 2, "bool", "write", "pulse", "Btn侧气顶出"),
    PLCBinding("btn.侧气缩回",     "M", 4, 3, "bool", "write", "pulse", "Btn侧气缩回"),
    PLCBinding("btn.高压气检启停", "M", 4, 7, "bool", "write", "pulse", "Btn高压气检启停"),
    PLCBinding("btn.低压气检启停", "M", 5, 0, "bool", "write", "pulse", "Btn低压气检启停"),
    PLCBinding("btn.打点伸出",     "M", 5, 4, "bool", "write", "pulse", "Btn打点伸出"),
    PLCBinding("btn.打点缩回",     "M", 5, 5, "bool", "write", "pulse", "Btn打点缩回"),
    PLCBinding("btn.水箱上升",     "M", 6, 1, "bool", "write", "pulse", "Btn水箱上升启停"),
    PLCBinding("btn.水箱下降",     "M", 6, 2, "bool", "write", "pulse", "Btn水箱下降启停"),
    PLCBinding("btn.高压水检",     "M", 6, 6, "bool", "write", "pulse", "Btn高压水检启停"),
    PLCBinding("btn.低压水检",     "M", 7, 0, "bool", "write", "pulse", "Btn低压水检启停"),
    PLCBinding("btn.工作台推出",   "M", 7, 3, "bool", "write", "pulse", "Btn工作台推出"),
    PLCBinding("btn.工作台退回",   "M", 7, 4, "bool", "write", "pulse", "Btn工作台退回"),
    PLCBinding("btn.启动气密",     "M", 1, 0, "bool", "write", "pulse", "Btn启动气密"),
    PLCBinding("btn.停止气密",     "M", 1, 1, "bool", "write", "pulse", "Btn停止气密"),
    PLCBinding("btn.清零计数",     "M", 2, 7, "bool", "write", "pulse", "Btn清零合格不合格计数"),
]

# ============================================================
#  开关 / 使能 (Store → PLC, 电平保持)
# ============================================================
