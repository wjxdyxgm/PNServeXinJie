"""
PLC 地址绑定映射表 — 声明式配置

所有 Store 字段与 PLC 地址的绑定关系均在此文件配置。
新增 PLC 点位只需在此新增一行 PLCBinding，无需修改 PLCBridge 或 PLCDriver。

地址规则:
  - M 区: byte_offset = M 地址的字节号, bit_offset = 位号
    例: M3.0 → byte_offset=3, bit_offset=0
  - V 区 bool: byte_offset 和 bit_offset 同理
    例: V600.4 → byte_offset=600, bit_offset=4
  - V 区 VB/VW/VD: byte_offset = 地址偏移, bit_offset = -1
    例: VW500 → byte_offset=500, VD502 → byte_offset=502
"""
from src.plc.binding import PLCBinding
from src.store.manual_store import ManualStore


# ============================================================
#  信号灯 / 传感器状态 (PLC → Store, 只读)
# ============================================================
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
MODE_BINDINGS = [
    PLCBinding("mode.手动模式", "M", 1, 4, "bool", "read", "none", "iMaual"),
    PLCBinding("mode.自动气检", "M", 1, 5, "bool", "read", "none", "iAutoGas"),
    PLCBinding("mode.自动水检", "M", 3, 4, "bool", "read", "none", "iAutoWater"),
    PLCBinding("mode.急停",     "M", 1, 7, "bool", "read", "none", "iStop急停"),
    PLCBinding("mode.工作台推出", "M", 2, 3, "bool", "read", "none", "i工作台推出"),
    PLCBinding("mode.工作台缩回", "M", 2, 4, "bool", "read", "none", "i工作台缩回"),
]

# ============================================================
#  按钮操作 (Store → PLC, 瞬时脉冲: press=True / release=False)
# ============================================================
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
TORQUE_BINDINGS = [
    PLCBinding("torque.torque_1",           "V", 132, -1, "real",  "read",  "none",  "UIConv扭力1"),
    PLCBinding("torque.torque_2",           "V", 136, -1, "real",  "read",  "none",  "UIConv扭力2"),
    PLCBinding("torque.torque_3",           "V", 172, -1, "real",  "read",  "none",  "UIConv扭力3"),
    PLCBinding("torque.torque_4",           "V", 176, -1, "real",  "read",  "none",  "UIConv扭力4"),
    PLCBinding("settings.standby_time",     "V", 116, -1, "int16", "read",  "none",  "ReadUISet无操作待机"),
    PLCBinding("settings.standby_time",     "V", 116, -1, "int16", "write", "level", "UISet无操作待机"),
]

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

GAS_BINDINGS = [
    PLCBinding(
        "gas.trigger",
        "M",
        14,
        4,
        "bool",
        "read",
        "none",
        "GasCollectTrigger",
    ),
    PLCBinding(
        "gas.product_code_raw",
        "V",
        180,
        -1,
        "bytes",
        "read",
        "none",
        "GasProductCodeBuffer",
        byte_length=80,
    ),
    PLCBinding(
        "gas.product_code_raw",
        "V",
        180,
        -1,
        "bytes",
        "write",
        "level",
        "GasProductCodeBufferWrite",
        byte_length=80,
    ),
    PLCBinding(
        "gas.code_present",
        "M",
        12,
        3,
        "bool",
        "write",
        "level",
        "CondTrue有码",
    ),
    PLCBinding(
        "gas.reset_counts",
        "M",
        2,
        7,
        "bool",
        "write",
        "pulse",
        "Btn清零合格不合格计数",
    ),
    PLCBinding(
        "gas.run_seq",
        "V",
        22,
        -1,
        "int16",
        "read",
        "none",
        "RunSeq",
    ),
    PLCBinding(
        "gas.cond_true_ok",
        "M",
        12,
        4,
        "bool",
        "read",
        "none",
        "CondTrue气检合格",
    ),
    PLCBinding(
        "gas.cond_true_ng",
        "M",
        12,
        5,
        "bool",
        "read",
        "none",
        "CondTrue气检不合格",
    ),
    PLCBinding(
        "gas.airtight_result",
        "V",
        260,
        -1,
        "int16",
        "read",
        "none",
        "GasAirtightResult",
    ),
    PLCBinding(
        "gas.operator_raw",
        "V",
        262,
        -1,
        "bytes",
        "read",
        "none",
        "GasOperatorBuffer",
        byte_length=20,
    ),
    PLCBinding(
        "gas.operator_raw",
        "V",
        262,
        -1,
        "bytes",
        "write",
        "level",
        "GasOperatorBufferWrite",
        byte_length=20,
    ),
    PLCBinding(
        "gas.pin1_pressure",
        "V",
        282,
        -1,
        "real",
        "read",
        "none",
        "GasPin1Pressure",
    ),
    PLCBinding(
        "gas.pin1_pressure_result",
        "V",
        286,
        -1,
        "int16",
        "read",
        "none",
        "GasPin1PressureResult",
    ),
    PLCBinding(
        "gas.pin1_distance",
        "V",
        288,
        -1,
        "real",
        "read",
        "none",
        "GasPin1Distance",
    ),
    PLCBinding(
        "gas.pin1_distance_result",
        "V",
        292,
        -1,
        "int16",
        "read",
        "none",
        "GasPin1DistanceResult",
    ),
    PLCBinding(
        "gas.pin2_pressure",
        "V",
        294,
        -1,
        "real",
        "read",
        "none",
        "GasPin2Pressure",
    ),
    PLCBinding(
        "gas.pin2_pressure_result",
        "V",
        298,
        -1,
        "int16",
        "read",
        "none",
        "GasPin2PressureResult",
    ),
    PLCBinding(
        "gas.pin2_distance",
        "V",
        300,
        -1,
        "real",
        "read",
        "none",
        "GasPin2Distance",
    ),
    PLCBinding(
        "gas.pin2_distance_result",
        "V",
        304,
        -1,
        "int16",
        "read",
        "none",
        "GasPin2DistanceResult",
    ),
    PLCBinding(
        "gas.pin3_pressure",
        "V",
        306,
        -1,
        "real",
        "read",
        "none",
        "GasPin3Pressure",
    ),
    PLCBinding(
        "gas.pin3_pressure_result",
        "V",
        310,
        -1,
        "int16",
        "read",
        "none",
        "GasPin3PressureResult",
    ),
    PLCBinding(
        "gas.pin3_distance",
        "V",
        312,
        -1,
        "real",
        "read",
        "none",
        "GasPin3Distance",
    ),
    PLCBinding(
        "gas.pin3_distance_result",
        "V",
        316,
        -1,
        "int16",
        "read",
        "none",
        "GasPin3DistanceResult",
    ),
    PLCBinding(
        "gas.pin4_pressure",
        "V",
        318,
        -1,
        "real",
        "read",
        "none",
        "GasPin4Pressure",
    ),
    PLCBinding(
        "gas.pin4_pressure_result",
        "V",
        322,
        -1,
        "int16",
        "read",
        "none",
        "GasPin4PressureResult",
    ),
    PLCBinding(
        "gas.pin4_distance",
        "V",
        324,
        -1,
        "real",
        "read",
        "none",
        "GasPin4Distance",
    ),
    PLCBinding(
        "gas.pin4_distance_result",
        "V",
        328,
        -1,
        "int16",
        "read",
        "none",
        "GasPin4DistanceResult",
    ),
    PLCBinding(
        "gas.count_ok",
        "V",
        100,
        -1,
        "int16",
        "read",
        "none",
        "CountGasRun合格",
    ),
    PLCBinding(
        "gas.count_ng",
        "V",
        102,
        -1,
        "int16",
        "read",
        "none",
        "CountGasRun不合格",
    ),
    PLCBinding(
        "gas.count_total",
        "V",
        104,
        -1,
        "int16",
        "read",
        "none",
        "CountGasRun总数",
    ),
]


# ============================================================
#  汇总所有绑定
# ============================================================
MODE_WRITE_BINDINGS = [
    PLCBinding(ManualStore.MANUAL_MODE_PATH, "M", 1, 4, "bool", "write", "level", "UIManualMode"),
    PLCBinding(ManualStore.AUTO_GAS_MODE_PATH, "M", 1, 5, "bool", "write", "level", "UIAutoGasMode"),
]

ALL_BINDINGS = (
    SIGNAL_BINDINGS
    + Q_STATUS_BINDINGS
    + MODE_BINDINGS
    + MODE_WRITE_BINDINGS
    + BUTTON_BINDINGS
    + ENABLE_BINDINGS
    + SERVO_M_BINDINGS
    + SERVO_V_BINDINGS
    + TORQUE_BINDINGS
    + SETTINGS_RUN_MODE_BINDINGS
    + SETTINGS_LIMIT_BINDINGS
    + GAS_BINDINGS
)

# 按方向分类 (供 PLCBridge 使用)
READ_BINDINGS = [b for b in ALL_BINDINGS if b.direction == "read"]
WRITE_BINDINGS = [b for b in ALL_BINDINGS if b.direction == "write"]
