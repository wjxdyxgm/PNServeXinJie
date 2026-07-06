from __future__ import annotations

from PyQt6.QtWidgets import QStackedWidget

from src.view.gas_page import GasPage
from src.view.manual_page import ManualPage
from src.view.settings_page import SettingsPage


class DashboardPageStack(QStackedWidget):
    """主界面页面栈，统一管理页面顺序和页面模式名。"""

    MANUAL_INDEX = 0
    GAS_INDEX = 1
    SETTINGS_INDEX = 2
    PLC_MODE_BY_INDEX = {
        MANUAL_INDEX: "manual",
        GAS_INDEX: "gas",
    }

    def __init__(self, manual_store, gas_store, settings_store, parent=None):
        super().__init__(parent)
        self.addWidget(ManualPage(store=manual_store))
        self.addWidget(GasPage(store=gas_store, manual_store=manual_store))
        self.addWidget(SettingsPage(store=settings_store))
        self.setCurrentIndex(self.GAS_INDEX)

    def is_gas_page_active(self) -> bool:
        return self.currentIndex() == self.GAS_INDEX

    def current_plc_mode_name(self) -> str | None:
        return self.PLC_MODE_BY_INDEX.get(self.currentIndex())
