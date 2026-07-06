"""
Gas page store.
"""
from __future__ import annotations

from datetime import datetime

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot


class GasStore(QObject):
    dataChanged = pyqtSignal()
    recordInserted = pyqtSignal(int, str, str)
    writeRequested = pyqtSignal(str, object)
    runSeqChanged = pyqtSignal(int)  # run_seq 值变化时 emit

    TRIGGER_PATH = "gas.trigger"
    PRODUCT_CODE_PATH = "gas.product_code_raw"
    CODE_PRESENT_PATH = "gas.code_present"
    RESET_COUNTS_PATH = "gas.reset_counts"
    RUN_SEQ_PATH = "gas.run_seq"
    COND_TRUE_OK_PATH = "gas.cond_true_ok"
    COND_TRUE_NG_PATH = "gas.cond_true_ng"
    OPERATOR_PATH = "gas.operator_raw"
    AIRTIGHT_RESULT_PATH = "gas.airtight_result"
    PIN1_PRESSURE_PATH = "gas.pin1_pressure"
    PIN1_PRESSURE_RESULT_PATH = "gas.pin1_pressure_result"
    PIN1_DISTANCE_PATH = "gas.pin1_distance"
    PIN1_DISTANCE_RESULT_PATH = "gas.pin1_distance_result"
    PIN2_PRESSURE_PATH = "gas.pin2_pressure"
    PIN2_PRESSURE_RESULT_PATH = "gas.pin2_pressure_result"
    PIN2_DISTANCE_PATH = "gas.pin2_distance"
    PIN2_DISTANCE_RESULT_PATH = "gas.pin2_distance_result"
    PIN3_PRESSURE_PATH = "gas.pin3_pressure"
    PIN3_PRESSURE_RESULT_PATH = "gas.pin3_pressure_result"
    PIN3_DISTANCE_PATH = "gas.pin3_distance"
    PIN3_DISTANCE_RESULT_PATH = "gas.pin3_distance_result"
    PIN4_PRESSURE_PATH = "gas.pin4_pressure"
    PIN4_PRESSURE_RESULT_PATH = "gas.pin4_pressure_result"
    PIN4_DISTANCE_PATH = "gas.pin4_distance"
    PIN4_DISTANCE_RESULT_PATH = "gas.pin4_distance_result"
    COUNT_OK_PATH = "gas.count_ok"
    COUNT_NG_PATH = "gas.count_ng"
    COUNT_TOTAL_PATH = "gas.count_total"

    PAGE_SIZE = 20
    RESULT_TEXT = {0: "未记录", 1: "OK", 2: "NG"}

    PLC_READ_PATHS = (
        TRIGGER_PATH,
        PRODUCT_CODE_PATH,
        RUN_SEQ_PATH,
        COND_TRUE_OK_PATH,
        COND_TRUE_NG_PATH,
        AIRTIGHT_RESULT_PATH,
        OPERATOR_PATH,
        PIN1_PRESSURE_PATH,
        PIN1_PRESSURE_RESULT_PATH,
        PIN1_DISTANCE_PATH,
        PIN1_DISTANCE_RESULT_PATH,
        PIN2_PRESSURE_PATH,
        PIN2_PRESSURE_RESULT_PATH,
        PIN2_DISTANCE_PATH,
        PIN2_DISTANCE_RESULT_PATH,
        PIN3_PRESSURE_PATH,
        PIN3_PRESSURE_RESULT_PATH,
        PIN3_DISTANCE_PATH,
        PIN3_DISTANCE_RESULT_PATH,
        PIN4_PRESSURE_PATH,
        PIN4_PRESSURE_RESULT_PATH,
        PIN4_DISTANCE_PATH,
        PIN4_DISTANCE_RESULT_PATH,
        COUNT_OK_PATH,
        COUNT_NG_PATH,
        COUNT_TOTAL_PATH,
    )

    _BUFFER_PATH_TO_FIELD = {
        PRODUCT_CODE_PATH: "product_code",
        OPERATOR_PATH: "operator",
    }
    _NUMERIC_PATH_TO_FIELD = {
        RUN_SEQ_PATH: "run_seq",
        AIRTIGHT_RESULT_PATH: "airtight_result",
        PIN1_PRESSURE_PATH: "pin1_pressure",
        PIN1_PRESSURE_RESULT_PATH: "pin1_pressure_result",
        PIN1_DISTANCE_PATH: "pin1_distance",
        PIN1_DISTANCE_RESULT_PATH: "pin1_distance_result",
        PIN2_PRESSURE_PATH: "pin2_pressure",
        PIN2_PRESSURE_RESULT_PATH: "pin2_pressure_result",
        PIN2_DISTANCE_PATH: "pin2_distance",
        PIN2_DISTANCE_RESULT_PATH: "pin2_distance_result",
        PIN3_PRESSURE_PATH: "pin3_pressure",
        PIN3_PRESSURE_RESULT_PATH: "pin3_pressure_result",
        PIN3_DISTANCE_PATH: "pin3_distance",
        PIN3_DISTANCE_RESULT_PATH: "pin3_distance_result",
        PIN4_PRESSURE_PATH: "pin4_pressure",
        PIN4_PRESSURE_RESULT_PATH: "pin4_pressure_result",
        PIN4_DISTANCE_PATH: "pin4_distance",
        PIN4_DISTANCE_RESULT_PATH: "pin4_distance_result",
        COUNT_OK_PATH: "count_ok",
        COUNT_NG_PATH: "count_ng",
        COUNT_TOTAL_PATH: "count_total",
    }
    _BOOL_PATH_TO_FIELD = {
        COND_TRUE_OK_PATH: "cond_true_ok",
        COND_TRUE_NG_PATH: "cond_true_ng",
    }
    _FLOAT_FIELDS = {
        "pin1_pressure",
        "pin1_distance",
        "pin2_pressure",
        "pin2_distance",
        "pin3_pressure",
        "pin3_distance",
        "pin4_pressure",
        "pin4_distance",
    }
    _RESULT_FIELDS = {
        "airtight_result",
        "pin1_pressure_result",
        "pin1_distance_result",
        "pin2_pressure_result",
        "pin2_distance_result",
        "pin3_pressure_result",
        "pin3_distance_result",
        "pin4_pressure_result",
        "pin4_distance_result",
    }

    def __init__(self, db=None, parent=None):
        super().__init__(parent)
        self.search_keyword = ""
        self.date_range = ("", "")
        self.page_index = 1
        self.page_size = self.PAGE_SIZE
        self.current_data = self._default_current_data()
        self._trigger_prev = False
        self._db = db

    def set_database(self, db) -> None:
        self._db = db

    def set_search(self, keyword: str = "", date_start: str = "", date_end: str = ""):
        changed = (
            self.search_keyword != keyword
            or self.date_range != (date_start, date_end)
            or self.page_index != 1
        )
        self.search_keyword = keyword
        self.date_range = (date_start, date_end)
        self.page_index = 1
        if changed:
            self.dataChanged.emit()

    def set_page(self, index: int):
        index = max(1, int(index))
        if self.page_index != index:
            self.page_index = index
            self.dataChanged.emit()

    def update_current_data(self, **kwargs):
        changed = False
        for key, value in kwargs.items():
            if key in self.current_data and self.current_data[key] != value:
                self.current_data[key] = value
                changed = True
        if changed:
            self.dataChanged.emit()

    def reset_current_data(self):
        reset = self._default_current_data()
        if reset != self.current_data:
            self.current_data = reset
            self._trigger_prev = False
            self.clear_code_present()
            self.dataChanged.emit()

    def load_records(self) -> tuple[list[dict], int]:
        if not self._db:
            return [], 0
        date_start, date_end = self.date_range
        return self._db.query(
            keyword=self.search_keyword,
            date_start=date_start,
            date_end=date_end,
            page=self.page_index,
            page_size=self.page_size,
        )

    def load_all_records(self) -> list[dict]:
        if not self._db:
            return []
        date_start, date_end = self.date_range
        return self._db.query_all(date_start=date_start, date_end=date_end)

    def get_ok_ng_count(self) -> tuple[int, int]:
        if not self._db:
            return 0, 0
        date_start, date_end = self.date_range
        return self._db.count_ok_ng(date_start=date_start, date_end=date_end)

    def update_chart_image(self, record_id: int, path: str) -> None:
        if not self._db:
            return
        self._db.update_chart_image(record_id, path)

    def signal_code_present(self) -> None:
        self.writeRequested.emit(self.CODE_PRESENT_PATH, True)

    def clear_code_present(self) -> None:
        self.writeRequested.emit(self.CODE_PRESENT_PATH, False)

    def reset_statistics(self) -> None:
        self.writeRequested.emit(self.RESET_COUNTS_PATH, True)
        self.writeRequested.emit(self.RESET_COUNTS_PATH, False)

    def get_status_card_state(self) -> str:
        run_seq = int(self.current_data.get("run_seq", 0) or 0)
        cond_true_ok = bool(self.current_data.get("cond_true_ok", False))
        cond_true_ng = bool(self.current_data.get("cond_true_ng", False))

        if run_seq == 10:
            return "pending"
        if 10 < run_seq < 600:
            if cond_true_ng:
                return "ng"
            if cond_true_ok:
                return "ok"
        return "pending"

    def to_dict(self) -> dict:
        return {
            "search_keyword": self.search_keyword,
            "date_range": self.date_range,
            "page_index": self.page_index,
            "page_size": self.page_size,
            "current_data": dict(self.current_data),
        }

    @pyqtSlot(str, object)
    def apply_plc_value(self, store_path: str, value):
        if store_path == self.TRIGGER_PATH:
            trigger = bool(value)
            rising_edge = trigger and not self._trigger_prev
            self._trigger_prev = trigger
            if rising_edge:
                self._on_trigger()
            return

        if store_path in self._BUFFER_PATH_TO_FIELD:
            field_name = self._BUFFER_PATH_TO_FIELD[store_path]
            self.update_current_data(**{field_name: self._decode_ascii_buffer(value)})
            return

        if store_path in self._BOOL_PATH_TO_FIELD:
            field_name = self._BOOL_PATH_TO_FIELD[store_path]
            self.update_current_data(**{field_name: bool(value)})
            return

        if store_path in self._NUMERIC_PATH_TO_FIELD:
            field_name = self._NUMERIC_PATH_TO_FIELD[store_path]
            coerced = self._coerce_field_value(field_name, value)
            self.update_current_data(**{field_name: coerced})
            if store_path == self.RUN_SEQ_PATH:
                self.runSeqChanged.emit(int(coerced))

    def _on_trigger(self):
        record = self._build_record_snapshot()
        if not self._db:
            return
        record_id = int(self._db.insert(record))
        self.recordInserted.emit(record_id, record["product_code"], record["timestamp"])

    def _build_record_snapshot(self) -> dict:
        return {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "product_code": self.current_data["product_code"],
            "operator": self.current_data["operator"],
            "airtight": self.current_data["airtight_result"],
            "pin1_pressure": self.current_data["pin1_pressure"],
            "pin1_pressure_result": self.current_data["pin1_pressure_result"],
            "pin1_distance": self.current_data["pin1_distance"],
            "pin1_distance_result": self.current_data["pin1_distance_result"],
            "pin2_pressure": self.current_data["pin2_pressure"],
            "pin2_pressure_result": self.current_data["pin2_pressure_result"],
            "pin2_distance": self.current_data["pin2_distance"],
            "pin2_distance_result": self.current_data["pin2_distance_result"],
            "pin3_pressure": self.current_data["pin3_pressure"],
            "pin3_pressure_result": self.current_data["pin3_pressure_result"],
            "pin3_distance": self.current_data["pin3_distance"],
            "pin3_distance_result": self.current_data["pin3_distance_result"],
            "pin4_pressure": self.current_data["pin4_pressure"],
            "pin4_pressure_result": self.current_data["pin4_pressure_result"],
            "pin4_distance": self.current_data["pin4_distance"],
            "pin4_distance_result": self.current_data["pin4_distance_result"],
        }

    @classmethod
    def result_to_text(cls, value) -> str:
        try:
            value = int(value)
        except (TypeError, ValueError):
            return ""
        return cls.RESULT_TEXT.get(value, "")

    @staticmethod
    def _default_current_data() -> dict:
        return {
            "product_code": "",
            "operator": "",
            "run_seq": 0,
            "cond_true_ok": False,
            "cond_true_ng": False,
            "airtight_result": 0,
            "pin1_pressure": 0.0,
            "pin1_pressure_result": 0,
            "pin1_distance": 0.0,
            "pin1_distance_result": 0,
            "pin2_pressure": 0.0,
            "pin2_pressure_result": 0,
            "pin2_distance": 0.0,
            "pin2_distance_result": 0,
            "pin3_pressure": 0.0,
            "pin3_pressure_result": 0,
            "pin3_distance": 0.0,
            "pin3_distance_result": 0,
            "pin4_pressure": 0.0,
            "pin4_pressure_result": 0,
            "pin4_distance": 0.0,
            "pin4_distance_result": 0,
            "count_ok": 0,
            "count_ng": 0,
            "count_total": 0,
        }

    @staticmethod
    def _decode_ascii_buffer(value) -> str:
        if isinstance(value, str):
            return value.strip()
        if not isinstance(value, (bytes, bytearray)):
            return ""

        raw = bytes(value)
        if b"\x00" in raw:
            raw = raw.split(b"\x00", 1)[0]
        return raw.decode("gbk", errors="ignore").strip()

    def _coerce_field_value(self, field_name: str, value):
        if field_name in self._FLOAT_FIELDS:
            try:
                return float(value)
            except (TypeError, ValueError):
                return 0.0

        if field_name in self._RESULT_FIELDS:
            try:
                return int(value)
            except (TypeError, ValueError):
                return 0

        return value
