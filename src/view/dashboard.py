"""
Main dashboard view.
"""
from PyQt6.QtCore import QDateTime, QPoint, QTimer, Qt
from PyQt6.QtWidgets import QApplication
from PyQt6.QtWidgets import (
    QVBoxLayout,
    QWidget,
)

from src.app import AppContext
from src.common.logging_utils import debug_log
from src.view.shell import (
    DashboardPageStack,
    FooterBar,
    HeaderBar,
    apply_dashboard_style,
    build_footer_feedback,
    create_window_shadow,
    request_operator_name,
)


class DashboardView(QWidget):
    def __init__(self, context: AppContext | None = None):
        super().__init__()
        self.setWindowTitle("伺服控制台")
        self.resize(1024, 720)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._drag_pos = QPoint()
        self._is_dragging = False

        self.context = context or AppContext(self)
        self.manual_store = self.context.manual_store
        self.auth_store = self.context.auth_store
        self.gas_db = self.context.gas_db
        self.gas_store = self.context.gas_store
        self.settings_store = self.context.settings_store
        self.plc_bridge = None
        self.scanner_service = None

        apply_dashboard_style(self)
        self._build_ui()
        self._add_shadow()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_system_time)
        self.timer.start(1000)
        self._update_system_time()

        self.auth_store.dataChanged.connect(self._update_header_from_auth)
        self.manual_store.dataChanged.connect(self._update_footer_torque)
        self._update_header_from_auth()
        self._update_footer_torque()
        self._init_plc()
        self._init_scanner()

    def _add_shadow(self):
        shadow = create_window_shadow(self)
        if shadow is not None:
            self.setGraphicsEffect(shadow)

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.header_bar = HeaderBar()
        self.header_bar.tabChanged.connect(self._on_tab_changed)
        self.header_bar.minimizeRequested.connect(self.showMinimized)
        self.header_bar.maximizeRequested.connect(self._toggle_maximize)
        self.header_bar.closeRequested.connect(self.close)
        root.addWidget(self.header_bar)

        self.pages = DashboardPageStack(
            self.manual_store,
            self.gas_store,
            self.settings_store,
        )
        root.addWidget(self.pages, 1)

        self.footer_bar = FooterBar(self.auth_store.current_user)
        self.footer_bar.operatorChanged.connect(self._on_operator_change)
        self.footer_bar.logoutRequested.connect(self.auth_store.logout)
        root.addWidget(self.footer_bar)

    def _toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
            self.header_bar.set_maximized_icon(False)
        else:
            self.showMaximized()
            self.header_bar.set_maximized_icon(True)

    def _init_plc(self):
        self.plc_bridge = self.context.create_plc_bridge()
        self.plc_bridge.connectionChanged.connect(self._on_plc_connection_changed)
        self.plc_bridge.errorOccurred.connect(lambda msg: print(f"[PLC Error] {msg}"))
        self.context.start_plc()

    def _init_scanner(self):
        self.scanner_service = self.context.create_scanner(self._should_capture_scanner_input)
        self.scanner_service.barcodeReceived.connect(self._on_barcode_received)
        self.context.start_scanner(QApplication.instance())

    def _on_plc_connection_changed(self, connected: bool):
        self.footer_bar.set_plc_connected(connected)
        if connected:
            self._sync_plc_mode_to_current_page()

    def _update_footer_torque(self):
        torque_values, servo_values = build_footer_feedback(self.manual_store)
        self.footer_bar.set_feedback_values(torque_values, servo_values)

    def closeEvent(self, event):
        self.context.shutdown()
        super().closeEvent(event)

    def _on_operator_change(self, username):
        self.context.set_operator(username)

    def _on_barcode_received(self, barcode: str):
        if not barcode:
            return
        debug_log(f"[Scanner] barcode received: {barcode}")
        if not self.context.apply_barcode(barcode):
            print(f"[Scanner] barcode write to PLC failed: {barcode}")

    def _should_capture_scanner_input(self) -> bool:
        return (
            getattr(self, "pages", None) is not None
            and self.pages.is_gas_page_active()
        )

    def _update_header_from_auth(self):
        self.header_bar.set_auth_summary(
            self.auth_store.clock_in_time,
            self.auth_store.operation_count,
        )
        self.footer_bar.set_operator(self.auth_store.current_user)

        if not self.auth_store.current_user:
            QTimer.singleShot(100, self._show_operator_login_dialog)

    def _show_operator_login_dialog(self):
        self._on_operator_change(request_operator_name(self))

    def _update_system_time(self):
        now = QDateTime.currentDateTime()
        self.header_bar.set_system_time(
            now.toString("yyyy-MM-dd"),
            now.toString("HH:mm:ss"),
        )

    def _on_tab_changed(self, index):
        self.pages.setCurrentIndex(index)
        self._sync_plc_mode_to_current_page()

    def _sync_plc_mode_to_current_page(self):
        if not hasattr(self, "manual_store") or not hasattr(self, "pages"):
            return

        page_name = self.pages.current_plc_mode_name()
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
