"""
PLC address binding compatibility module.

The binding declarations are split by domain under ``src.plc.bindings``.
Keep this module as the stable import path for PLCBridge and validation code.
"""
from src.plc.bindings import (
    ALL_BINDINGS,
    BUTTON_BINDINGS,
    ENABLE_BINDINGS,
    GAS_BINDINGS,
    MODE_BINDINGS,
    MODE_WRITE_BINDINGS,
    Q_STATUS_BINDINGS,
    READ_BINDINGS,
    SERVO_M_BINDINGS,
    SERVO_V_BINDINGS,
    SETTINGS_LIMIT_BINDINGS,
    SETTINGS_RUN_MODE_BINDINGS,
    SIGNAL_BINDINGS,
    TORQUE_BINDINGS,
    WRITE_BINDINGS,
)

__all__ = [
    "SIGNAL_BINDINGS",
    "Q_STATUS_BINDINGS",
    "MODE_BINDINGS",
    "MODE_WRITE_BINDINGS",
    "BUTTON_BINDINGS",
    "ENABLE_BINDINGS",
    "SERVO_M_BINDINGS",
    "SERVO_V_BINDINGS",
    "TORQUE_BINDINGS",
    "SETTINGS_RUN_MODE_BINDINGS",
    "SETTINGS_LIMIT_BINDINGS",
    "GAS_BINDINGS",
    "ALL_BINDINGS",
    "READ_BINDINGS",
    "WRITE_BINDINGS",
]
