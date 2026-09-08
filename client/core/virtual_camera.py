"""
מצלמה וירטואלית: תבנית Strategy (בחירת backend בזמן ריצה) + Null Object
(NullVirtualCamera) כדי שקוד הצריכה לא יצטרך תנאי has_vcam בכל מקום.
"""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import List, Optional

import numpy as np
import pyvirtualcam

logger = logging.getLogger(__name__)


class VirtualCamera(ABC):
    @abstractmethod
    def send(self, frame_rgb: np.ndarray) -> None: ...

    @abstractmethod
    def close(self) -> None: ...

    @property
    @abstractmethod
    def is_active(self) -> bool: ...

    @property
    def device_name(self) -> str:
        return "none"


class NullVirtualCamera(VirtualCamera):
    """Null Object: משמשת כשלא נמצא דרייבר תואם - אין צורך בבדיקות if בקוד הקורא."""

    def send(self, frame_rgb: np.ndarray) -> None:
        return None

    def close(self) -> None:
        return None

    @property
    def is_active(self) -> bool:
        return False


class _PyVirtualCamAdapter(VirtualCamera):
    def __init__(self, camera: "pyvirtualcam.Camera") -> None:
        self._camera = camera

    def send(self, frame_rgb: np.ndarray) -> None:
        self._camera.send(frame_rgb)

    def close(self) -> None:
        self._camera.close()

    @property
    def is_active(self) -> bool:
        return True

    @property
    def device_name(self) -> str:
        return self._camera.device


def create_virtual_camera(
    width: int, height: int, fps: int = 30, backends: Optional[List[str]] = None,
) -> VirtualCamera:
    """
    מנסה ליצור מצלמה וירטואלית לפי סדר עדיפות של backends (Strategy).
    אם אף אחד לא זמין, מחזירה NullVirtualCamera (Null Object) - קוד הצריכה
    תמיד מקבל אובייקט תקין עם ממשק אחיד, בלי לבדוק None.
    """
    for backend in backends or ["unitycapture", "obs"]:
        try:
            camera = pyvirtualcam.Camera(width=width, height=height, fps=fps, backend=backend)
            logger.info("Virtual camera connected via backend '%s': %s", backend, camera.device)
            return _PyVirtualCamAdapter(camera)
        except Exception as exc:  # noqa: BLE001 - backend availability check, expected to fail often
            logger.debug("Virtual camera backend '%s' unavailable: %s", backend, exc)

    logger.warning("No virtual camera driver found (tried: %s)", backends)
    return NullVirtualCamera()
