"""ניהול קיצורי מקלדת - ממפה מקש לפעולה, כדי לא לפזר if/elif בלולאה הראשית."""
from __future__ import annotations

from typing import Callable, Dict

import cv2

QUIT_KEY = ord("q")


class InputHandler:
    def __init__(self) -> None:
        self._bindings: Dict[int, Callable[[], None]] = {}

    def bind(self, key: str, callback: Callable[[], None]) -> None:
        self._bindings[ord(key)] = callback

    def poll(self, wait_ms: int = 1) -> bool:
        """קוראת מקש שנלחץ ומפעילה את הפעולה המתאימה. מחזירה True אם צריך לצאת."""
        key = cv2.waitKey(wait_ms) & 0xFF
        if key == QUIT_KEY:
            return True
        callback = self._bindings.get(key)
        if callback is not None:
            callback()
        return False
