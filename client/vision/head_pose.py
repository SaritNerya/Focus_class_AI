"""
הערכת פוזת הראש (pitch, yaw, roll) מתוך 6 נקודות ציון של הפנים,
בעזרת solvePnP (ללא כיול מצלמה אמיתי - קירוב סביר עבור מצלמת web רגילה).
"""
from __future__ import annotations

from typing import NamedTuple, Sequence

import cv2
import numpy as np

from client.vision.landmark_types import Landmark

# נקודות המודל התלת-ממדי הגנרי של הפנים (יחידות שרירותיות, לא ס"מ אמיתיים)
_MODEL_POINTS = np.array([
    (0.0, 0.0, 0.0),
    (0.0, -330.0, -65.0),
    (-225.0, 170.0, -135.0),
    (225.0, 170.0, -135.0),
    (-150.0, -150.0, -125.0),
    (150.0, -150.0, -125.0),
])

# אינדקסים של MediaPipe FaceMesh: אף, סנטר, פינת עין שמאל, פינת עין ימין, פינת פה שמאל/ימין
_POSE_LANDMARK_INDICES = (1, 152, 33, 263, 61, 291)


class HeadPose(NamedTuple):
    pitch: float
    yaw: float
    roll: float


def calculate_head_pose(landmarks: Sequence[Landmark], img_w: int, img_h: int) -> HeadPose:
    """
    מחזירה זווית pitch/yaw/roll משוערת של הראש.

    הערה על יציבות: הערכת פוזה מ-6 נקודות בלבד (בלי כיול מצלמה אמיתי) ידועה
    כרגישה לרעש, במיוחד ב-roll כאשר ה-yaw גדול. ההגנה מפני כך (clamp, floor,
    EMA smoothing) ממוקמת במכוון בשכבת הניקוד (client/scoring) ולא כאן, כדי
    שמודול זה יישאר עוסק אך ורק בגאומטריה הגולמית.
    """
    image_points = np.array(
        [(landmarks[i].x * img_w, landmarks[i].y * img_h) for i in _POSE_LANDMARK_INDICES],
        dtype="double",
    )

    focal_length = img_w
    center = (img_w / 2, img_h / 2)
    camera_matrix = np.array(
        [[focal_length, 0, center[0]],
         [0, focal_length, center[1]],
         [0, 0, 1]],
        dtype="double",
    )
    dist_coeffs = np.zeros((4, 1))

    success, rotation_vector, _translation_vector = cv2.solvePnP(
        _MODEL_POINTS, image_points, camera_matrix, dist_coeffs,
        flags=cv2.SOLVEPNP_ITERATIVE,
    )
    if not success:
        return HeadPose(pitch=0.0, yaw=0.0, roll=0.0)

    rotation_matrix, _ = cv2.Rodrigues(rotation_vector)
    angles, *_ = cv2.RQDecomp3x3(rotation_matrix)

    return HeadPose(pitch=angles[0], yaw=angles[1], roll=angles[2])
