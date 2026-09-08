"""ראוטר הדשבורד - מגיש את דף ה-HTML הסטטי (מוגן בסיסמה)."""
from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse

from server.core.security import require_dashboard_auth

router = APIRouter(tags=["dashboard"])

_TEMPLATE_PATH = Path(__file__).resolve().parent.parent.parent / "templates" / "dashboard.html"


@router.get("/", response_class=HTMLResponse, dependencies=[Depends(require_dashboard_auth)])
def dashboard() -> str:
    return _TEMPLATE_PATH.read_text(encoding="utf-8")
