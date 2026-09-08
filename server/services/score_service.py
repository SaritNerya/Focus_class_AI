"""שכבת השירות (Service Layer) - לוגיקה עסקית מופרדת מהראוטרים (שנשארים
דקים ואחראים רק על HTTP) ומה-repository (שאחראי רק על גישה לנתונים)."""
from __future__ import annotations

from typing import Dict

from server.domain.schemas import DashboardStudent, ScoreSubmission
from server.repositories.student_repository import IStudentRepository


class ScoreService:
    def __init__(self, repository: IStudentRepository, student_timeout_seconds: float) -> None:
        self._repository = repository
        self._student_timeout_seconds = student_timeout_seconds

    def submit_score(self, submission: ScoreSubmission) -> None:
        self._repository.upsert(submission.student_id, submission.focus_score, submission.reasons)

    def get_dashboard_state(self) -> Dict[str, DashboardStudent]:
        active = self._repository.get_active(self._student_timeout_seconds)
        return {
            name: DashboardStudent(score=state.score, last_seen=state.last_seen)
            for name, state in active.items()
        }
