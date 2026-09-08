"""
Rate limiting בסיסי (sliding window פר-IP, בזיכרון) - שכבת הגנה נוספת נגד
הצפה/ניסיונות brute-force על נתיבי ה-API, מעבר לאימות עצמו.
לא מיועד לתחליף למגן DDoS ברמת רשת אמיתי (למשל Cloudflare) בסביבת production
מרובת-שרתים, אלא כהגנה סבירה לשרת יחיד בסביבת כיתה.
"""
from __future__ import annotations

import time
from collections import defaultdict, deque
from typing import Deque, Dict

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_minute: int) -> None:
        super().__init__(app)
        self._limit = requests_per_minute
        self._window_seconds = 60.0
        self._hits: Dict[str, Deque[float]] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        hits = self._hits[client_ip]

        while hits and now - hits[0] > self._window_seconds:
            hits.popleft()

        if len(hits) >= self._limit:
            return JSONResponse(
                status_code=429,
                content={"status": "error", "message": "יותר מדי בקשות - נסי שוב בעוד רגע"},
            )

        hits.append(now)
        return await call_next(request)
