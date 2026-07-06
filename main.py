"""
Servo - 项目入口
启动 PyQt6 Dashboard 应用
"""
import sys
from PyQt6.QtWidgets import QApplication
from src.app import AppContext
from src.plc.binding_validation import print_binding_validation_report
from src.view.dashboard import DashboardView


def main():
    app = QApplication(sys.argv)
    print_binding_validation_report()
    context = AppContext()
    window = DashboardView(context)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
