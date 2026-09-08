"""
אבטחה בצד השרת:

1. require_api_key - מגן על נתיב הגשת הציונים (/api/v1/scores POST) בעזרת
   מפתח API משותף שנשלח בכותרת Authorization: Bearer <key>. משווים בעזרת
   secrets.compare_digest כדי למנוע Timing Attack.

2. require_dashboard_auth - מגן על הדשבורד ועל שליפת הציונים (GET) בעזרת
   HTTP Basic Auth. הסיסמה נשמרת כ-bcrypt hash בלבד (לעולם לא בטקסט גלוי),
   וההשוואה מתבצעת דרך passlib (constant-time באופן פנימי).
"""
from __future__ import annotations

import secrets
from typing import Optional

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from server.config import ServerSettings, settings
from server.domain.password_hashing import verify_password

_basic_auth = HTTPBasic()


def _extract_bearer_token(authorization_header: Optional[str]) -> Optional[str]:
    if not authorization_header:
        return None
    parts = authorization_header.split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    return parts[1]


def require_api_key(
    authorization: Optional[str] = Header(default=None),
    app_settings: ServerSettings = Depends(lambda: settings),
) -> None:
    """Dependency: מוודאת שהבקשה נושאת מפתח API תקין. נועדה למנוע שליחת
    ציונים מזויפים ע"י גורם שאינו קוד הלקוח הרשמי."""
    token = _extract_bearer_token(authorization)
    if not token or not secrets.compare_digest(token, app_settings.api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="מפתח API חסר או שגוי",
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_dashboard_auth(
    credentials: HTTPBasicCredentials = Depends(_basic_auth),
    app_settings: ServerSettings = Depends(lambda: settings),
) -> str:
    """Dependency: מגנה על הדשבורד/API בסיסמה. משתמשת ב-compare_digest גם
    על שם המשתמש כדי למנוע user enumeration דרך timing, ובאימות bcrypt
    (constant-time) על הסיסמה."""
    is_username_correct = secrets.compare_digest(
        credentials.username.encode("utf-8"), app_settings.dashboard_username.encode("utf-8"),
    )
    is_password_correct = verify_password(credentials.password, app_settings.dashboard_password_hash)

    if not (is_username_correct and is_password_correct):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="שם משתמש או סיסמה שגויים",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username
