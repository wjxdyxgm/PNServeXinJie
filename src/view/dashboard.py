"""
Main dashboard view.
"""
from PyQt6.QtCore import QDateTime, QPoint, QTimer, Qt
from PyQt6.QtWidgets import QApplication
from PyQt6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

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
from src.view.components import CapsuleToggle, ClickableLineEdit, FullVirtualKeyboard, StatusLamp
from src.view.gas_page import GasPage
from src.view.manual_page import ManualPage
from src.view.settings_page import SettingsPage


class DashboardView(QWidget):
    PRIMARY = "#597EF7"
    HEADER_BG = "#597EF7"

    def __init__(self):
        super().__init__()
        self.setWindowTitle("伺服控制台")
        self.resize(1024, 720)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._drag_pos = QPoint()
        self._is_dragging = False

        self.manual_store = ManualStore(self)
        self.auth_store = AuthStore(self)
        self.gas_db = GasRecordDB()
        self.gas_store = GasStore(db=self.gas_db, parent=self)
        self.settings_store = SettingsStore(self)
        self.scanner_service = ScannerService(self._should_capture_scanner_input, self)
        self._load_local_settings()

        self._apply_global_style()
        self._build_ui()
        self._add_shadow()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_system_time)
        self.timer.start(1000)
        self._update_system_time()

        self.auth_store.dataChanged.connect(self._update_header_from_auth)
        self.manual_store.dataChanged.connect(self._update_footer_torque)
        self.settings_store.serialPortChanged.connect(self._save_local_settings)
        self._update_header_from_auth()
        self._update_footer_torque()
        self._init_plc()
        self._init_scanner()

    def _add_shadow(self):
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(0)
        shadow.setColor(Qt.GlobalColor.black)

    def _apply_global_style(self):
        self.setStyleSheet(
            """
            QWidget {
                font-family: 'Microsoft YaHei', sans-serif;
                color: #333;
                font-size: 13px;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 8px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #e0e0e0;
                min-height: 25px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: #c0c0c0;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
            QScrollBar:horizontal {
                background: transparent;
                height: 8px;
                margin: 0px;
            }
            QScrollBar::handle:horizontal {
                background: #e0e0e0;
                min-width: 25px;
                border-radius: 4px;
            }
            QScrollBar::handle:horizontal:hover {
                background: #c0c0c0;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                background: none;
            }
            """
        )

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_header())

        self.pages = QStackedWidget()
        self.pages.addWidget(ManualPage(store=self.manual_store))
        self.pages.addWidget(GasPage(store=self.gas_store, manual_store=self.manual_store))
        self.pages.addWidget(SettingsPage(store=self.settings_store))
        self.pages.setCurrentIndex(1)
        root.addWidget(self.pages, 1)

        root.addWidget(self._build_footer())

    def _build_header(self):
        header = QFrame()
        header.setFixedHeight(60)
        header.setStyleSheet(f"background-color: {self.HEADER_BG};")
        layout = QHBoxLayout(header)
        layout.setContentsMargins(10, 0, 0, 0)
        layout.setSpacing(0)

        logo = QLabel("精驰")
        logo.setStyleSheet(
            """
            color: white; font-size: 20pt; font-weight: 900;
            font-family: 'YouSheBiaoTiHei', 'Microsoft YaHei';
            background: transparent;
            padding: 0 5px;
            """
        )
        layout.addWidget(logo)

        layout.addSpacing(25)
        self.capsule = CapsuleToggle([("手动", "manual"), ("自动", "gas"), ("设置", "settings")])
        self.capsule.tabChanged.connect(self._on_tab_changed)
        layout.addWidget(self.capsule)
        layout.addStretch()

        self.system_time_label = QLabel()
        self.system_time_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.system_time_label.setStyleSheet(
            """
            color: white; font-size: 14px; font-weight: bold;
            font-family: 'YouSheBiaoTiHei', sans-serif;
            margin-right: 15px;
            """
        )
        layout.addWidget(self.system_time_label)

        self.labels = {}
        for title, value in [("上班", "00:00"), ("操作数", "0")]:
            column = QVBoxLayout()
            column.setContentsMargins(0, 5, 0, 5)
            column.setSpacing(0)

            title_label = QLabel(title)
            title_label.setStyleSheet(
                "color: rgba(255, 255, 255, 0.7); font-size: 13px; font-family: 'YouSheBiaoTiHei';"
            )
            title_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

            value_label = QLabel(value)
            value_label.setStyleSheet(
                """
                color: white; font-size: 24px; font-weight: bold;
                font-family: 'YouSheBiaoTiHei';
                """
            )
            value_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.labels[title] = value_label

            column.addWidget(title_label)
            column.addWidget(value_label)

            wrapper = QWidget()
            wrapper.setFixedWidth(100)
            wrapper.setLayout(column)
            layout.addWidget(wrapper)

        layout.addSpacing(15)  # 增加与操作数标签之间的间距

        right_controls = QWidget()
        right_layout = QVBoxLayout(right_controls)
        right_layout.setContentsMargins(0, 0, 0, 0)  # 置顶、靠右
        right_layout.setSpacing(0)

        win_layout = QHBoxLayout()
        win_layout.setSpacing(0)
        # 使用 Windows 10/11 原生控制图标
        self.min_btn = self._create_win_btn("\uE921", self.showMinimized)
        self.max_btn = self._create_win_btn("\uE922", self._toggle_maximize)
        self.close_btn = self._create_win_btn("\uE8BB", self.close, is_close=True)
        
        win_layout.addWidget(self.min_btn)
        win_layout.addWidget(self.max_btn)
        win_layout.addWidget(self.close_btn)
        
        right_layout.addLayout(win_layout)
        right_layout.addStretch()  # 加上垂直弹簧，将窗口按钮顶到最上方
        
        layout.addWidget(right_controls)

        return header

    def _build_footer(self):
        footer = QFrame()
        footer.setFixedHeight(36)
        footer.setStyleSheet(
            """
            QFrame {
                background-color: #F5F5F7;
                border-top: 1px solid #E0E0E0;
            }
            """
        )
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(0)

        operator_label = QLabel("操作员")
        operator_label.setStyleSheet("color: #666; font-size: 13px; border: none; background: transparent;")
        layout.addWidget(operator_label)
        layout.addSpacing(5)

        self.op_input = ClickableLineEdit(self.auth_store.current_user, keyboard_type="full")
        self.op_input.setPlaceholderText("输入操作员")
        self.op_input.setFixedWidth(100)
        self.op_input.setStyleSheet(
            """
            background: transparent; border: none;
            color: #1890FF;
            font-size: 14px; font-weight: bold;
            font-family: 'FangSong', 'STFangsong';
            """
        )
        self.op_input.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.op_input.valueChanged.connect(self._on_operator_change)
        layout.addWidget(self.op_input)

        layout.addSpacing(15)
        self.logout_btn = QPushButton("注销登录")
        self.logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.logout_btn.setStyleSheet(
            """
            QPushButton {
                background: transparent; color: #999;
                border: none; font-size: 12px; text-decoration: underline;
            }
            QPushButton:hover { color: #597EF7; }
            """
        )
        self.logout_btn.clicked.connect(self.auth_store.logout)
        layout.addWidget(self.logout_btn)

        layout.addStretch()

        torque_panel = QWidget()
        torque_layout = QHBoxLayout(torque_panel)
        torque_layout.setContentsMargins(0, 0, 0, 0)
        torque_layout.setSpacing(18)

        group = QWidget()
        group_layout = QHBoxLayout(group)
        group_layout.setContentsMargins(0, 0, 0, 0)
        group_layout.setSpacing(8)

        title_label = QLabel("压力1/2/3/4:")
        title_label.setStyleSheet(
            "color: #7a7a7a; font-size: 12px; border: none; background: transparent;"
        )

        self.torque_value_label = QLabel("0.00/0.00/0.00/0.00")
        self.torque_value_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.torque_value_label.setStyleSheet(
            """
            color: #2f54eb;
            font-size: 14px;
            font-weight: bold;
            font-family: 'Consolas', 'Microsoft YaHei';
            border: none;
            background: transparent;
            """
        )

        unit_label = QLabel("KG")
        unit_label.setStyleSheet(
            "color: #9a9a9a; font-size: 11px; border: none; background: transparent;"
        )

        group_layout.addWidget(title_label)
        group_layout.addWidget(self.torque_value_label)
        group_layout.addWidget(unit_label)
        torque_layout.addWidget(group)

        layout.addWidget(torque_panel)

        layout.addSpacing(10)

        pos_fb_panel = QWidget()
        pos_fb_layout = QHBoxLayout(pos_fb_panel)
        pos_fb_layout.setContentsMargins(0, 0, 0, 0)
        pos_fb_layout.setSpacing(10)

        group = QWidget()
        group_layout = QHBoxLayout(group)
        group_layout.setContentsMargins(0, 0, 0, 0)
        group_layout.setSpacing(8)

        title_label = QLabel("伺服1/2/3/4:")
        title_label.setStyleSheet(
            "color: #7a7a7a; font-size: 12px; border: none; background: transparent;"
        )

        self.servo_value_label = QLabel("0.000/0.000/0.000/0.000")
        self.servo_value_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.servo_value_label.setStyleSheet(
            """
            color: #1890ff;
            font-size: 14px;
            font-weight: bold;
            font-family: 'Consolas', 'Microsoft YaHei';
            border: none;
            background: transparent;
            """
        )

        unit_label = QLabel("mm")
        unit_label.setStyleSheet(
            "color: #9a9a9a; font-size: 11px; border: none; background: transparent;"
        )

        group_layout.addWidget(title_label)
        group_layout.addWidget(self.servo_value_label)
        group_layout.addWidget(unit_label)
        pos_fb_layout.addWidget(group)

        layout.addWidget(pos_fb_panel)
        layout.addStretch()

        self.plc_status_lamp = StatusLamp(size=10)
        self.plc_status_lamp.set_error(True)
        plc_label = QLabel("PLC")
        plc_label.setStyleSheet("color: #666; font-size: 12px; border: none; background: transparent;")
        layout.addWidget(self.plc_status_lamp)
        layout.addSpacing(4)
        layout.addWidget(plc_label)
        return footer

    def _create_win_btn(self, text, slot, is_close=False):
        button = QPushButton(text)
        button.setFixedSize(46, 32)
        hover_color = "#e81123" if is_close else "rgba(255, 255, 255, 0.2)"
        button.setStyleSheet(
            f"""
            QPushButton {{
                background: transparent; color: white; border: none; font-size: 10pt;
                font-family: 'Segoe Fluent Icons', 'Segoe MDL2 Assets', sans-serif;
            }}
            QPushButton:hover {{
                background: {hover_color};
            }}
            """
        )
        button.clicked.connect(slot)
        return button

    def _toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
            self.max_btn.setText("\uE922")
        else:
            self.showMaximized()
            self.max_btn.setText("\uE923")

    def _init_plc(self):
        plc_ip = get_plc_ip()
        self.plc_driver = Snap7Driver()
        self.plc_bridge = PLCBridge(self.plc_driver, plc_ip, parent=self)
        self.plc_bridge.register_store("manual", self.manual_store)
        self.plc_bridge.register_store("gas", self.gas_store)
        self.plc_bridge.register_store("settings", self.settings_store)
        self.plc_bridge.connectionChanged.connect(self._on_plc_connection_changed)
        self.plc_bridge.errorOccurred.connect(lambda msg: print(f"[PLC Error] {msg}"))
        self.plc_bridge.start()

    def _init_scanner(self):
        self.scanner_service.barcodeReceived.connect(self._on_barcode_received)
        self.scanner_service.start(QApplication.instance())

    def _on_plc_connection_changed(self, connected: bool):
        if connected:
            self.plc_status_lamp.set_active(True)
            self._sync_plc_mode_to_current_page()
        else:
            self.plc_status_lamp.set_error(True)

    def _update_footer_torque(self):
        if hasattr(self, "torque_value_label"):
            t1 = self.manual_store.torque_data.get("torque_1", 0.0)
            t2 = self.manual_store.torque_data.get("torque_2", 0.0)
            t3 = self.manual_store.torque_data.get("torque_3", 0.0)
            t4 = self.manual_store.torque_data.get("torque_4", 0.0)
            self.torque_value_label.setText(f"{float(t1):.2f}/{float(t2):.2f}/{float(t3):.2f}/{float(t4):.2f}")

        if hasattr(self, "servo_value_label"):
            s1 = self.manual_store.servo_data.get(1, {}).get("current_pos", 0)
            s2 = self.manual_store.servo_data.get(2, {}).get("current_pos", 0)
            s3 = self.manual_store.servo_data.get(3, {}).get("current_pos", 0)
            s4 = self.manual_store.servo_data.get(4, {}).get("current_pos", 0)
            self.servo_value_label.setText(f"{float(s1)/1000:.3f}/{float(s2)/1000:.3f}/{float(s3)/1000:.3f}/{float(s4)/1000:.3f}")

    def _load_local_settings(self):
        payload = load_local_settings()
        serial_port = payload.get("serial_port")
        if isinstance(serial_port, str):
            self.settings_store.set_serial_port(serial_port)

    def _save_local_settings(self, _port: str = ""):
        try:
            save_local_settings(
                self.settings_store.config,
                self.settings_store.unmanaged_keys,
            )
        except OSError as exc:
            print(f"[Settings] local settings save failed: {exc}")

    def closeEvent(self, event):
        if hasattr(self, "scanner_service"):
            self.scanner_service.stop()
        if hasattr(self, "plc_bridge"):
            self.plc_bridge.stop()
        if hasattr(self, "gas_db"):
            self.gas_db.close()
        super().closeEvent(event)

    def _on_operator_change(self, username):
        if not username:
            return
        self.auth_store.login(username, "admin", ["manual", "gas", "settings"])
        self.auth_store.clock_in()
        # 将操作员名称写入 PLC (VW262-VW280, 20 字节 GBK)
        if hasattr(self, "plc_bridge"):
            self.plc_bridge.write("gas.operator_raw", username)
        # 同步到 gas_store，确保记录入库时使用正确的操作员名
        if hasattr(self, "gas_store"):
            self.gas_store.update_current_data(operator=username)

    def _on_barcode_received(self, barcode: str):
        if not barcode:
            return
        print(f"[Scanner] barcode received: {barcode}")
        if not hasattr(self, "plc_bridge"):
            return
        if not self.plc_bridge.write("gas.product_code_raw", barcode):
            print(f"[Scanner] barcode write to PLC failed: {barcode}")
            return
        if hasattr(self, "gas_store"):
            self.gas_store.apply_plc_value("gas.product_code_raw", barcode)
            self.gas_store.signal_code_present()

    def _should_capture_scanner_input(self) -> bool:
        return (
            getattr(self, "pages", None) is not None
            and isinstance(self.pages.currentWidget(), GasPage)
        )

    def _update_header_from_auth(self):
        from datetime import datetime

        if self.auth_store.clock_in_time > 0:
            dt = datetime.fromtimestamp(self.auth_store.clock_in_time)
            self.labels["上班"].setText(dt.strftime("%H:%M"))
        else:
            self.labels["上班"].setText("--:--")

        self.labels["操作数"].setText(str(self.auth_store.operation_count))

        if self.op_input.text() != self.auth_store.current_user:
            self.op_input.setText(self.auth_store.current_user)

        if not self.auth_store.current_user:
            QTimer.singleShot(100, self._show_operator_login_dialog)

    def _show_operator_login_dialog(self):
        dialog = FullVirtualKeyboard("", self)
        dialog.setWindowTitle("请输入操作员")
        while True:
            result = dialog.exec()
            name = dialog.get_value().strip()
            if result and name:
                self._on_operator_change(name)
                break
            dialog = FullVirtualKeyboard("", self)

    def _update_system_time(self):
        now = QDateTime.currentDateTime()
        self.system_time_label.setText(f"{now.toString('yyyy-MM-dd')}\n{now.toString('HH:mm:ss')}")

    def _on_tab_changed(self, index):
        self.pages.setCurrentIndex(index)
        self._sync_plc_mode_to_current_page()

    def _sync_plc_mode_to_current_page(self):
        if not hasattr(self, "manual_store") or not hasattr(self, "pages"):
            return

        page_name = {
            0: "manual",
            1: "gas",
        }.get(self.pages.currentIndex())
        if page_name:
            self.manual_store.set_page_mode(page_name)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and event.position().y() < 60:
            self._is_dragging = True
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._is_dragging and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._is_dragging = False
