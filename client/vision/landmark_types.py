"""
טיפוסים משותפים לשכבת ה-vision, כדי לא לקשור את כל המודולים ישירות
לטיפוס הפנימי של MediaPipe (Dependency Inversion - תלות בממשק מופשט
ולא במימוש קונקרטי של ספרייה חיצונית).
"""
from __future__ import annotations

from typing import Protocol, Tuple


class Landmark(Protocol):
    """כל אובייקט עם קואורדינטות x, y (ואופציונלית z) מתאים - למשל
    landmark של MediaPipe, בלי צורך לייבא את הספרייה כאן."""
    x: float
    y: float


Point2D = Tuple[float, float]
