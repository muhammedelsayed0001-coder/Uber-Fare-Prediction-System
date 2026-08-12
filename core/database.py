"""SQLite persistence layer for the Uber Fare Estimator.

Single responsibility: persist and retrieve prediction records.
This module knows nothing about Streamlit, the ML model, or the
feature engineering internals beyond the plain data it's handed —
that keeps it swappable (e.g. for Postgres later) without touching
app.py, in line with the Dependency Inversion / Open-Closed
principles.
"""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Iterator, Optional

DEFAULT_DB_PATH = Path(__file__).resolve().parent / "predictions.db"


@dataclass
class PredictionRecord:
    """A single prediction request, ready to be persisted or read back."""

    pickup_lat: float
    pickup_lon: float
    dropoff_lat: float
    dropoff_lon: float
    pickup_datetime: datetime
    passenger_count: int
    predicted_fare: float
    engineered_features: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    id: Optional[int] = None

    def to_row(self) -> tuple:
        """Serialize to a tuple matching the INSERT column order."""
        return (
            self.pickup_lat,
            self.pickup_lon,
            self.dropoff_lat,
            self.dropoff_lon,
            self.pickup_datetime.isoformat(),
            self.passenger_count,
            self.predicted_fare,
            json.dumps(self.engineered_features, default=str),
            self.created_at.isoformat(),
        )

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "PredictionRecord":
        return cls(
            id=row["id"],
            pickup_lat=row["pickup_lat"],
            pickup_lon=row["pickup_lon"],
            dropoff_lat=row["dropoff_lat"],
            dropoff_lon=row["dropoff_lon"],
            pickup_datetime=datetime.fromisoformat(row["pickup_datetime"]),
            passenger_count=row["passenger_count"],
            predicted_fare=row["predicted_fare"],
            engineered_features=json.loads(row["engineered_features"] or "{}"),
            created_at=datetime.fromisoformat(row["created_at"]),
        )


class PredictionRepository:
    """All SQLite access for prediction records lives here.

    Only this class touches sqlite3/SQL directly (Single Responsibility).
    Callers (e.g. app.py) work with PredictionRecord objects only.
    """

    _CREATE_TABLE_SQL = """
        CREATE TABLE IF NOT EXISTS predictions (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            pickup_lat          REAL NOT NULL,
            pickup_lon          REAL NOT NULL,
            dropoff_lat         REAL NOT NULL,
            dropoff_lon         REAL NOT NULL,
            pickup_datetime     TEXT NOT NULL,
            passenger_count     INTEGER NOT NULL,
            predicted_fare      REAL NOT NULL,
            engineered_features TEXT,
            created_at          TEXT NOT NULL
        )
    """

    def __init__(self, db_path: Path | str = DEFAULT_DB_PATH) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(self._CREATE_TABLE_SQL)

    def save(self, record: PredictionRecord) -> int:
        """Insert a record and return its new row id."""
        with self._connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO predictions (
                    pickup_lat, pickup_lon, dropoff_lat, dropoff_lon,
                    pickup_datetime, passenger_count, predicted_fare,
                    engineered_features, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                record.to_row(),
            )
            return cursor.lastrowid

    def get_all(self, limit: Optional[int] = None) -> list[PredictionRecord]:
        query = "SELECT * FROM predictions ORDER BY id DESC"
        if limit is not None:
            query += " LIMIT ?"
            params: tuple = (int(limit),)
        else:
            params = ()
        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [PredictionRecord.from_row(row) for row in rows]

    def get_by_id(self, record_id: int) -> Optional[PredictionRecord]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM predictions WHERE id = ?", (record_id,)
            ).fetchone()
        return PredictionRecord.from_row(row) if row else None

    def count(self) -> int:
        with self._connect() as conn:
            row = conn.execute("SELECT COUNT(*) AS c FROM predictions").fetchone()
        return row["c"]

    def delete_all(self) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM predictions")