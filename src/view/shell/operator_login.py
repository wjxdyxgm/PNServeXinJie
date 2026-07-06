from __future__ import annotations

from src.view.components import FullVirtualKeyboard


def request_operator_name(parent=None) -> str:
    """循环弹出操作员输入框，直到输入有效姓名。"""

    while True:
        dialog = FullVirtualKeyboard("", parent)
        dialog.setWindowTitle("请输入操作员")
        result = dialog.exec()
        name = dialog.get_value().strip()
        if result and name:
            return name
