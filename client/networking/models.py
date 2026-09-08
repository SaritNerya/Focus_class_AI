"""מודלים פשוטים (dataclasses, לא Pydantic) לשליחה לשרת - הלקוח נשאר קליל
ולא תלוי בספריות של צד השרת."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class ScoreSubmission:
    student_id: str
    focus_score: int
    reasons: List[str] = field(default_factory=list)

    def to_json_dict(self) -> dict:
        return {
            "student_id": self.student_id,
            "focus_score": self.focus_score,
            "reasons": self.reasons,
        }
