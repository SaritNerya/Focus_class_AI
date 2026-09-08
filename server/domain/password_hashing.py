"""
פונקציית hash סיסמה עצמאית, ללא תלות ב-server.config.

הופרדה במכוון למודול נפרד: server/scripts/generate_password_hash.py
צריך לייצר hash *לפני* שקובץ ה-.env מכיל DASHBOARD_PASSWORD_HASH תקין,
ואם היה מייבא דרך server.core.security (שדורש settings מלאים בזמן import),
היינו נתקלים בבעיית "ביצה ותרנגולת".
"""
from __future__ import annotations

from passlib.context import CryptContext

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    return _pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return _pwd_context.verify(plain_password, hashed_password)
