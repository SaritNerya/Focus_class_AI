"""
לקוח HTTP לשליחת ציוני ריכוז לשרת המרצה.

אבטחה: כל בקשה נשלחת עם מפתח API בכותרת Authorization (Bearer token) -
המפתח משותף מראש בין הלקוח לשרת (דרך משתני סביבה), כדי שהשרת יוכל לדחות
בקשות מזויפות. הבקשה תמיד עם timeout קצר כדי לא לתקוע את לולאת הווידאו.
"""
from __future__ import annotations

import logging

import requests

from client.networking.models import ScoreSubmission

logger = logging.getLogger(__name__)


class ScoreApiClient:
    def __init__(self, server_url: str, api_key: str, timeout_seconds: float = 2.0) -> None:
        if not api_key:
            raise ValueError("API_KEY לא הוגדר - יש להגדיר אותו בקובץ ה-.env של הלקוח")
        self._endpoint = server_url.rstrip("/") + "/api/v1/scores"
        self._timeout_seconds = timeout_seconds
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        })

    def submit_score(self, submission: ScoreSubmission) -> None:
        """שולחת ציון לשרת. כשלים ברשת מנוטרלים בשקט (לא קריטי לחוויית הלקוח),
        אך נרשמים ל-log כדי שיהיה ניתן לאבחן תקלות."""
        try:
            response = self._session.post(
                self._endpoint, json=submission.to_json_dict(), timeout=self._timeout_seconds,
            )
            if response.status_code == 401:
                logger.error("השרת דחה את מפתח ה-API - בדקי שהוא תואם בין הלקוח לשרת.")
            elif not response.ok:
                logger.warning("שליחת ציון נכשלה: HTTP %s", response.status_code)
        except requests.RequestException as exc:
            logger.debug("שגיאת רשת בשליחת ציון (מתעלמים, לא חוסם את הווידאו): %s", exc)
