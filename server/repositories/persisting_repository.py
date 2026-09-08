"""
PersistingStudentRepository - שוב תבנית Decorator, הפעם ברמת השרת: עוטפת
repository קיים (למשל InMemoryStudentRepository) ומוסיפה עליו התנהגות של
שמירה מתמשכת ל-DB, מבלי לשנות את ממשק IStudentRepository או את הצרכנים שלו.
זו אותה שפת עיצוב כמו שרשרת העונשים בלקוח - עקביות ארכיטקטונית לאורך הפרויקט.
"""
from __future__ import annotations

import logging
from typing import Callable, Dict, List

from sqlalchemy.orm import Session

from server.db.models import ScoreLog
from server.repositories.student_repository import IStudentRepository, StudentState

logger = logging.getLogger(__name__)


class PersistingStudentRepository(IStudentRepository):
    def __init__(self, wrapped: IStudentRepository, session_factory: Callable[[], Session]) -> None:
        self._wrapped = wrapped
        self._session_factory = session_factory

    def upsert(self, student_name: str, score: int, reasons: List[str]) -> None:
        self._wrapped.upsert(student_name, score, reasons)
        self._persist(student_name, score, reasons)

    def get_active(self, timeout_seconds: float) -> Dict[str, StudentState]:
        return self._wrapped.get_active(timeout_seconds)

    def _persist(self, student_name: str, score: int, reasons: List[str]) -> None:
        """כתיבה ל-DB לצורך היסטוריה/ביקורת. כשל בכתיבה לא אמור להפיל את
        הבקשה (המצב החי כבר עודכן בהצלחה ב-in-memory cache)."""
        session = self._session_factory()
        try:
            session.add(ScoreLog(student_name=student_name, score=score, reasons=", ".join(reasons)))
            session.commit()
        except Exception as exc:  # noqa: BLE001 - persistence is best-effort, never blocks the live path
            logger.error("נכשלה שמירת ScoreLog ל-DB: %s", exc)
            session.rollback()
        finally:
            session.close()
