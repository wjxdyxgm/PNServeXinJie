from __future__ import annotations

from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import QFileDialog, QMessageBox

from src.service.gas import export_gas_records_to_excel


class GasExportAction:
    """气检记录导出动作，封装文件选择和导出提示。"""

    def __init__(self, parent=None):
        self.parent = parent

    def export_records(self, records: list[dict], start_date: QDate, end_date: QDate) -> None:
        if not records:
            QMessageBox.information(self.parent, "提示", "当前时间范围内没有记录可导出。")
            return

        default_name = self._default_filename(start_date, end_date)
        filepath, _ = QFileDialog.getSaveFileName(
            self.parent,
            "导出气检记录",
            default_name,
            "Excel 文件 (*.xlsx)",
        )
        if not filepath:
            return

        try:
            export_gas_records_to_excel(records, filepath)
            QMessageBox.information(self.parent, "提示", f"导出成功！\n共 {len(records)} 条记录。")
        except Exception as exc:
            QMessageBox.warning(self.parent, "导出失败", f"导出时发生错误：\n{exc}")

    @staticmethod
    def _default_filename(start_date: QDate, end_date: QDate) -> str:
        start_str = start_date.toString("yyyy-MM-dd")
        end_str = end_date.toString("yyyy-MM-dd")
        return f"气检记录_{start_str}_{end_str}.xlsx"
