"""
SQLite helpers for gas inspection records.
"""
from __future__ import annotations

import sqlite3
import threading
from pathlib import Path

from src.common.app_paths import gas_records_db_path


class GasRecordDB:
    TABLE_NAME = "gas_records"
    CHART_IMAGE_COLUMN = "chart_image"
    RECORD_COLUMNS = (
        "timestamp",
        "product_code",
        "operator",
        "airtight",
        "pin1_pressure",
        "pin1_pressure_result",
        "pin1_distance",
        "pin1_distance_result",
        "pin2_pressure",
        "pin2_pressure_result",
        "pin2_distance",
        "pin2_distance_result",
        "pin3_pressure",
        "pin3_pressure_result",
        "pin3_distance",
        "pin3_distance_result",
        "pin4_pressure",
        "pin4_pressure_result",
        "pin4_distance",
        "pin4_distance_result",
    )

    def __init__(self, db_path: str | Path | None = None):
        if db_path is None:
            db_path = gas_records_db_path()

        self._db_path = db_path
        self._lock = threading.RLock()
        self._conn = self._connect(db_path)
        self._conn.row_factory = sqlite3.Row
        self._init_schema()

    @property
    def db_path(self) -> str | Path:
        return self._db_path

    def insert(self, record: dict) -> int:
        payload = {column: record.get(column) for column in self.RECORD_COLUMNS}
        placeholders = ", ".join("?" for _ in self.RECORD_COLUMNS)
        sql = (
            f"INSERT INTO {self.TABLE_NAME} ({', '.join(self.RECORD_COLUMNS)}) "
            f"VALUES ({placeholders})"
        )
        with self._lock:
            cursor = self._conn.execute(
                sql,
                tuple(payload[column] for column in self.RECORD_COLUMNS),
            )
            self._conn.commit()
            return int(cursor.lastrowid)

    def query(
        self,
        keyword: str = "",
        date_start: str = "",
        date_end: str = "",
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[dict], int]:
        page = max(1, int(page))
        page_size = max(1, int(page_size))
        where_sql, params = self._build_filters(keyword, date_start, date_end)

        with self._lock:
            total_count = int(
                self._conn.execute(
                    f"SELECT COUNT(*) FROM {self.TABLE_NAME}{where_sql}",
                    params,
                ).fetchone()[0]
            )

            rows = self._conn.execute(
                f"SELECT * FROM {self.TABLE_NAME}{where_sql} "
                "ORDER BY id DESC LIMIT ? OFFSET ?",
                params + [page_size, (page - 1) * page_size],
            ).fetchall()

        return [dict(row) for row in rows], total_count

    def query_all(
        self,
        keyword: str = "",
        date_start: str = "",
        date_end: str = "",
    ) -> list[dict]:
        where_sql, params = self._build_filters(keyword, date_start, date_end)
        with self._lock:
            rows = self._conn.execute(
                f"SELECT * FROM {self.TABLE_NAME}{where_sql} ORDER BY id DESC",
                params,
            ).fetchall()
        return [dict(row) for row in rows]

    def update_chart_image(self, record_id: int, image_path: str) -> None:
        sql = f"UPDATE {self.TABLE_NAME} SET {self.CHART_IMAGE_COLUMN} = ? WHERE id = ?"
        with self._lock:
            self._conn.execute(sql, (image_path, int(record_id)))
            self._conn.commit()

    def count_ok_ng(
        self,
        date_start: str = "",
        date_end: str = "",
    ) -> tuple[int, int]:
        where_sql, params = self._build_filters("", date_start, date_end)
        sql = (
            f"SELECT "
            "SUM(CASE WHEN airtight = 1 THEN 1 ELSE 0 END) AS ok_count, "
            "SUM(CASE WHEN airtight = 2 THEN 1 ELSE 0 END) AS ng_count "
            f"FROM {self.TABLE_NAME}{where_sql}"
        )
        with self._lock:
            row = self._conn.execute(sql, params).fetchone()
        ok_count = int(row["ok_count"] or 0)
        ng_count = int(row["ng_count"] or 0)
        return ok_count, ng_count

    def close(self) -> None:
        with self._lock:
            self._conn.close()

    def _connect(self, db_path: str | Path) -> sqlite3.Connection:
        if isinstance(db_path, Path):
            db_path.parent.mkdir(parents=True, exist_ok=True)
            return sqlite3.connect(str(db_path), check_same_thread=False)

        if db_path != ":memory:" and not str(db_path).startswith("file:"):
            path_obj = Path(db_path)
            path_obj.parent.mkdir(parents=True, exist_ok=True)
            db_path = str(path_obj)
        return sqlite3.connect(db_path, check_same_thread=False)

    def _init_schema(self) -> None:
        sql = f"""
        CREATE TABLE IF NOT EXISTS {self.TABLE_NAME} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            product_code TEXT NOT NULL,
            operator TEXT NOT NULL,
            airtight INTEGER NOT NULL,
            pin1_pressure REAL,
            pin1_pressure_result INTEGER,
            pin1_distance REAL,
            pin1_distance_result INTEGER,
            pin2_pressure REAL,
            pin2_pressure_result INTEGER,
            pin2_distance REAL,
            pin2_distance_result INTEGER,
            pin3_pressure REAL,
            pin3_pressure_result INTEGER,
            pin3_distance REAL,
            pin3_distance_result INTEGER,
            pin4_pressure REAL,
            pin4_pressure_result INTEGER,
            pin4_distance REAL,
            pin4_distance_result INTEGER,
            {self.CHART_IMAGE_COLUMN} TEXT
        )
        """
        with self._lock:
            self._conn.execute(sql)
            self._ensure_chart_image_column()
            self._ensure_pin34_columns()
            self._conn.commit()

    def _ensure_chart_image_column(self) -> None:
        columns = {
            row["name"]
            for row in self._conn.execute(f"PRAGMA table_info({self.TABLE_NAME})").fetchall()
        }
        if self.CHART_IMAGE_COLUMN in columns:
            return
        self._conn.execute(
            f"ALTER TABLE {self.TABLE_NAME} ADD COLUMN {self.CHART_IMAGE_COLUMN} TEXT"
        )

    _PIN34_COLUMNS = {
        "pin3_pressure": "REAL",
        "pin3_pressure_result": "INTEGER",
        "pin3_distance": "REAL",
        "pin3_distance_result": "INTEGER",
        "pin4_pressure": "REAL",
        "pin4_pressure_result": "INTEGER",
        "pin4_distance": "REAL",
        "pin4_distance_result": "INTEGER",
    }

    def _ensure_pin34_columns(self) -> None:
        existing = {
            row["name"]
            for row in self._conn.execute(f"PRAGMA table_info({self.TABLE_NAME})").fetchall()
        }
        for col_name, col_type in self._PIN34_COLUMNS.items():
            if col_name not in existing:
                self._conn.execute(
                    f"ALTER TABLE {self.TABLE_NAME} ADD COLUMN {col_name} {col_type}"
                )

    def _build_filters(
        self,
        keyword: str = "",
        date_start: str = "",
        date_end: str = "",
    ) -> tuple[str, list]:
        conditions = []
        params: list = []

        keyword = keyword.strip()
        if keyword:
            like_value = f"%{keyword}%"
            conditions.append("(product_code LIKE ? OR operator LIKE ?)")
            params.extend([like_value, like_value])

        if date_start:
            conditions.append("date(timestamp) >= date(?)")
            params.append(date_start)

        if date_end:
            conditions.append("date(timestamp) <= date(?)")
            params.append(date_end)

        if not conditions:
            return "", params
        return " WHERE " + " AND ".join(conditions), params
