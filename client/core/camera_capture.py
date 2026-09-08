"""עטיפה סביב cv2.VideoCapture - ניהול משאב המצלמה (context manager)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

import cv2
import numpy as np


@dataclass(frozen=True)
class CameraSettings:
    device_index: int = 0
    width: int = 640
    height: int = 480
    fps: int = 30


class CameraError(RuntimeError):
    """נזרקת כשלא ניתן לפתוח את המצלמה או לקרוא ממנה פריים ראשוני."""


class CameraCapture:
    def __init__(self, settings: CameraSettings) -> None:
        self._settings = settings
        self._cap: Optional[cv2.VideoCapture] = None

    def open(self) -> Tuple[int, int]:
        """פותחת את המצלמה, מחזירה (width, height) בפועל. זורקת CameraError בכשל."""
        self._cap = cv2.VideoCapture(self._settings.device_index)
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self._settings.width)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self._settings.height)
        self._cap.set(cv2.CAP_PROP_FPS, self._settings.fps)

        if not self._cap.isOpened():
            raise CameraError("לא ניתן לפתוח את המצלמה. ודאי שהיא לא בשימוש ע\"י תוכנה אחרת.")

        ok, first_frame = self._cap.read()
        if not ok:
            raise CameraError("לא הצלחתי לקרוא פריים ראשוני מהמצלמה.")

        height, width, _ = first_frame.shape
        return width, height

    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        if self._cap is None:
            raise CameraError("המצלמה לא נפתחה - יש לקרוא ל-open() תחילה.")
        return self._cap.read()

    def release(self) -> None:
        if self._cap is not None:
            self._cap.release()
            self._cap = None

    def __enter__(self) -> "CameraCapture":
        self.open()
        return self

    def __exit__(self, *_exc_info) -> None:
        self.release()
