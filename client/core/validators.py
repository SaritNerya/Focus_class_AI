"""
ולידציה וסניטציה של קלט משתמש (שם התלמידה) לפני שליחה לרשת.

חשוב מבחינת אבטחה: גם אם הצד השרת מוגן (Pydantic validation + escaping ב-
תבנית ה-HTML), עדיף "להגן בשכבות" - לא לשלוח קלט גולמי לא-מסונן כבר מהלקוח.
"""
from __future__ import annotations

import re
import unicodedata

_MAX_NAME_LENGTH = 100
# מתירים אותיות (כולל עברית), רווחים, מקפים וגרשיים בודדים בלבד
_ALLOWED_NAME_PATTERN = re.compile(r"^[\w\u0590-\u05FF' \-]+$", re.UNICODE)


class InvalidStudentNameError(ValueError):
    pass


def sanitize_student_name(raw_name: str) -> str:
    """מנקה תווי בקרה, חותכת לאורך מקסימלי, ומוודאת שרק תווים מותרים נשארו."""
    if raw_name is None:
        raise InvalidStudentNameError("שם התלמידה לא יכול להיות ריק")

    normalized = unicodedata.normalize("NFKC", raw_name).strip()
    # הסרת תווי בקרה (control characters) - מונע הזרקות ותקלות תצוגה
    cleaned = "".join(ch for ch in normalized if unicodedata.category(ch)[0] != "C")
    cleaned = cleaned[:_MAX_NAME_LENGTH].strip()

    if not cleaned:
        raise InvalidStudentNameError("שם התלמידה לא יכול להיות ריק")
    if not _ALLOWED_NAME_PATTERN.match(cleaned):
        raise InvalidStudentNameError(
            "שם התלמידה יכול להכיל רק אותיות, רווחים, מקפים וגרשיים"
        )
    return cleaned
