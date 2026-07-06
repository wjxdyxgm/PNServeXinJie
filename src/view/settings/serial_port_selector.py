from __future__ import annotations

from PyQt6.QtWidgets import QComboBox

from src.common.serial_ports import list_serial_ports


class SerialPortSelector(QComboBox):
    """串口选择下拉框。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(160)
        self.setEditable(False)
        self.setStyleSheet(
            """
            QComboBox {
                border: 1px solid #d9d9d9;
                border-radius: 4px;
                padding: 4px 8px;
                background: white;
                font-size: 14px;
                color: #1890ff;
                font-weight: bold;
            }
            QComboBox:hover {
                border-color: #40a9ff;
            }
            QComboBox::drop-down {
                border: none;
                width: 24px;
            }
            """
        )

    def refresh_ports(self, preferred_port: str = ""):
        current_port = self.currentText()
        preferred_port = str(preferred_port or current_port or "")

        ports = list_serial_ports()
        if preferred_port and preferred_port not in ports:
            ports.append(preferred_port)
        ports = sorted(set(ports))

        combo_items = [self.itemText(index) for index in range(self.count())]
        if combo_items == ports:
            self.set_selection(preferred_port or current_port)
            return

        self.blockSignals(True)
        self.clear()
        self.addItems(ports)
        self.blockSignals(False)
        self.set_selection(preferred_port or current_port)

    def set_selection(self, port: str):
        port = str(port or "")
        if port and self.findText(port) < 0:
            self.blockSignals(True)
            self.addItem(port)
            self.model().sort(0)
            self.blockSignals(False)

        self.blockSignals(True)
        if not port:
            self.setCurrentIndex(-1)
        else:
            self.setCurrentIndex(self.findText(port))
        self.blockSignals(False)
