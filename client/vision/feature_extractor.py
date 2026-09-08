"""
Facade שמאחד את כל חישובי ה-vision הבודדים (EAR, MAR, פוזת ראש, תזוזה)
לכדי אובייקט FrameFeatures אחד לכל פריים - כדי ששאר האפליקציה לא תצטרך
להכיר את הפרטים הפנימיים (אינדקסים של נקודות ציון וכו').
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence

from client.vision.eyes import calculate_ear
from client.vision.head_pose import calculate_head_pose
from client.vision.landmark_types import Landmark, Point2D
from client.vision.mouth import calculate_mar

_LEFT_EYE_INDICES = (33, 160, 158, 133, 153, 144)
_RIGHT_EYE_INDICES = (362, 385, 387, 263, 373, 380)
_MOUTH_INDICES = (78, 308, 13, 14)
_NOSE_INDEX = 1


@dataclass(frozen=True)
class FrameFeatures:
    """תכונות גולמיות (לא-מכוילות) שחולצו מפריים בודד."""
    avg_ear: float
    mar: float
    pitch: float
    yaw: float
    roll: float
    nose_pos: Point2D


class FaceFeatureExtractor:
    """אחראית אך ורק על הפיכת נקודות ציון גולמיות ל-FrameFeatures."""

    def extract(self, landmarks: Sequence[Landmark], img_w: int, img_h: int) -> FrameFeatures:
        left_ear = calculate_ear(landmarks, _LEFT_EYE_INDICES)
        right_ear = calculate_ear(landmarks, _RIGHT_EYE_INDICES)
        avg_ear = (left_ear + right_ear) / 2.0

        mar = calculate_mar(landmarks, _MOUTH_INDICES)
        pitch, yaw, roll = calculate_head_pose(landmarks, img_w, img_h)

        nose = landmarks[_NOSE_INDEX]
        nose_pos: Point2D = (nose.x * img_w, nose.y * img_h)

        return FrameFeatures(
            avg_ear=avg_ear, mar=mar, pitch=pitch, yaw=yaw, roll=roll, nose_pos=nose_pos,
        )
