"""חישוב מרחק תזוזת האף בין פריימים, לזיהוי חוסר שקט (fidgeting)."""
from __future__ import annotations

import math
from typing import Optional

from client.vision.landmark_types import Point2D


def calculate_movement_distance(current_nose: Point2D, prev_nose: Optional[Point2D]) -> float:
    """מרחק אוקלידי בפיקסלים בין מיקום האף בפריים הנוכחי לקודם."""
    if prev_nose is None:
        return 0.0
    return math.hypot(current_nose[0] - prev_nose[0], current_nose[1] - prev_nose[1])
