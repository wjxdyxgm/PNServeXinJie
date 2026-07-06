"""
开发环境配置加载模块。

从项目根目录的 dev_config.json 读取 PLC 连接参数，
支持 ethernet / wifi 两种连接方式切换。
"""
from __future__ import annotations

import json
from pathlib import Path

from src.common.app_paths import dev_config_path

# 默认配置（文件缺失或格式错误时使用）
_DEFAULTS = {
    "connection_type": "ethernet",
    "ethernet": {"plc_ip": "192.168.2.10"},
    "wifi": {"plc_ip": "192.168.3.10"},
}


def load_dev_config(path: str | Path | None = None) -> dict:
    """读取 dev_config.json，返回配置字典。

    文件不存在或 JSON 格式错误时返回默认配置的副本。
    """
    path = Path(path) if path is not None else dev_config_path()
    if not path.is_file():
        print(f"[DevConfig] 配置文件不存在，使用默认配置: {path}")
        return dict(_DEFAULTS)

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[DevConfig] 配置文件解析失败，使用默认配置: {exc}")
        return dict(_DEFAULTS)

    if not isinstance(payload, dict):
        print("[DevConfig] 配置文件格式错误（非对象），使用默认配置")
        return dict(_DEFAULTS)

    return payload


def get_plc_ip(config: dict | None = None) -> str:
    """根据 connection_type 返回对应的 PLC IP 地址。

    Args:
        config: 可选，已加载的配置字典。为 None 时自动加载配置文件。

    Returns:
        PLC IP 地址字符串。
    """
    if config is None:
        config = load_dev_config()

    conn_type = config.get("connection_type", "ethernet")
    section = config.get(conn_type, {})
    plc_ip = section.get("plc_ip")

    if not plc_ip:
        # 回退到默认值
        plc_ip = _DEFAULTS.get(conn_type, _DEFAULTS["ethernet"])["plc_ip"]
        print(f"[DevConfig] 未找到 {conn_type}.plc_ip，使用默认值: {plc_ip}")

    print(f"[DevConfig] 连接方式={conn_type}, PLC IP={plc_ip}")
    return plc_ip
