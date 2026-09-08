"""
Pydantic schemas - קו ההגנה הראשון על גבול הרשת (Defense in Depth).
כל קלט חיצוני עובר ולידציה קפדנית: אורך, טווח ותווים מותרים, לפני שהוא נוגע
בכל שכבה עסקית אחרת.
"""
from __future__ import annotations

import re
import unicodedata
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

_MAX_NAME_LENGTH = 100
_MAX_REASON_LENGTH = 100
_MAX_REASONS = 10
_ALLOWED_NAME_PATTERN = re.compile(r"^[\w\u0590-\u05FF' \-]+$", re.UNICODE)


def _strip_control_chars(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value).strip()
    return "".join(ch for ch in normalized if unicodedata.category(ch)[0] != "C")


class ScoreSubmission(BaseModel):
    """גוף הבקשה ב-POST /api/v1/scores - נשלח ע"י קוד הלקוח."""

    student_id: str = Field(..., min_length=1, max_length=_MAX_NAME_LENGTH)
    focus_score: int = Field(..., ge=0, le=100)
    reasons: List[str] = Field(default_factory=list, max_length=_MAX_REASONS)

    @field_validator("student_id")
    @classmethod
    def _validate_student_id(cls, value: str) -> str:
        cleaned = _strip_control_chars(value)[:_MAX_NAME_LENGTH].strip()
        if not cleaned:
            raise ValueError("student_id לא יכול להיות ריק")
        if not _ALLOWED_NAME_PATTERN.match(cleaned):
            raise ValueError("student_id מכיל תווים לא חוקיים")
        return cleaned

    @field_validator("reasons")
    @classmethod
    def _validate_reasons(cls, value: List[str]) -> List[str]:
        return [_strip_control_chars(reason)[:_MAX_REASON_LENGTH] for reason in value]


class ScoreSubmissionResponse(BaseModel):
    status: str
    message: Optional[str] = None


class DashboardStudent(BaseModel):
    """מצב תלמידה עדכני, כפי שמוצג בדשבורד."""

    score: int
    last_seen: float
