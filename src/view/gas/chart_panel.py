from __future__ import annotations

from time import monotonic

import pyqtgraph as pg
from PyQt6.QtCore import QCoreApplication, Qt
from PyQt6.QtGui import QAction, QColor
from PyQt6.QtWidgets import QFrame, QSizePolicy, QVBoxLayout

from src.common.logging_utils import debug_log
from src.view.components import NumericKeypad


_orig_translate = QCoreApplication.translate


def _chinese_translate(context, src, disambiguation=None, n=-1):
    trans_map = {
        "View All": "显示全部",
        "X axis": "X 轴",
        "Y axis": "Y 轴",
        "Mouse Mode": "鼠标模式",
        "Plot Options": "绘图选项",
        "Export...": "导出数据...",
        "Set Safety Threshold...": "设置安全阈值...",
    }
    return trans_map.get(src, _orig_translate(context, src, disambiguation, n))


QCoreApplication.translate = _chinese_translate


class GasChartPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.threshold = 85.0
        self._chart_state = "IDLE"
        self._chart_max_samples = 500
        self._chart_started_at: float | None = None
        self._chart_x: list[float] = []
        self._chart_torque_1: list[float] = []
        self._chart_torque_2: list[float] = []
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet("background: #0f1429; border-radius: 4px;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.plot = pg.PlotWidget()
        self.plot.setBackground("#0f1429")
        self.plot.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._setup_chart()
        layout.addWidget(self.plot)

    def _setup_chart(self):
        plot_item = self.plot.getPlotItem()
        plot_item.hideAxis("top")
        plot_item.hideAxis("right")

        left = plot_item.getAxis("left")
        left.setPen(QColor("#5d7bb9"))
        left.setTextPen(QColor("#9dbde3"))
        left.setLabel("力矩 (Nm)", color="#9dbde3")

        bottom = plot_item.getAxis("bottom")
        bottom.setPen(QColor("#5d7bb9"))
        bottom.setTextPen(QColor("#9dbde3"))
        bottom.setLabel("相对时间 (s)", color="#9dbde3")

        self.plot.showGrid(x=True, y=True, alpha=0.15)
        self.plot.setYRange(0, 100)
        self.plot.setXRange(0, 10)

        self.warn_line = pg.InfiniteLine(
            pos=self.threshold,
            angle=0,
            pen=pg.mkPen("#ff7676", width=2, style=Qt.PenStyle.DashLine),
        )
        self.plot.addItem(self.warn_line)

        menu = plot_item.getViewBox().menu
        menu.addSeparator()
        action = QAction("Set Safety Threshold...", self)
        action.triggered.connect(self._on_set_threshold)
        menu.addAction(action)

        self.curve_1 = self.plot.plot([], [], pen=pg.mkPen("#0958d9", width=2.5))
        self.curve_1_base = self.plot.plot([], [], pen=None)
        self.curve_1_fill = pg.FillBetweenItem(
            self.curve_1,
            self.curve_1_base,
            brush=QColor(9, 88, 217, 40),
        )
        self.plot.addItem(self.curve_1_fill)

        self.curve_2 = self.plot.plot([], [], pen=pg.mkPen("#389e0d", width=2.5))
        self.curve_2_base = self.plot.plot([], [], pen=None)
        self.curve_2_fill = pg.FillBetweenItem(
            self.curve_2,
            self.curve_2_base,
            brush=QColor(56, 158, 13, 30),
        )
        self.plot.addItem(self.curve_2_fill)

    def _on_set_threshold(self):
        keypad = NumericKeypad(str(self.threshold), self.window())
        if keypad.exec():
            try:
                self.threshold = float(keypad.get_value())
                self.warn_line.setPos(self.threshold)
            except ValueError:
                pass

    def handle_run_seq(self, run_seq: int):
        if run_seq > 10 and self._chart_state != "COLLECTING":
            self.start_collecting()

    def start_collecting(self):
        self._chart_state = "COLLECTING"
        self._chart_started_at = None
        self._chart_x.clear()
        self._chart_torque_1.clear()
        self._chart_torque_2.clear()
        self._refresh_torque_chart()
        debug_log("[GasPage] 工序采集开始")

    def freeze(self, record_id: int):
        self._chart_state = "FROZEN"
        debug_log(f"[GasPage] 工序采集冻结 (record_id={record_id})")

    def sample_torque(self, torque_1: float, torque_2: float, sample_at: float | None = None):
        if self._chart_state != "COLLECTING":
            return
        self._append_torque_sample(torque_1, torque_2, sample_at or monotonic())

    def grab_chart(self):
        return self.plot.grab()

    def _append_torque_sample(self, torque_1: float, torque_2: float, sample_at: float):
        if self._chart_started_at is None:
            self._chart_started_at = sample_at

        relative_time = max(0.0, sample_at - self._chart_started_at)
        self._chart_x.append(relative_time)
        self._chart_torque_1.append(float(torque_1))
        self._chart_torque_2.append(float(torque_2))

        if len(self._chart_x) > self._chart_max_samples:
            self._downsample()

        self._refresh_torque_chart()

    def _downsample(self):
        target = int(self._chart_max_samples * 0.75)
        n = len(self._chart_x)
        if n <= target:
            return
        indices = [0]
        step = (n - 1) / (target - 1)
        for i in range(1, target - 1):
            indices.append(int(round(i * step)))
        indices.append(n - 1)
        self._chart_x = [self._chart_x[i] for i in indices]
        self._chart_torque_1 = [self._chart_torque_1[i] for i in indices]
        self._chart_torque_2 = [self._chart_torque_2[i] for i in indices]

    def _refresh_torque_chart(self):
        x_data = list(self._chart_x)
        y1_data = list(self._chart_torque_1)
        y2_data = list(self._chart_torque_2)
        baseline = [0.0] * len(x_data)

        self.curve_1.setData(x_data, y1_data)
        self.curve_1_base.setData(x_data, baseline)
        self.curve_2.setData(x_data, y2_data)
        self.curve_2_base.setData(x_data, baseline)

        max_x = x_data[-1] if x_data else 10.0
        self.plot.setXRange(0, max(10.0, max_x * 1.05), padding=0)

        max_value = max([self.threshold, 10.0] + y1_data + y2_data)
        self.plot.setYRange(0, max(100.0, max_value * 1.1), padding=0)
