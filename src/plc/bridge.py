"""
PLC bridge thread.
"""
import struct

from PyQt6.QtCore import QMutex, QMutexLocker, QThread, pyqtSignal
from snap7.util import get_bool

from src.common.logging_utils import debug_log
from src.plc.binding import PLCBinding
from src.plc.binding_config import READ_BINDINGS, WRITE_BINDINGS
from src.plc.driver import PLCDriver


class PLCBridge(QThread):
    connectionChanged = pyqtSignal(bool)
    errorOccurred = pyqtSignal(str)
    storeUpdateRequested = pyqtSignal(str, object)

    def __init__(self, driver: PLCDriver, plc_ip: str, parent=None):
        super().__init__(parent)
        self._driver = driver
        self._plc_ip = plc_ip
        self._stopped = False
        self._poll_interval_ms = 100
        self._reconnect_interval_ms = 3000
        self._mutex = QMutex()
        self._read_cache: dict[str, object] = {}
        self._stores: dict[str, object] = {}
        self._write_index: dict[str, PLCBinding] = {
            binding.store_path: binding for binding in WRITE_BINDINGS
        }
        self._read_index: dict[str, PLCBinding] = {
            binding.store_path: binding for binding in READ_BINDINGS
        }
        self._read_groups = self._build_read_groups()

    def register_store(self, name: str, store):
        self._stores[name] = store

        if hasattr(store, "writeRequested"):
            store.writeRequested.connect(self._on_write_requested)

        if hasattr(store, "apply_plc_value"):
            self.storeUpdateRequested.connect(store.apply_plc_value)

    def run(self):
        was_connected = False

        while not self._stopped:
            if not self._driver.is_connected():
                if was_connected:
                    self.connectionChanged.emit(False)
                    was_connected = False

                self._try_connect()
                if not self._driver.is_connected():
                    self.msleep(self._reconnect_interval_ms)
                    continue

            if not was_connected:
                self.connectionChanged.emit(True)
                was_connected = True

            try:
                self._poll_read()
            except Exception as exc:
                self.errorOccurred.emit(str(exc))

            self.msleep(self._poll_interval_ms)

        self._driver.disconnect()

    def stop(self):
        self._stopped = True
        self.wait(3000)

    def _try_connect(self):
        try:
            self._driver.connect(self._plc_ip, rack=0, slot=1)
        except Exception as exc:
            self.errorOccurred.emit(str(exc))

    def _build_read_groups(self):
        groups: dict[str, list[tuple[int, int, PLCBinding]]] = {}

        for binding in READ_BINDINGS:
            area_groups = groups.setdefault(binding.plc_area, [])
            area_groups.append(
                (binding.byte_offset, binding.byte_offset + binding.byte_size, binding)
            )

        merged_groups = {}
        for area, items in groups.items():
            items.sort(key=lambda item: item[0])
            merged = []
            for start, end, binding in items:
                if merged and start - merged[-1][1] <= 8:
                    merged[-1] = (
                        merged[-1][0],
                        max(merged[-1][1], end),
                        merged[-1][2] + [binding],
                    )
                else:
                    merged.append((start, end, [binding]))
            merged_groups[area] = merged

        return merged_groups

    def _poll_read(self):
        pending_updates = []
        with QMutexLocker(self._mutex):
            for area, groups in self._read_groups.items():
                for start, end, bindings in groups:
                    try:
                        raw = self._driver.read_bytes(area, start, end - start)
                    except Exception as exc:
                        self.errorOccurred.emit(f"read {area}[{start}:{end}] failed: {exc}")
                        continue

                    for binding in bindings:
                        local_offset = binding.byte_offset - start
                        value = self._extract_value(raw, local_offset, binding)
                        cached = self._read_cache.get(binding.store_path)
                        if cached != value:
                            self._read_cache[binding.store_path] = value
                            pending_updates.append((binding.store_path, value))

        for store_path, value in pending_updates:
            if store_path == "gas.trigger":
                continue
            self.storeUpdateRequested.emit(store_path, value)

        for store_path, value in pending_updates:
            if store_path != "gas.trigger":
                continue
            self.storeUpdateRequested.emit(store_path, value)

    def _extract_value(self, raw: bytes, offset: int, binding: PLCBinding):
        data_type = binding.data_type
        if data_type == "bool":
            return get_bool(bytearray(raw), offset, binding.bit_offset)
        if data_type == "byte":
            return raw[offset]
        if data_type == "bytes":
            return raw[offset : offset + binding.byte_size]
        if data_type == "int16":
            return struct.unpack(">h", raw[offset : offset + 2])[0]
        if data_type == "int32":
            return struct.unpack(">i", raw[offset : offset + 4])[0]
        if data_type == "real":
            return round(struct.unpack(">f", raw[offset : offset + 4])[0], 4)
        return None

    def _on_write_requested(self, store_path: str, value):
        debug_log(f"[PLCBridge] 收到写入请求: {store_path}={value}")
        binding = self._write_index.get(store_path)
        if not binding:
            self.errorOccurred.emit(f"missing binding for {store_path}")
            return False

        try:
            with QMutexLocker(self._mutex):
                normalized = self._write_value(binding, value)
                self._prime_read_cache(store_path, normalized)
            debug_log(f"[PLCBridge] 写入成功: {binding.address_str}={value}")
            return True
        except Exception as exc:
            self.errorOccurred.emit(f"write {binding.address_str} failed: {exc}")
            return False

    def _write_value(self, binding: PLCBinding, value):
        data_type = binding.data_type
        area = binding.plc_area
        offset = binding.byte_offset

        if data_type == "bool":
            normalized = bool(value)
            self._driver.write_bool(area, offset, binding.bit_offset, normalized)
            return normalized
        if data_type == "byte":
            normalized = int(value)
            self._driver.write_byte(area, offset, normalized)
            return normalized
        if data_type == "int16":
            normalized = int(value)
            self._driver.write_int16(area, offset, normalized)
            return normalized
        if data_type == "int32":
            normalized = int(value)
            self._driver.write_int32(area, offset, normalized)
            return normalized
        if data_type == "real":
            normalized = float(value)
            self._driver.write_real(area, offset, normalized)
            return normalized
        if data_type == "bytes":
            if isinstance(value, str):
                value = value.encode("gbk", errors="ignore")
            raw = bytes(value)
            target_len = binding.byte_size
            if len(raw) < target_len:
                raw = raw + b"\x00" * (target_len - len(raw))
            else:
                raw = raw[:target_len]
            self._driver.write_bytes(area, offset, raw)
            return raw
        raise ValueError(f"unsupported write data type: {data_type}")

    def _prime_read_cache(self, store_path: str, value):
        if store_path not in self._read_index:
            return
        self._read_cache[store_path] = value

    def write(self, store_path: str, value):
        return self._on_write_requested(store_path, value)
