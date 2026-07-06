"""
Snap7Driver — 基于 python-snap7 的 S7-200 SMART 驱动实现

关键: S7-200 SMART 不支持标准 S7-300/400 的 COTP rack/slot 协商,
      必须使用 set_connection_params() 设置 TSAP 连接:
        - local_tsap = 0x1000 (snap7 客户端)
        - remote_tsap = 0x0300 (S7-200 SMART 服务端)

注意事项:
  - V 区通过 snap7 的 DB1 访问
  - M 区通过 Areas.MK 访问
  - S7 数据为 Big Endian，读写时需做字节序转换

兼容性: 同时支持 python-snap7 2.x (C库) 和 3.x (纯Python)
"""
import struct
import snap7
from snap7.util import get_bool, set_bool
from src.plc.driver import PLCDriver

# snap7 版本兼容: Areas 可能在 snap7.types 或 snap7.type
try:
    from snap7.types import Areas
except ImportError:
    try:
        from snap7.type import Areas
    except ImportError:
        Areas = None  # snap7 3.0: 使用字符串 area 标识

# 检测 snap7 版本 (3.x 为纯 Python, 无 _lib)
_SNAP7_V3 = not hasattr(snap7.client.Client(), '_lib')


class Snap7Driver(PLCDriver):
    """python-snap7 驱动实现，适配 S7-200 SMART ST20

    连接方式: 使用 TSAP 参数连接 (非 rack/slot)
    默认 TSAP: local=0x1000, remote=0x0300
    """

    # S7-200 SMART: V 区通过 DB1 访问
    _V_DB_NUMBER = 1

    # S7-200 SMART 默认 TSAP 参数
    _DEFAULT_LOCAL_TSAP = 0x1000   # snap7 客户端
    _DEFAULT_REMOTE_TSAP = 0x0300  # S7-200 SMART 服务端

    def __init__(self):
        self._client = snap7.client.Client()
        self._connected = False

    # ---- 生命周期 ----

    def connect(self, ip: str, rack: int = 0, slot: int = 1) -> bool:
        """连接 S7-200 SMART PLC

        注意: rack/slot 参数被忽略, S7-200 SMART 使用 TSAP 连接方式。
        自动检测 python-snap7 版本 (2.x / 3.x) 并使用对应连接方式。
        """
        try:
            # 1. 设置 TSAP 连接参数
            self._client.set_connection_params(
                ip,
                self._DEFAULT_LOCAL_TSAP,
                self._DEFAULT_REMOTE_TSAP
            )

            if _SNAP7_V3:
                # python-snap7 3.x: 纯 Python 实现
                # connect() 会覆盖 remote_tsap，所以手动建连接
                from snap7.connection import ISOTCPConnection
                self._client.host = ip
                self._client.port = 102
                self._client.connection = ISOTCPConnection(
                    host=ip,
                    port=102,
                    local_tsap=self._DEFAULT_LOCAL_TSAP,
                    remote_tsap=self._DEFAULT_REMOTE_TSAP,
                )
                self._client.connection.connect()
                self._client._setup_communication()
                self._client.connected = True
            else:
                # python-snap7 2.x: C 库实现
                from snap7.error import check_error
                check_error(self._client._lib.Cli_Connect(self._client._s7_client))

            self._connected = self._client.get_connected()
            if self._connected:
                print(f"[Snap7Driver] 已连接 PLC: {ip} (TSAP: 0x{self._DEFAULT_LOCAL_TSAP:04X}/0x{self._DEFAULT_REMOTE_TSAP:04X})")
            return self._connected
        except Exception as e:
            print(f"[Snap7Driver] 连接失败: {e}")
            self._connected = False
            return False

    def disconnect(self) -> None:
        """断开连接"""
        try:
            if self._connected:
                self._client.disconnect()
                print("[Snap7Driver] 已断开 PLC 连接")
        except Exception as e:
            print(f"[Snap7Driver] 断开连接异常: {e}")
        finally:
            self._connected = False

    def is_connected(self) -> bool:
        """返回连接状态（带实时检查）"""
        try:
            self._connected = self._client.get_connected()
        except Exception:
            self._connected = False
        return self._connected

    # ---- 内部辅助 ----

    def _read_area(self, area: str, byte_offset: int, size: int) -> bytearray:
        """统一读取 M 区或 V 区的原始字节"""
        if area == "M":
            return self._client.read_area(Areas.MK, 0, byte_offset, size)
        elif area == "V":
            return self._client.db_read(self._V_DB_NUMBER, byte_offset, size)
        else:
            raise ValueError(f"不支持的 PLC 区域: {area}")

    def _write_area(self, area: str, byte_offset: int, data: bytearray) -> None:
        """统一写入 M 区或 V 区的原始字节"""
        if area == "M":
            self._client.write_area(Areas.MK, 0, byte_offset, data)
        elif area == "V":
            self._client.db_write(self._V_DB_NUMBER, byte_offset, data)
        else:
            raise ValueError(f"不支持的 PLC 区域: {area}")

    # ---- 读操作 ----

    def read_bool(self, area: str, byte_offset: int, bit_offset: int) -> bool:
        data = self._read_area(area, byte_offset, 1)
        return get_bool(data, 0, bit_offset)

    def read_byte(self, area: str, byte_offset: int) -> int:
        data = self._read_area(area, byte_offset, 1)
        return data[0]

    def read_int16(self, area: str, byte_offset: int) -> int:
        data = self._read_area(area, byte_offset, 2)
        return struct.unpack(">h", data)[0]  # Big Endian signed int16

    def read_int32(self, area: str, byte_offset: int) -> int:
        data = self._read_area(area, byte_offset, 4)
        return struct.unpack(">i", data)[0]  # Big Endian signed int32

    def read_real(self, area: str, byte_offset: int) -> float:
        data = self._read_area(area, byte_offset, 4)
        return struct.unpack(">f", data)[0]  # Big Endian float32

    # ---- 写操作 ----

    def write_bool(self, area: str, byte_offset: int, bit_offset: int, value: bool) -> None:
        # 先读取当前字节，修改目标位，再写回（保护其他位）
        data = self._read_area(area, byte_offset, 1)
        set_bool(data, 0, bit_offset, value)
        self._write_area(area, byte_offset, data)

    def write_byte(self, area: str, byte_offset: int, value: int) -> None:
        data = bytearray([value & 0xFF])
        self._write_area(area, byte_offset, data)

    def write_int16(self, area: str, byte_offset: int, value: int) -> None:
        data = bytearray(struct.pack(">h", value))  # Big Endian
        self._write_area(area, byte_offset, data)

    def write_int32(self, area: str, byte_offset: int, value: int) -> None:
        data = bytearray(struct.pack(">i", value))  # Big Endian
        self._write_area(area, byte_offset, data)

    def write_real(self, area: str, byte_offset: int, value: float) -> None:
        data = bytearray(struct.pack(">f", value))  # Big Endian
        self._write_area(area, byte_offset, data)

    def write_bytes(self, area: str, byte_offset: int, data: bytes) -> None:
        self._write_area(area, byte_offset, bytearray(data))

    # ---- 批量读 ----

    def read_bytes(self, area: str, byte_offset: int, length: int) -> bytes:
        """批量读取连续字节块"""
        return bytes(self._read_area(area, byte_offset, length))
