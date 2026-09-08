"""עונש תזוזת גוף (fidgeting) - עונש מדורג ורציף ללא קפיצות בין מדרגות."""
from __future__ import annotations

from client.core.calibration import CalibratedFeatures
from client.scoring.base import FocusEvaluator, PenaltyDecorator, Verdict
from client.scoring.config import ScoringConfig
from client.vision.movement import calculate_movement_distance


class MovementPenaltyDecorator(PenaltyDecorator):
    def __init__(self, wrapped: FocusEvaluator, config: ScoringConfig) -> None:
        super().__init__(wrapped)
        self._config = config
        self._movement_frames = 0.0
        self._prev_nose_pos = None

    @property
    def seconds_moving(self) -> float:
        return self._movement_frames / self._config.assumed_fps

    def _reset_self(self) -> None:
        self._movement_frames = 0.0
        self._prev_nose_pos = None

    @staticmethod
    def _penalty_for(seconds_moving: float) -> float:
        """
        עונש מדורג: 0-3ש' אין עונש, 3-5ש' 2 נק'/שנייה, 5-10ש' ממשיך מ-10 עד 20,
        10-15ש' ממשיך מ-20 עד 42, מעל 15ש' 2 נק' נוספות לכל שנייה.
        """
        if seconds_moving < 3.0:
            return 0.0
        if seconds_moving < 5.0:
            return 2.0 * seconds_moving
        if seconds_moving < 10.0:
            return 10.0 + 2.0 * (seconds_moving - 5.0)
        if seconds_moving < 15.0:
            return 20.0 + ((seconds_moving - 10.0) / 5.0) * 22.0
        return 42.0 + (seconds_moving - 15.0) * 2.0

    def _evaluate_self(self, features: CalibratedFeatures) -> Verdict:
        cfg = self._config
        distance_moved = calculate_movement_distance(features.nose_pos, self._prev_nose_pos)
        self._prev_nose_pos = features.nose_pos
        is_moving = distance_moved > cfg.movement_threshold_px

        if is_moving:
            self._movement_frames += 1
        else:
            self._movement_frames = max(0.0, self._movement_frames - cfg.movement_cooldown_step)

        penalty = self._penalty_for(self.seconds_moving)
        target = max(15.0, 100.0 - penalty)
        # להפרה "פעילה" (שחוסמת התאוששות) משתמשים במונה המצטבר עם סף grace קטן,
        # ולא בדגל is_moving הרגעי - כדי שפריים בודד רועש לא יחסום טיפוס למעלה.
        is_violating = self._movement_frames >= cfg.movement_violation_grace_frames

        reasons = ("Excessive movement",) if penalty > 0 else ()
        is_severe = self._movement_frames >= cfg.severe_movement_seconds * cfg.assumed_fps
        return Verdict(target_ceiling=target, reasons=reasons, is_violating=is_violating, is_severe=is_severe)
