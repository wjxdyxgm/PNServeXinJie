from __future__ import annotations


def build_footer_feedback(manual_store) -> tuple[tuple[float, float, float, float], tuple[float, float, float, float]]:
    """从 ManualStore 提取页脚反馈值。"""

    torque_values = (
        _float_value(manual_store.torque_data.get("torque_1", 0.0)),
        _float_value(manual_store.torque_data.get("torque_2", 0.0)),
        _float_value(manual_store.torque_data.get("torque_3", 0.0)),
        _float_value(manual_store.torque_data.get("torque_4", 0.0)),
    )
    servo_values = (
        _float_value(manual_store.servo_data.get(1, {}).get("current_pos", 0)) / 1000,
        _float_value(manual_store.servo_data.get(2, {}).get("current_pos", 0)) / 1000,
        _float_value(manual_store.servo_data.get(3, {}).get("current_pos", 0)) / 1000,
        _float_value(manual_store.servo_data.get(4, {}).get("current_pos", 0)) / 1000,
    )
    return torque_values, servo_values


def _float_value(value) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0
