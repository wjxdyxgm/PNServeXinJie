from __future__ import annotations


def list_serial_ports() -> list[str]:
    ports = set(_list_serial_ports_from_pyserial())
    ports.update(_list_serial_ports_from_registry())
    return sorted(port for port in ports if port)


def _list_serial_ports_from_pyserial() -> list[str]:
    try:
        from serial.tools import list_ports
    except ImportError:
        return []

    try:
        return [
            str(port.device).strip()
            for port in list_ports.comports()
            if getattr(port, "device", "")
        ]
    except Exception:
        return []


def _list_serial_ports_from_registry() -> list[str]:
    try:
        import winreg
    except ImportError:
        return []

    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DEVICEMAP\SERIALCOMM") as key:
            ports = []
            index = 0
            while True:
                try:
                    _, value, _ = winreg.EnumValue(key, index)
                except OSError:
                    break

                if value:
                    ports.append(str(value).strip())
                index += 1
    except OSError:
        return []

    return ports
