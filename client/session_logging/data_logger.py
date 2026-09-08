"""
DataLogger - רישום נתוני אימון (למשל לצורך אימון מודל ML בעתיד) לקובץ CSV.

הערה: בקוד המקורי main.py ייבא `from focus_logic.data_logger import DataLogger`
אך הקובץ הזה לא היה קיים בכלל בפרויקט (bug שהיה שובר את ההרצה). כאן הוא
ממומש בפועל, עם כתיבה בטוחה (פותחים ווסוגרים את הקובץ בכל רשומה, כדי לא
לאבד נתונים אם התהליך קורס).
"""
from __future__ import annotations

import csv
import logging
import re
import time
from pathlib import Path

logger = logging.getLogger(__name__)

_CSV_HEADERS = [
    "timestamp", "student_name", "score", "delta_ear", "delta_yaw", "delta_roll", "delta_pitch", "label",
]
_SAFE_FILENAME_PATTERN = re.compile(r"[^\w\-]+", re.UNICODE)


def _safe_filename_part(name: str) -> str:
    """מסננת את שם התלמידה לשימוש בטוח בשם קובץ (מונעת path traversal)."""
    return _SAFE_FILENAME_PATTERN.sub("_", name).strip("_") or "student"


class DataLogger:
    def __init__(self, output_dir: Path, student_name: str) -> None:
        self.is_recording = False
        self.current_label = 1  # 1 = ממוקדת, 0 = מוסחת

        output_dir.mkdir(parents=True, exist_ok=True)
        safe_name = _safe_filename_part(student_name)
        self._csv_path = output_dir / f"session_{safe_name}_{int(time.time())}.csv"
        self._write_header_if_needed()

    def _write_header_if_needed(self) -> None:
        if not self._csv_path.exists():
            with self._csv_path.open("w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow(_CSV_HEADERS)

    def toggle_recording(self) -> None:
        self.is_recording = not self.is_recording
        logger.info("הקלטת נתונים %s", "הופעלה" if self.is_recording else "הופסקה")

    def set_label(self, label: int) -> None:
        self.current_label = 1 if label == 1 else 0

    def log_data(
        self, student_name: str, score: float,
        delta_ear: float, delta_yaw: float, delta_roll: float, delta_pitch: float,
    ) -> None:
        if not self.is_recording:
            return
        try:
            with self._csv_path.open("a", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow([
                    time.time(), student_name, round(score, 2),
                    round(delta_ear, 4), round(delta_yaw, 2), round(delta_roll, 2), round(delta_pitch, 2),
                    self.current_label,
                ])
        except OSError as exc:
            logger.error("כתיבה לקובץ ה-CSV נכשלה: %s", exc)
