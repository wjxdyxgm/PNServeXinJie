from __future__ import annotations

from collections.abc import Callable

from PyQt6.QtCore import QObject
from PyQt6.QtWidgets import QApplication

from src.common.db import GasRecordDB
from src.common.dev_config import get_plc_ip
from src.common.settings_persistence import load_local_settings, save_local_settings
from src.plc.bridge import PLCBridge
from src.plc.scanner_service import ScannerService
from src.plc.snap7_driver import Snap7Driver
from src.store.auth_store import AuthStore
from src.store.gas_store import GasStore
from src.store.manual_store import ManualStore
from src.store.settings_store import SettingsStore


class AppContext(QObject):
    """Owns application services and long-lived state objects."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.manual_store = ManualStore(self)
        self.auth_store = AuthStore(self)
        self.gas_db = GasRecordDB()
        self.gas_store = GasStore(db=self.gas_db, parent=self)
        self.settings_store = SettingsStore(self)

        self.plc_driver: Snap7Driver | None = None
        self.plc_bridge: PLCBridge | None = None
        self.scanner_service: ScannerService | None = None
        self._shutdown = False

        self._load_local_settings()
        self.settings_store.serialPortChanged.connect(self._save_local_settings)

    def create_plc_bridge(self) -> PLCBridge:
        if self.plc_bridge is not None:
            return self.plc_bridge

        self.plc_driver = Snap7Driver()
        self.plc_bridge = PLCBridge(self.plc_driver, get_plc_ip(), parent=self)
        self.plc_bridge.register_store("manual", self.manual_store)
        self.plc_bridge.register_store("gas", self.gas_store)
        self.plc_bridge.register_store("settings", self.settings_store)
        return self.plc_bridge

    def start_plc(self) -> PLCBridge:
        bridge = self.create_plc_bridge()
        if not bridge.isRunning():
            bridge.start()
        return bridge

    def create_scanner(self, should_capture: Callable[[], bool]) -> ScannerService:
        if self.scanner_service is None:
            self.scanner_service = ScannerService(should_capture, self)
        return self.scanner_service

    def start_scanner(self, application: QApplication | None = None) -> ScannerService | None:
        if self.scanner_service is None:
            return None
        self.scanner_service.start(application)
        return self.scanner_service

    def set_operator(self, username: str) -> bool:
        username = str(username or "").strip()
        if not username:
            return False

        self.auth_store.login(username, "admin", ["manual", "gas", "settings"])
        self.auth_store.clock_in()

        if self.plc_bridge is not None:
            self.plc_bridge.write("gas.operator_raw", username)

        self.gas_store.update_current_data(operator=username)
        return True

    def apply_barcode(self, barcode: str) -> bool:
        barcode = str(barcode or "").strip()
        if not barcode or self.plc_bridge is None:
            return False

        if not self.plc_bridge.write("gas.product_code_raw", barcode):
            return False

        self.gas_store.apply_plc_value("gas.product_code_raw", barcode)
        self.gas_store.signal_code_present()
        return True

    def shutdown(self) -> None:
        if self._shutdown:
            return
        self._shutdown = True
        if self.scanner_service is not None and hasattr(self.scanner_service, "stop"):
            self.scanner_service.stop()
        if self.plc_bridge is not None and hasattr(self.plc_bridge, "stop"):
            self.plc_bridge.stop()
        self.gas_db.close()

    def _load_local_settings(self) -> None:
        payload = load_local_settings()
        serial_port = payload.get("serial_port")
        if isinstance(serial_port, str):
            self.settings_store.set_serial_port(serial_port)

    def _save_local_settings(self, _port: str = "") -> None:
        try:
            save_local_settings(
                self.settings_store.config,
                self.settings_store.unmanaged_keys,
            )
        except OSError as exc:
            print(f"[Settings] local settings save failed: {exc}")
