"""
PLCBinding — Store 字段 ↔ PLC 地址的绑定规则数据类
"""
from dataclasses import dataclass


@dataclass
class PLCBinding:
    """一条 Store 字段 ↔ PLC 地址的声明式绑定规则

    Attributes:
        store_path:   Store 字段路径, 如 "signals.顶缸上限", "servo.1.target_pos"
        plc_area:     PLC 区域: "M" (M 区) 或 "V" (V 区，snap7 映射为 DB1)
        byte_offset:  字节偏移, 如 M3.0 → 3, VW500 → 500
        bit_offset:   位偏移 (bool 类型 0~7, 非 bool 类型为 -1)
        data_type:    数据类型: "bool" | "byte" | "int16" | "int32" | "real" | "bytes"
        direction:    数据方向: "read" (PLC→Store) | "write" (Store→PLC)
        write_mode:   写入模式: "pulse" (瞬时脉冲) | "level" (电平保持) | "none" (只读)
        description:  可选描述，便于维护
    """
    store_path: str
    plc_area: str           # "M" | "V"
    byte_offset: int
    bit_offset: int = -1    # bool 类型 0~7, 其他为 -1
    data_type: str = "bool"
    direction: str = "read"
    write_mode: str = "none"
    description: str = ""
    byte_length: int = 0

    @property
    def byte_size(self) -> int:
        """该绑定占用的字节数"""
        if self.data_type == "bytes":
            return self.byte_length
        return {
            "bool": 1,
            "byte": 1,
            "int16": 2,
            "int32": 4,
            "real": 4,
        }.get(self.data_type, 1)

    @property
    def address_str(self) -> str:
        """返回可读的 PLC 地址字符串, 如 'M3.0', 'VW500'"""
        if self.plc_area == "M":
            if self.data_type == "bool":
                return f"M{self.byte_offset}.{self.bit_offset}"
            return f"MB{self.byte_offset}"
        else:  # V 区
            if self.data_type == "bool":
                return f"V{self.byte_offset}.{self.bit_offset}"
            prefix = {"byte": "VB", "int16": "VW", "int32": "VD", "real": "VD", "bytes": "VB"}
            return f"{prefix.get(self.data_type, 'V')}{self.byte_offset}"
