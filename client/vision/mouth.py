"""חישוב מדד MAR (Mouth Aspect Ratio) לזיהוי פיהוקים."""
from __future__ import annotations

from typing import Sequence

from client.vision.eyes import euclidean_distance
from client.vision.landmark_types import Landmark


def calculate_mar(landmarks: Sequence[Landmark], mouth_indices: Sequence[int]) -> float:
    """
    מחשבת את מדד ה-MAR לזיהוי פיהוקים.

    Args:
        landmarks: כל נקודות הציון של הפנים.
        mouth_indices: 4 אינדקסים בסדר [שמאל, ימין, למעלה, למטה] של חלל הפה הפנימי.
    """
    if len(mouth_indices) != 4:
        raise ValueError("calculate_mar מצפה בדיוק ל-4 אינדקסים")

    p_left, p_right, p_top, p_bottom = (landmarks[i] for i in mouth_indices)

    vertical_dist = euclidean_distance((p_top.x, p_top.y), (p_bottom.x, p_bottom.y))
    horizontal_dist = euclidean_distance((p_left.x, p_left.y), (p_right.x, p_right.y))

    if horizontal_dist == 0:
        return 0.0

    return vertical_dist / horizontal_dist
