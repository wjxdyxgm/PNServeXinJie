from __future__ import annotations


class NumericInputState:
    """数字键盘输入状态。"""

    def __init__(self, initial_value=""):
        self.value = str(initial_value)
        self.is_first_input = True

    def press(self, key: str) -> str:
        if key == "C":
            self.value = ""
            self.is_first_input = False
        elif key == "←":
            self.value = self.value[:-1]
            self.is_first_input = False
        elif key == ".":
            if self.is_first_input:
                self.value = "0."
            elif "." not in self.value:
                self.value += "."
            self.is_first_input = False
        else:
            if self.is_first_input:
                self.value = key
            else:
                self.value += key
            self.is_first_input = False

        return self.value
