from __future__ import annotations

from PyQt6.QtCore import QRect, Qt
from PyQt6.QtGui import QColor, QFont, QPainter, QPen
from PyQt6.QtWidgets import QWidget


class GroupHeaderWidget(QWidget):
    def __init__(self, table, groups, parent=None):
        super().__init__(parent)
        self.table = table
        self.groups = groups
        self.setFixedHeight(56)
        self.setMouseTracking(True)
        self.setStyleSheet("background: white;")

        self.table.horizontalHeader().sectionResized.connect(self.update)
        self.table.horizontalScrollBar().valueChanged.connect(self.update)

    def _offset_x(self):
        viewport = self.table.viewport()
        return viewport.mapToGlobal(viewport.rect().topLeft()).x() - self.mapToGlobal(
            self.rect().topLeft()
        ).x()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        header = self.table.horizontalHeader()
        offset_x = self._offset_x()

        painter.setPen(QPen(QColor("#F0F0F0"), 1))
        painter.setBrush(QColor("white"))
        painter.drawRect(self.rect())

        font_main = QFont("Microsoft YaHei", 9)
        font_main.setBold(True)
        font_sub = QFont("Microsoft YaHei", 8)

        current_col = 0
        for group in self.groups:
            label = group["label"]
            span = group["span"]
            subs = group.get("subs", [])

            x_pos = header.sectionViewportPosition(current_col) + offset_x
            width = sum(header.sectionSize(current_col + i) for i in range(span))
            rect = QRect(x_pos, 0, width, self.height())

            if rect.right() > 0 and rect.left() < self.width():
                if not subs:
                    painter.setFont(font_main)
                    painter.setPen(QColor("#333"))
                    painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, label)
                else:
                    top_rect = QRect(x_pos, 0, width, self.height() // 2)
                    painter.setFont(font_main)
                    painter.setPen(QColor("#666"))
                    painter.drawText(top_rect, Qt.AlignmentFlag.AlignCenter, label)

                    sub_x = x_pos
                    painter.setFont(font_sub)
                    painter.setPen(QColor("#999"))
                    for index, sub_label in enumerate(subs):
                        sub_w = header.sectionSize(current_col + index)
                        sub_rect = QRect(sub_x, self.height() // 2, sub_w, self.height() // 2)
                        painter.drawText(sub_rect, Qt.AlignmentFlag.AlignCenter, sub_label)
                        if index < len(subs) - 1:
                            painter.setPen(QColor("#F5F5F5"))
                            painter.drawLine(
                                sub_x + sub_w,
                                self.height() // 2 + 6,
                                sub_x + sub_w,
                                self.height() - 6,
                            )
                            painter.setPen(QColor("#999"))
                        sub_x += sub_w

                    painter.setPen(QColor("#F0F0F0"))
                    painter.drawLine(
                        x_pos + 4,
                        self.height() // 2,
                        x_pos + width - 4,
                        self.height() // 2,
                    )

                painter.setPen(QPen(QColor("#F0F0F0"), 1))
                if current_col + span < self.table.columnCount():
                    painter.drawLine(rect.right(), 10, rect.right(), self.height() - 10)

            current_col += span

        painter.setPen(QPen(QColor("#E8E8E8"), 1))
        painter.drawLine(0, self.height() - 1, self.width(), self.height() - 1)
