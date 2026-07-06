"""
PLCDriver — PLC 协议驱动抽象基类
定义统一的读写接口，供不同协议实现类继承
"""
from abc import ABC, abstractmethod


class PLCDriver(ABC):
    """PLC 协议驱动抽象基类

    所有具体驱动（如 Snap7Driver）必须实现以下方法。
    地址参数统一使用 (area, byte_offset, bit_offset) 三元组。
    """

    # ---- 生命周期 ----

    @abstractmethod
    def connect(self, ip: str, rack: int = 0, slot: int = 1) -> bool:
        """连接 PLC，返回是否成功"""
        ...

    @abstractmethod
    def disconnect(self) -> None:
        """断开连接"""
        ...

    @abstractmethod
    def is_connected(self) -> bool:
        """返回当前连接状态"""
        ...

    # ---- 读操作 ----

    @abstractmethod
    def read_bool(self, area: str, byte_offset: int, bit_offset: int) -> bool:
        """读取单个 bool 位
        area: "M" 或 "V"
        """
        ...

    @abstractmethod
    def read_byte(self, area: str, byte_offset: int) -> int:
        """读取单个字节 (VB)"""
        ...

    @abstractmethod
    def read_int16(self, area: str, byte_offset: int) -> int:
        """读取 16 位整数 (VW)"""
        ...

    @abstractmethod
    def read_int32(self, area: str, byte_offset: int) -> int:
        """读取 32 位整数 (VD as int)"""
        ...

    @abstractmethod
    def read_real(self, area: str, byte_offset: int) -> float:
        """读取 32 位浮点数 (VD as float)"""
        ...

    # ---- 写操作 ----

    @abstractmethod
    def write_bool(self, area: str, byte_offset: int, bit_offset: int, value: bool) -> None:
        """写入单个 bool 位"""
        ...

    @abstractmethod
    def write_byte(self, area: str, byte_offset: int, value: int) -> None:
        """写入单个字节"""
        ...

    @abstractmethod
    def write_int16(self, area: str, byte_offset: int, value: int) -> None:
        """写入 16 位整数"""
        ...

    @abstractmethod
    def write_int32(self, area: str, byte_offset: int, value: int) -> None:
        """写入 32 位整数"""
        ...

    @abstractmethod
    def write_real(self, area: str, byte_offset: int, value: float) -> None:
        """写入 32 位浮点数"""
        ...

    @abstractmethod
    def write_bytes(self, area: str, byte_offset: int, data: bytes) -> None:
        """批量写入连续字节块（如 ASCII 缓冲区）"""
        ...

    # ---- 批量读 ----

    @abstractmethod
    def read_bytes(self, area: str, byte_offset: int, length: int) -> bytes:
        """批量读取连续字节块，用于 PLCBridge 优化轮询"""
        ...
