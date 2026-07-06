from PyQt6.QtWidgets import QDialog, QFrame, QHBoxLayout, QLineEdit, QPushButton, QVBoxLayout
from PyQt6.QtCore import Qt

from .numeric_input_state import NumericInputState
from .numeric_key_grid import NumericKeyGrid


class NumericKeypad(QDialog):
    """
    工业级数字键盘对话框
    """
    def __init__(self, initial_value="", parent=None):
        super().__init__(parent)
        self.setWindowTitle("数字输入")
        self.setFixedSize(320, 550) # 同步高度
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.input_state = NumericInputState(initial_value)
        self._build_ui()

    def _build_ui(self):
        container = QFrame(self)
        container.setObjectName("KeypadContainer")
        container.setFixedSize(320, 550) # 维持高度，确保空间充足
        container.setStyleSheet("""
            #KeypadContainer {
                background: white;
                border: 2px solid #597EF7;
                border-radius: 12px;
            }
            QPushButton {
                background: #F8F9FA;
                border: 1px solid #D9D9D9;
                border-radius: 8px;
                font-size: 22px;
                font-weight: bold;
                color: #262626;
                padding: 0;
                margin: 0;
            }
            QPushButton:pressed {
                background: #E6F4FF;
                border-color: #1890FF;
            }
            #FuncBtn {
                background: #597EF7;
                color: white;
                border: none;
            }
            #FuncBtn:pressed {
                background: #40A9FF;
            }
            #ClearBtn {
                background: #FFF1F0;
                color: #FF4D4F;
                border: 1px solid #FFA39E;
            }
            #ClearBtn:pressed {
                background: #FFCCC7;
            }
        """)
        
        main_lay = QVBoxLayout(container)
        main_lay.setContentsMargins(20, 20, 20, 20)
        main_lay.setSpacing(15)

        # 显示区域
        self.display = QLineEdit(self.input_state.value)
        self.display.setReadOnly(True)
        self.display.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.display.setFixedHeight(65)
        self.display.setStyleSheet("""
            font-size: 36px;
            font-weight: bold;
            color: #1890FF;
            background: #FAFAFA;
            border: 1px solid #D9D9D9;
            border-radius: 6px;
            padding: 0 15px;
        """)
        main_lay.addWidget(self.display)

        key_grid = NumericKeyGrid()
        key_grid.keyClicked.connect(self._on_key_clicked)
        main_lay.addWidget(key_grid)

        # 底部操作
        action_lay = QVBoxLayout()
        action_lay.setSpacing(10)
        
        clear_btn = QPushButton("全部清空")
        clear_btn.setObjectName("ClearBtn")
        clear_btn.setFixedHeight(45)
        clear_btn.setStyleSheet("font-size: 16px;")
        clear_btn.clicked.connect(lambda: self._on_key_clicked('C'))

        ctrl_lay = QHBoxLayout()
        ctrl_lay.setSpacing(10)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.setFixedHeight(50)
        cancel_btn.clicked.connect(self.reject)
        
        ok_btn = QPushButton("确认输入")
        ok_btn.setObjectName("FuncBtn")
        ok_btn.setFixedHeight(50)
        ok_btn.clicked.connect(self.accept)
        
        ctrl_lay.addWidget(cancel_btn, 1)
        ctrl_lay.addWidget(ok_btn, 1)

        action_lay.addWidget(clear_btn)
        action_lay.addLayout(ctrl_lay)
        
        main_lay.addLayout(action_lay)

    def _on_key_clicked(self, key):
        self.display.setText(self.input_state.press(key))

    def get_value(self):
        return self.input_state.value
