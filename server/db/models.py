"""
מודלי ORM. שימי לב: השימוש ב-SQLAlchemy (ORM) במקום SQL גולמי הוא כשלעצמו
אמצעי אבטחה - כל הפרמטרים נשלחים בצורה מפורשת (parameterized), כך שאין שום
דרך "טבעית" לבצע SQL Injection דרך הקוד הזה.
"""
from __future__ import annotations

import time

from sqlalchemy import Float, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from server.db.base import Base


class ScoreLog(Base):
    """רשומת היסטוריה: כל עדכון ציון שהתקבל מהלקוחות, לצורך ביקורת/אנליטיקה
    (לא לצורך שליפת "המצב החי" בדשבורד - זה תפקיד ה-cache בזיכרון)."""

    __tablename__ = "score_logs"
    __table_args__ = (Index("ix_score_logs_student_created", "student_name", "created_at"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_name: Mapped[str] = mapped_column(String(100), nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    reasons: Mapped[str] = mapped_column(String(1024), nullable=False, default="")
    created_at: Mapped[float] = mapped_column(Float, nullable=False, default=time.time)
