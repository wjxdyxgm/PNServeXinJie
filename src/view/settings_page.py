from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from src.common.logging_utils import debug_log
from src.store.settings_store import SettingsStore
from src.view.settings import BasicSettingsPanel, LIMIT_FIELD_LABELS, LimitsSettingsPanel


class SettingsPage(QFrame):
    """系统设置页面"""

    SERIAL_PORT_REFRESH_MS = 2000

    def __init__(self, store: SettingsStore = None, parent=None):
        super().__init__(parent)
        self.store = store
        self.setStyleSheet("background: #f0f2f5;")
        self._build_ui()
        self._connect_signals()
        self._refresh_serial_ports()
        self._update_ui_from_store()

        self._serial_port_timer = QTimer(self)
        self._serial_port_timer.timeout.connect(self._refresh_serial_ports)
        self._serial_port_timer.start(self.SERIAL_PORT_REFRESH_MS)

    # ------------------------------------------------------------------
    #  UI 构建
    # ------------------------------------------------------------------

    def _build_ui(self):
        root_lay = QVBoxLayout(self)
        root_lay.setContentsMargins(0, 0, 0, 0)
        root_lay.setSpacing(0)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        content = QWidget()
        scroll_area.setWidget(content)
        root_lay.addWidget(scroll_area)

        main_lay = QVBoxLayout(content)
        main_lay.setContentsMargins(40, 40, 40, 40)
        main_lay.setSpacing(30)

        header_lay = QHBoxLayout()
        title = QLabel("系统参数设置")
        title.setStyleSheet(
            """
            font-size: 24px; font-weight: bold;
            font-family: 'YouSheBiaoTiHei';
            color: #1890ff;
            """
        )
        header_lay.addWidget(title)
        header_lay.addStretch()
        main_lay.addLayout(header_lay)

        self.basic_panel = BasicSettingsPanel()
        main_lay.addWidget(self.basic_panel)

        self.limits_panel = LimitsSettingsPanel()
        main_lay.addWidget(self.limits_panel)

        main_lay.addStretch()

    # ------------------------------------------------------------------
    #  信号连接
    # ------------------------------------------------------------------

    def _connect_signals(self):
        if not self.store:
            return

        self.basic_panel.standbyTimeChanged.connect(
            lambda value: self.store.set_standby_time(value, write=True)
        )
        self.basic_panel.featureToggled.connect(self.store.set_feature_enabled)
        self.basic_panel.runModeSelected.connect(
            lambda mode: self.store.set_run_mode(mode, write=True)
        )
        self.basic_panel.serialPortChanged.connect(self.store.set_serial_port)
        self.limits_panel.limitValueChanged.connect(self._on_limit_value_changed)
        self.store.dataChanged.connect(self._update_ui_from_store)

    # ------------------------------------------------------------------
    #  UI 刷新
    # ------------------------------------------------------------------

    def _update_ui_from_store(self):
        if not self.store:
            return

        config = self.store.config
        self.basic_panel.set_config(config)
        self.limits_panel.set_config(config)

    def _refresh_serial_ports(self):
        preferred_port = self.store.config.get("serial_port", "") if self.store else ""
        self.basic_panel.refresh_serial_ports(preferred_port)

    # ------------------------------------------------------------------
    #  内部工具
    # ------------------------------------------------------------------

    def _on_limit_value_changed(self, key: str, raw_value: str):
        value = float(raw_value or 0)
        debug_log(f"[SettingsPage] 用户修改: {key}={value}")
        if self.store.set_limit_value(key, value, write=True):
            return

        self._update_ui_from_store()
        pair = self.store.get_limit_pair(key)
        if pair is None:
            return

        low_key, high_key = pair
        QMessageBox.warning(
            self,
            "参数范围无效",
            f"{LIMIT_FIELD_LABELS[low_key]} 不能大于 {LIMIT_FIELD_LABELS[high_key]}。",
        )
