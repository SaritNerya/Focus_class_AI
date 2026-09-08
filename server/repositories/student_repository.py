"""
שכבת ה-Repository - מפשטת את שאלת "איפה שמורים הנתונים" משאר האפליקציה
(Dependency Inversion: ה-service תלוי בממשק IStudentRepository, לא במימוש).

InMemoryStudentRepository: מצב "חי" מהיר (thread-safe) לצורך הדשבורד -
תשובה תוך מיקרושניות, בלי לפגוע ב-DB בכל בקשת polling של הדשבורד (שקורית
פעם בשנייה מכל דפדפן מחובר).
"""
from __future__ import annotations

import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(frozen=True)
class StudentState:
    score: int
    reasons: List[str]
    last_seen: float


class IStudentRepository(ABC):
    @abstractmethod
    def upsert(self, student_name: str, score: int, reasons: List[str]) -> None: ...

    @abstractmethod
    def get_active(self, timeout_seconds: float) -> Dict[str, StudentState]: ...


class InMemoryStudentRepository(IStudentRepository):
    """מקור האמת ל'מי מחובר עכשיו' - dict מוגן בעזרת Lock (הבקשות מגיעות
    מ-threadpool, ולכן חייבים הגנה מפני race conditions)."""

    def __init__(self) -> None:
        self._students: Dict[str, StudentState] = {}
        self._lock = threading.Lock()

    def upsert(self, student_name: str, score: int, reasons: List[str]) -> None:
        with self._lock:
            self._students[student_name] = StudentState(score=score, reasons=reasons, last_seen=time.time())

    def get_active(self, timeout_seconds: float) -> Dict[str, StudentState]:
        now = time.time()
        with self._lock:
            expired = [name for name, state in self._students.items() if now - state.last_seen > timeout_seconds]
            for name in expired:
                del self._students[name]
            return dict(self._students)
