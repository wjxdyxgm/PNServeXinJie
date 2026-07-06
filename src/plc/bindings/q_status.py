from src.plc.binding import PLCBinding


Q_STATUS_BINDINGS = [
    PLCBinding("q_status.顶缸伸出",   "M", 3, 2, "bool", "read", "none", "Q顶缸伸出启停"),
    PLCBinding("q_status.顶缸缩回",   "M", 3, 3, "bool", "read", "none", "Q顶缸缩回启停"),
    PLCBinding("q_status.侧顶油伸出", "M", 3, 7, "bool", "read", "none", "Q侧顶油伸出启停"),
    PLCBinding("q_status.侧顶油缩回", "M", 4, 0, "bool", "read", "none", "Q侧顶油缩回启停"),
    PLCBinding("q_status.侧气顶出",   "M", 4, 4, "bool", "read", "none", "Q侧气顶出"),
    PLCBinding("q_status.侧气缩回",   "M", 4, 5, "bool", "read", "none", "Q侧气缩回"),
    PLCBinding("q_status.高压气检",   "M", 5, 1, "bool", "read", "none", "Q高压气检启停"),
    PLCBinding("q_status.低压气检",   "M", 5, 2, "bool", "read", "none", "Q低压气检启停"),
    PLCBinding("q_status.打点伸出",   "M", 5, 6, "bool", "read", "none", "Q打点伸出"),
    PLCBinding("q_status.打点缩回",   "M", 5, 7, "bool", "read", "none", "Q打点缩回"),
    PLCBinding("q_status.水箱上升",   "M", 6, 3, "bool", "read", "none", "Q水箱上升启停"),
    PLCBinding("q_status.水箱下降",   "M", 6, 4, "bool", "read", "none", "Q水箱下降启停"),
    PLCBinding("q_status.高压水检",   "M", 6, 7, "bool", "read", "none", "Q高压水检启停"),
    PLCBinding("q_status.低压水检",   "M", 7, 1, "bool", "read", "none", "Q低压水检启停"),
    PLCBinding("q_status.工作台推出", "M", 7, 5, "bool", "read", "none", "Q工作台推出"),
    PLCBinding("q_status.工作台退回", "M", 7, 6, "bool", "read", "none", "Q工作台退回"),
    PLCBinding("q_status.启动气密仪", "M", 7, 7, "bool", "read", "none", "Q启动气密仪"),
    PLCBinding("q_status.停止气密仪", "M", 8, 0, "bool", "read", "none", "Q停止气密仪"),
    PLCBinding("q_status.Error报警",  "M", 8, 3, "bool", "read", "none", "QError报警"),
    PLCBinding("q_status.启动运行灯", "M", 8, 4, "bool", "read", "none", "Q启动运行灯"),
    PLCBinding("q_status.三色绿运行", "M", 8, 5, "bool", "read", "none", "Q三色绿运行"),
    PLCBinding("q_status.三色红故障", "M", 8, 6, "bool", "read", "none", "Q三色红故障"),
    PLCBinding("q_status.三色黄等待", "M", 8, 7, "bool", "read", "none", "Q三色黄等待"),
    PLCBinding("q_status.原位指示",   "M", 9, 1, "bool", "read", "none", "Q原位指示"),
]

# ============================================================
#  模式 / 系统状态 (PLC → Store, 只读)
# ============================================================
