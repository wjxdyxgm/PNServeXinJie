"""
Binding validation helpers for startup diagnostics.
"""
from dataclasses import dataclass, field

from src.plc.binding_config import READ_BINDINGS, WRITE_BINDINGS
from src.store.gas_store import GasStore
from src.store.manual_store import ManualStore
from src.store.settings_store import SettingsStore
from src.view.manual.button_bindings import BUTTON_BINDING_MAP


@dataclass
class BindingValidationReport:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    infos: list[str] = field(default_factory=list)

    @property
    def is_ok(self) -> bool:
        return not self.errors

    def to_text(self) -> str:
        lines = ["[BindingCheck] PLC binding validation report"]

        if self.infos:
            lines.append("[BindingCheck] info:")
            lines.extend(f"  - {item}" for item in self.infos)

        if self.warnings:
            lines.append("[BindingCheck] warnings:")
            lines.extend(f"  - {item}" for item in self.warnings)

        if self.errors:
            lines.append("[BindingCheck] errors:")
            lines.extend(f"  - {item}" for item in self.errors)
        else:
            lines.append("[BindingCheck] errors: none")

        lines.append(
            f"[BindingCheck] summary: {len(self.errors)} error(s), {len(self.warnings)} warning(s)"
        )
        return "\n".join(lines)


def _duplicate_paths(bindings) -> list[str]:
    counts = {}
    for binding in bindings:
        counts[binding.store_path] = counts.get(binding.store_path, 0) + 1
    return sorted(path for path, count in counts.items() if count > 1)


def validate_binding_configuration() -> BindingValidationReport:
    report = BindingValidationReport()
    gas_store = GasStore()
    manual_store = ManualStore()
    settings_store = SettingsStore()

    read_paths = {binding.store_path for binding in READ_BINDINGS}
    write_paths = {binding.store_path for binding in WRITE_BINDINGS}

    report.infos.append(f"read bindings: {len(READ_BINDINGS)}")
    report.infos.append(f"write bindings: {len(WRITE_BINDINGS)}")
    report.infos.append(
        f"settings with declared PLC write paths: {len(settings_store.plc_write_paths)}"
    )
    report.infos.append(
        f"settings with declared PLC readback paths: {len(settings_store.plc_readback_paths)}"
    )

    read_duplicates = _duplicate_paths(READ_BINDINGS)
    write_duplicates = _duplicate_paths(WRITE_BINDINGS)
    if read_duplicates:
        report.errors.append(f"duplicate read paths: {', '.join(read_duplicates)}")
    if write_duplicates:
        report.errors.append(f"duplicate write paths: {', '.join(write_duplicates)}")

    expected_manual_read = {f"signals.{key}" for key in manual_store.signals}
    expected_manual_read |= {f"q_status.{key}" for key in manual_store.q_status}
    expected_manual_read |= {f"mode.{key}" for key in manual_store.mode_status}
    expected_manual_read |= {f"torque.{key}" for key in manual_store.torque_data}

    read_servo_fields = {
        "enable",
        "done",
        "target_pos",
        "mdi",
        "zero_offset",
        "fly_ref",
        "current_pos",
        "error_id",
    }
    for servo_id in manual_store.servo_data:
        for field_name in read_servo_fields:
            expected_manual_read.add(f"servo.{servo_id}.{field_name}")

    expected_manual_write = set(BUTTON_BINDING_MAP.values())
    expected_manual_write |= {
        ManualStore.MANUAL_MODE_PATH,
        ManualStore.AUTO_GAS_MODE_PATH,
    }
    write_servo_fields = {
        "enable",
        "execute",
        "mode",
        "target_pos",
        "mdi",
        "zero_offset",
        "fly_ref",
        "reset_err",
    }
    for servo_id in manual_store.servo_data:
        for field_name in write_servo_fields:
            expected_manual_write.add(f"servo.{servo_id}.{field_name}")

    expected_settings_write = set(settings_store.plc_write_paths.values())
    expected_settings_read = set(settings_store.plc_readback_paths.values())
    expected_gas_read = set(gas_store.PLC_READ_PATHS)
    unmanaged_settings = sorted(settings_store.unmanaged_keys)
    write_only_settings = sorted(settings_store.write_only_keys)

    missing_manual_read = sorted(expected_manual_read - read_paths)
    extra_manual_read = sorted(
        path
        for path in read_paths
        if (
            path.startswith("signals.")
            or path.startswith("q_status.")
            or path.startswith("mode.")
            or path.startswith("servo.")
            or path.startswith("torque.")
        )
        and path not in expected_manual_read
    )
    missing_manual_write = sorted(expected_manual_write - write_paths)
    missing_settings_read = sorted(expected_settings_read - read_paths)
    missing_settings_write = sorted(expected_settings_write - write_paths)
    missing_gas_read = sorted(expected_gas_read - read_paths)

    if missing_manual_read:
        report.errors.append(f"missing manual read bindings: {', '.join(missing_manual_read)}")
    if extra_manual_read:
        report.errors.append(f"read bindings not represented in store: {', '.join(extra_manual_read)}")
    if missing_manual_write:
        report.errors.append(f"missing manual write bindings: {', '.join(missing_manual_write)}")
    if missing_settings_read:
        report.errors.append(f"missing settings read bindings: {', '.join(missing_settings_read)}")
    if missing_settings_write:
        report.errors.append(f"missing settings write bindings: {', '.join(missing_settings_write)}")
    if missing_gas_read:
        report.errors.append(f"missing gas read bindings: {', '.join(missing_gas_read)}")

    if unmanaged_settings:
        report.warnings.append(
            "settings without declared PLC paths: " + ", ".join(unmanaged_settings)
        )
    if write_only_settings:
        report.warnings.append(
            "settings without PLC readback paths: " + ", ".join(write_only_settings)
        )

    return report


def print_binding_validation_report() -> BindingValidationReport:
    report = validate_binding_configuration()
    print(report.to_text())
    return report
