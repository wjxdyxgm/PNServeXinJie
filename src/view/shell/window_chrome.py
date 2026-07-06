from __future__ import annotations

import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QGraphicsDropShadowEffect, QWidget


def apply_dashboard_style(widget: QWidget) -> None:
    widget.setStyleSheet(
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


def create_window_shadow(parent: QWidget) -> QGraphicsDropShadowEffect | None:
    # Windows layered windows can produce invalid dirty rects when a top-level
    # translucent frameless window also has a graphics-effect shadow.
    if sys.platform.startswith("win"):
        return None

    shadow = QGraphicsDropShadowEffect(parent)
    shadow.setBlurRadius(20)
    shadow.setXOffset(0)
    shadow.setYOffset(0)
    shadow.setColor(Qt.GlobalColor.black)
    return shadow
