"""
הגדרות הלקוח - נטענות ממשתני סביבה / קובץ .env, ולא hardcoded בקוד.
זהו עיקרון אבטחה בסיסי: אין להטמיע מפתחות סודיים (כמו API_KEY) בקוד המקור.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

_PROJECT_ROOT = Path(__file__).resolve().parent
load_dotenv(_PROJECT_ROOT / ".env")


def _env_float(name: str, default: float) -> float:
    try:
        return float(os.environ.get(name, default))
    except ValueError:
        return default


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, default))
    except ValueError:
        return default


@dataclass(frozen=True)
class ClientSettings:
    server_url: str = os.environ.get("SERVER_URL", "http://127.0.0.1:8000")
    api_key: str = os.environ.get("API_KEY", "")

    camera_index: int = _env_int("CAMERA_INDEX", 0)
    camera_width: int = _env_int("CAMERA_WIDTH", 640)
    camera_height: int = _env_int("CAMERA_HEIGHT", 480)
    camera_fps: int = _env_int("CAMERA_FPS", 30)

    send_interval_seconds: float = _env_float("SEND_INTERVAL_SECONDS", 1.0)
    log_interval_seconds: float = _env_float("LOG_INTERVAL_SECONDS", 0.5)
    request_timeout_seconds: float = _env_float("REQUEST_TIMEOUT_SECONDS", 2.0)

    logs_dir: Path = _PROJECT_ROOT / "data" / "logs"


settings = ClientSettings()
