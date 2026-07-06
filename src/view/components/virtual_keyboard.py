from PyQt6.QtWidgets import QDialog, QFrame, QHBoxLayout, QLineEdit, QPushButton, QVBoxLayout
from PyQt6.QtCore import Qt

from .keyboard_candidate_bar import KeyboardCandidateBar
from .keyboard_recent_bar import KeyboardRecentBar
from .pinyin_engine import PinyinCandidateEngine


class FullVirtualKeyboard(QDialog):
    """
    全功能虚拟键盘 (QWERTY + 数字 + 中文拼音输入)
    """
    RECENT_USERS = []  # 静态变量，记录最近输入的操作员

    def __init__(self, initial_value="", parent=None):
        super().__init__(parent)
        self.setWindowTitle("标准输入")
        self.setFixedSize(850, 480) # 缩减高度以适应内容
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.value = str(initial_value)
        self.pinyin_buffer = ""
        self.is_caps = False
        self.is_first_input = True
        self.is_chinese_mode = True 
        self.pinyin_engine = PinyinCandidateEngine()

        self._build_ui()

    def _build_ui(self):
        container = QFrame(self)
        container.setObjectName("KbContainer")
        container.setFixedSize(850, 480)
        container.setStyleSheet("""
            #KbContainer {
                background: #F0F2F5;
                border: 2px solid #597EF7;
                border-radius: 12px;
            }
            QPushButton {
                background: white;
                border: 1px solid #D9D9D9;
                border-radius: 6px;
                font-size: 18px;
                font-weight: bold;
                min-height: 50px;
                color: #333;
            }
            QPushButton:pressed {
                background: #E6F4FF;
                border-color: #1890FF;
            }
            #ActionBtn {
                background: #597EF7;
                color: white;
                border: none;
            }
            #ClearBtn {
                background: #FFF1F0;
                color: #FF4D4F;
                border: 1px solid #FFA39E;
            }
            .CandidateBtn {
                background: transparent;
                border: none;
                color: #1890FF;
                font-size: 22px;
                padding: 0 10px;
                min-height: 40px;
            }
            .CandidateBtn:hover {
                background: #E6F4FF;
                border-radius: 4px;
            }
            #PageBtn {
                background: #E8E8E8;
                color: #666;
                font-size: 20px;
                min-width: 40px;
                min-height: 40px;
                max-width: 40px;
                border: none;
                border-radius: 20px;
            }
        """)
        
        main_lay = QVBoxLayout(container)
        main_lay.setContentsMargins(20, 15, 20, 15)
        main_lay.setSpacing(8)

        # 1. 顶部显示内容
        self.display = QLineEdit(self.value)
        self.display.setReadOnly(True)
        self.display.setFixedHeight(60)
        self.display.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            color: #1890FF;
            background: white;
            border: 1px solid #D9D9D9;
            border-radius: 6px;
            padding: 0 15px;
        """)
        main_lay.addWidget(self.display)

        self.recent_bar = KeyboardRecentBar()
        self.recent_bar.nameSelected.connect(self._on_recent_clicked)
        main_lay.addWidget(self.recent_bar)

        self.candidate_bar = KeyboardCandidateBar()
        self.candidate_bar.candidateSelected.connect(self._on_candidate_selected)
        main_lay.addWidget(self.candidate_bar)

        # 3. 键盘区域
        rows_lay = QVBoxLayout()
        rows_lay.setSpacing(6)

        # 第一行: 数字
        r1 = QHBoxLayout()
        for k in "1234567890":
            r1.addWidget(self._create_btn(k))
        btn_back = self._create_btn("←", True)
        btn_back.clicked.connect(lambda: self._handle_key("←"))
        r1.addWidget(btn_back)
        rows_lay.addLayout(r1)

        # 第二行: Q-P
        r2 = QHBoxLayout()
        for k in "QWERTYUIOP":
            r2.addWidget(self._create_btn(k))
        rows_lay.addLayout(r2)

        # 第三行: A-L
        r3 = QHBoxLayout()
        r3.addSpacing(25)
        for k in "ASDFGHJKL":
            r3.addWidget(self._create_btn(k))
        r3.addSpacing(25)
        rows_lay.addLayout(r3)

        # 第四行: 大写、Z-M、清空
        r4 = QHBoxLayout()
        self.caps_btn = self._create_btn("大写", True)
        self.caps_btn.setFixedWidth(80)
        self.caps_btn.clicked.connect(self._toggle_caps)
        r4.addWidget(self.caps_btn)
        for k in "ZXCVBNM":
            r4.addWidget(self._create_btn(k))
        
        btn_clear = self._create_btn("清空", False)
        btn_clear.setObjectName("ClearBtn")
        btn_clear.setFixedWidth(80)
        btn_clear.clicked.connect(lambda: self._handle_key("C"))
        r4.addWidget(btn_clear)
        rows_lay.addLayout(r4)

        # 第五行: 切换, 空格, 取消, 确定
        r5 = QHBoxLayout()
        self.lang_btn = self._create_btn("中文", True)
        self.lang_btn.setFixedWidth(120)
        self.lang_btn.clicked.connect(self._toggle_lang)
        self.lang_btn.setStyleSheet("background: #BAE7FF;") 
        r5.addWidget(self.lang_btn)
        
        btn_space = self._create_btn("空格", True)
        btn_space.clicked.connect(lambda: self._handle_key(" "))
        r5.addWidget(btn_space, 4)

        btn_cancel = self._create_btn("取消")
        btn_cancel.clicked.connect(self.reject)
        r5.addWidget(btn_cancel, 1)

        btn_ok = self._create_btn("确认输入", False)
        btn_ok.setObjectName("ActionBtn")
        btn_ok.clicked.connect(self._commit_and_accept)
        r5.addWidget(btn_ok, 2)
        
        rows_lay.addLayout(r5)
        main_lay.addLayout(rows_lay)

    def _commit_and_accept(self):
        """确认输入前，将拼音缓冲区残留内容追加到 value"""
        if self.pinyin_buffer:
            self.value += self.pinyin_buffer
            self.pinyin_buffer = ""
        self.accept()

    def _create_btn(self, text, is_special=False):
        btn = QPushButton(text)
        if is_special:
            btn.setStyleSheet(btn.styleSheet() + " background: #F5F5F5;")
        
        if len(text) == 1 and text not in "←C":
            btn.clicked.connect(lambda: self._handle_key(text))
        return btn

    def _handle_key(self, key):
        if key == "C":
            self.value = ""
            self.pinyin_buffer = ""
        elif key == "←":
            if self.pinyin_buffer:
                self.pinyin_buffer = self.pinyin_buffer[:-1]
            else:
                self.value = self.value[:-1]
        elif key == " ":
            candidate = self.candidate_bar.current_page_first_candidate()
            if candidate:
                self._on_candidate_selected(candidate)
                return
            self.value += " "
        else:
            char = key
            if not self.is_caps and char.isalpha():
                char = char.lower()
            
            # 中文模式核心逻辑
            if self.is_chinese_mode and char.isalpha():
                if self.is_first_input:
                    self.value = "" # 输入中文前清空默认值
                self.pinyin_buffer += char
            else:
                if self.is_first_input:
                    self.value = char
                else:
                    self.value += char
        
        self.is_first_input = False
        self._update_display()

    def _update_display(self):
        self.display.setText(self.value)
        self._refresh_candidates_data() # 仅在拼音变化时重新生成数据

    def _refresh_candidates_data(self):
        self.candidate_bar.set_pinyin(self.pinyin_buffer)
        self.candidate_bar.set_candidates(self.pinyin_engine.candidates(self.pinyin_buffer))

    def _on_candidate_selected(self, cand):
        self.value += cand
        self.pinyin_buffer = ""
        self._update_display()

    def _toggle_caps(self):
        self.is_caps = not self.is_caps
        self.caps_btn.setStyleSheet("background: #BAE7FF; border-color: #69C0FF;" if self.is_caps else "background: #F5F5F5;")
        
    def _toggle_lang(self):
        self.is_chinese_mode = not self.is_chinese_mode
        self.pinyin_buffer = "" 
        self.lang_btn.setText("中文" if self.is_chinese_mode else "英文")
        self.lang_btn.setStyleSheet("background: #BAE7FF;" if self.is_chinese_mode else "background: #F5F5F5;")
        self._update_display()

    def showEvent(self, event):
        super().showEvent(event)
        self.recent_bar.set_names(self.RECENT_USERS)

    def _on_recent_clicked(self, name):
        self.value = name
        self.is_first_input = False
        self._update_display()

    def accept(self):
        # 点击确定时，记录最近使用的操作员
        val = self.display.text().strip()
        if val and val not in self.RECENT_USERS:
            self.RECENT_USERS.append(val)
            if len(self.RECENT_USERS) > 5:
                self.RECENT_USERS.pop(0)
        super().accept()

    def get_value(self):
        return self.value
