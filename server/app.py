"""
App Factory pattern - יוצרת ומחווטת את כל האפליקציה במקום אחד. זה מאפשר
גם ליצור מספר instance-ים עצמאיים (למשל בבדיקות אוטומטיות) בלי state גלובלי
משותף בין ריצות.
"""
from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server.api.v1.router import api_router
from server.config import settings
from server.core.exceptions import register_exception_handlers
from server.core.rate_limit import RateLimitMiddleware
from server.core.security_headers import SecurityHeadersMiddleware
from server.db.base import Base
from server.db.session import SessionLocal, engine
from server.repositories.persisting_repository import PersistingStudentRepository
from server.repositories.student_repository import InMemoryStudentRepository
from server.services.score_service import ScoreService

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("focusclass.server")


def create_app() -> FastAPI:
    app = FastAPI(
        title="FocusClass Teacher Server",
        version="2.0.0",
        docs_url="/docs" if settings.debug else None,
        redoc_url=None,
    )
    app.state.logger = logger

    # --- בסיס נתונים: יצירת טבלאות אם לא קיימות ---
    Base.metadata.create_all(bind=engine)

    # --- חיווט repository מורכב: In-Memory (מהיר, למצב חי) מעוטר בהתמדה ל-DB ---
    in_memory_repo = InMemoryStudentRepository()
    persisting_repo = PersistingStudentRepository(in_memory_repo, SessionLocal)
    app.state.student_repository = persisting_repo
    app.state.score_service = ScoreService(persisting_repo, settings.student_timeout_seconds)

    # --- Middleware (סדר חשוב: מבחוץ פנימה) ---
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RateLimitMiddleware, requests_per_minute=settings.rate_limit_requests_per_minute)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins or [],
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["Authorization", "Content-Type"],
    )

    register_exception_handlers(app)
    app.include_router(api_router)

    if not settings.cors_origins:
        logger.warning(
            "CORS_ORIGINS לא הוגדר - בקשות דפדפן מחוץ למקור השרת יידחו כברירת מחדל."
        )

    return app
