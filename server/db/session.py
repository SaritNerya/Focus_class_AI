"""חיבור בסיס הנתונים (SQLite כברירת מחדל, אך database_url ניתן להחלפה בקלות
ל-Postgres/MySQL בפריסה אמיתית - זו כל הנקודה בהפרדת repository/session)."""
from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from server.config import settings

_connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

if settings.database_url.startswith("sqlite:///"):
    db_path = Path(settings.database_url.replace("sqlite:///", "", 1))
    db_path.parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(settings.database_url, connect_args=_connect_args, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_db_session():
    """FastAPI dependency: פותחת session ומבטיחה סגירה תמיד (גם בשגיאה)."""
    session: Session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
