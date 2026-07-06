from src.plc.binding import PLCBinding
from src.store.manual_store import ManualStore


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


MODE_WRITE_BINDINGS = [
    PLCBinding(ManualStore.MANUAL_MODE_PATH, "M", 1, 4, "bool", "write", "level", "UIManualMode"),
    PLCBinding(ManualStore.AUTO_GAS_MODE_PATH, "M", 1, 5, "bool", "write", "level", "UIAutoGasMode"),
]
