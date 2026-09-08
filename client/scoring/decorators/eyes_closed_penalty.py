"""עונש עצימת עיניים ממושכת (לא כולל מצמוץ רגיל)."""
from __future__ import annotations

from client.core.calibration import CalibratedFeatures
from client.scoring.base import FocusEvaluator, PenaltyDecorator, Verdict
from client.scoring.config import ScoringConfig


class EyesClosedPenaltyDecorator(PenaltyDecorator):
    def __init__(self, wrapped: FocusEvaluator, config: ScoringConfig) -> None:
        super().__init__(wrapped)
        self._config = config
        self._closed_eyes_frames = 0

    def _reset_self(self) -> None:
        self._closed_eyes_frames = 0

    def _evaluate_self(self, features: CalibratedFeatures) -> Verdict:
        cfg = self._config
        is_eyes_closed = features.avg_ear < features.ear_threshold
        # בזמן פיהוק העיניים נוטות להיראות "עצומות" מדדית (MAR גבוה, גיאומטריית
        # הפנים משתנה) - לכן לא סופרים זאת כעצימת עיניים, כדי לא לכפול-להעניש
        # על אותו אירוע (ראה גם YawnPenaltyDecorator).
        is_yawning = features.mar > cfg.mar_threshold

        if is_yawning:
            self._closed_eyes_frames = 0
        elif is_eyes_closed:
            self._closed_eyes_frames += 1
        else:
            self._closed_eyes_frames = 0

        target = 100.0
        reasons: tuple[str, ...] = ()
        if self._closed_eyes_frames > cfg.frames_blink_threshold:
            seconds_closed = self._closed_eyes_frames / cfg.assumed_fps
            penalty = seconds_closed * cfg.eye_penalty_per_second
            target = 100.0 - penalty
            reasons = ("Eyes closed too long",)

        is_severe = self._closed_eyes_frames >= cfg.severe_eyes_closed_seconds * cfg.assumed_fps
        return Verdict(target_ceiling=target, reasons=reasons, is_violating=is_eyes_closed, is_severe=is_severe)
