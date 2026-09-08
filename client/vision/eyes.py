"""
חישוב מדד EAR (Eye Aspect Ratio) לזיהוי עצימת/מצמוץ עיניים.

מודול זה עוסק אך ורק במתמטיקה של נקודות הציון (Single Responsibility) -
אין כאן שום תלות במצלמה, בניקוד או ברשת.
"""
from __future__ import annotations

import math
from typing import Sequence

from client.vision.landmark_types import Landmark, Point2D


def euclidean_distance(p1: Point2D, p2: Point2D) -> float:
    """מרחק אוקלידי בין שתי נקודות דו-ממדיות."""
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])


def calculate_ear(landmarks: Sequence[Landmark], eye_indices: Sequence[int]) -> float:
    """
    מחשבת את מדד ה-EAR (Eye Aspect Ratio) לזיהוי עיניים עצומות.

    Args:
        landmarks: כל נקודות הציון של הפנים (מ-MediaPipe).
        eye_indices: 6 אינדקסים של נקודת העין [p1..p6] בסדר הסטנדרטי.

    Returns:
        ערך EAR - ככל שקטן יותר, העין עצומה יותר.
    """
    if len(eye_indices) != 6:
        raise ValueError("calculate_ear מצפה בדיוק ל-6 אינדקסים של נקודות עין")

    p1, p2, p3, p4, p5, p6 = (landmarks[i] for i in eye_indices)

    vertical_1 = euclidean_distance((p2.x, p2.y), (p6.x, p6.y))
    vertical_2 = euclidean_distance((p3.x, p3.y), (p5.x, p5.y))
    horizontal = euclidean_distance((p1.x, p1.y), (p4.x, p4.y))

    if horizontal == 0:
        return 0.0

    return (vertical_1 + vertical_2) / (2.0 * horizontal)
