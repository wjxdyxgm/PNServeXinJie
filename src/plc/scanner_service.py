"""
Keyboard-wedge barcode scanner service.
"""
from __future__ import annotations

from time import monotonic
from typing import Callable

from PyQt6.QtCore import QEvent, QObject, Qt, pyqtSignal
from PyQt6.QtWidgets import QApplication, QLineEdit, QWidget


class ScannerService(QObject):
    """Capture fast keyboard input sequences and emit barcodes."""

    barcodeReceived = pyqtSignal(str)
    errorOccurred = pyqtSignal(str)

    MAX_INTER_KEY_SECONDS = 0.15

    def __init__(self, should_capture: Callable[[], bool] | None = None, parent=None):
        super().__init__(parent)
        self._should_capture = should_capture or (lambda: True)
        self._application: QApplication | None = None
        self._buffer = ""
        self._last_key_at: float | None = None
        self._scanner_active = False
        self._editable_target: QLineEdit | None = None

    def start(self, application: QApplication | None = None):
        application = application or QApplication.instance()
        if application is None:
            self.errorOccurred.emit("scanner service start failed: QApplication is not available")
            return

        if self._application is application:
            return

        if self._application is not None:
            self._application.removeEventFilter(self)

        self._application = application
        self._application.installEventFilter(self)

    def stop(self):
        if self._application is not None:
            self._application.removeEventFilter(self)
            self._application = None
        self._reset_capture()

    _MODIFIER_KEYS = frozenset({
        Qt.Key.Key_Shift, Qt.Key.Key_Control,
        Qt.Key.Key_Alt, Qt.Key.Key_Meta,
        Qt.Key.Key_CapsLock, Qt.Key.Key_NumLock,
    })

    def eventFilter(self, watched, event):
        if event.type() != QEvent.Type.KeyPress:
            return False

        if not self._should_capture():
            self._reset_capture()
            return False

        key_event = event
        key = key_event.key()
        text = key_event.text() or ""

        if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            return self._finish_capture()

        # 忽略修饰键（Shift/Ctrl/Alt等），不重置buffer也不追加
        if key in self._MODIFIER_KEYS:
            return self._scanner_active

        if not self._is_supported_key(text, key_event.modifiers()):
            self._reset_capture()
            return False

        now = monotonic()
        if self._last_key_at is None or now - self._last_key_at > self.MAX_INTER_KEY_SECONDS:
            self._buffer = text
            self._last_key_at = now
            self._scanner_active = False
            self._editable_target = watched if isinstance(watched, QLineEdit) else None
            return False

        if not self._scanner_active:
            self._scanner_active = True
            self._cleanup_first_character()

        self._buffer += text
        self._last_key_at = now
        return True

    @staticmethod
    def _is_supported_key(text: str, modifiers: Qt.KeyboardModifier) -> bool:
        if not text or not text.isprintable():
            return False
        if modifiers & (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.AltModifier):
            return False
        return True

    def _cleanup_first_character(self):
        if self._editable_target is None:
            return

        current_text = self._editable_target.text()
        first_char = self._buffer[:1]
        if current_text.endswith(first_char):
            self._editable_target.setText(current_text[:-1])

    def _finish_capture(self) -> bool:
        if not self._scanner_active or not self._buffer:
            self._reset_capture()
            return False

        barcode = self._buffer.strip()
        self._reset_capture()
        if barcode:
            self.barcodeReceived.emit(barcode)
            return True
        return False

    def _reset_capture(self):
        self._buffer = ""
        self._last_key_at = None
        self._scanner_active = False
        self._editable_target = None
