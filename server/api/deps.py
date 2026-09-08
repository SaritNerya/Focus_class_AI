"""
חיווט תלויות (Dependency Injection) של FastAPI. יוצר singleton אחד לכל
repository/service בחיי ה-process (state על app.state), כדי שכל הבקשות
ישתפו את אותו cache בזיכרון.
"""
from __future__ import annotations

from fastapi import Request

from server.repositories.student_repository import IStudentRepository
from server.services.score_service import ScoreService


def get_student_repository(request: Request) -> IStudentRepository:
    return request.app.state.student_repository


def get_score_service(request: Request) -> ScoreService:
    return request.app.state.score_service
