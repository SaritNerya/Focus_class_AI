"""
הגדרות השרת - נטענות ממשתני סביבה / קובץ .env בלבד (12-factor app).
אף סוד (מפתח API, סיסמה, hash) לא נמצא hardcoded בקוד המקור - זו דרישת
אבטחה בסיסית שמאפשרת גם לסובב (rotate) סודות בלי לשנות קוד.
"""
from __future__ import annotations

from pathlib import Path
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

_PROJECT_ROOT = Path(__file__).resolve().parent


class ServerSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(_PROJECT_ROOT / ".env"), extra="ignore")

    # --- כללי ---
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False

    # --- אבטחה ---
    api_key: str = Field(..., min_length=16, description="מפתח משותף בין הלקוחות לשרת")
    dashboard_username: str = Field(..., min_length=1)
    dashboard_password_hash: str = Field(..., min_length=1, description="bcrypt hash, ראו server/scripts/generate_password_hash.py")
    cors_origins_raw: str = Field(default="", alias="CORS_ORIGINS")
    rate_limit_requests_per_minute: int = 120

    # --- נתונים ---
    database_url: str = f"sqlite:///{_PROJECT_ROOT / 'data' / 'focusclass.db'}"
    student_timeout_seconds: float = 7.0

    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins_raw.split(",") if origin.strip()]


settings = ServerSettings()
