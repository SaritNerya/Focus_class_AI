"""עונש פיהוק, עם רמפ הדרגתי במקום קפיצה ישירה."""
from __future__ import annotations

from client.core.calibration import CalibratedFeatures
from client.scoring.base import FocusEvaluator, PenaltyDecorator, Verdict
from client.scoring.config import ScoringConfig


class YawnPenaltyDecorator(PenaltyDecorator):
    def __init__(self, wrapped: FocusEvaluator, config: ScoringConfig) -> None:
        super().__init__(wrapped)
        self._config = config
        self._yawn_frames = 0

    def _reset_self(self) -> None:
        self._yawn_frames = 0

    def _evaluate_self(self, features: CalibratedFeatures) -> Verdict:
        cfg = self._config
        is_yawning = features.mar > cfg.mar_threshold
        self._yawn_frames = self._yawn_frames + 1 if is_yawning else 0

        target = 100.0
        reasons: tuple[str, ...] = ()
        if self._yawn_frames >= cfg.frames_for_yawn:
            ramp_progress = min(1.0, (self._yawn_frames - cfg.frames_for_yawn) / cfg.yawn_ramp_frames)
            penalty = cfg.yawn_max_penalty * ramp_progress
            target = 100.0 - penalty
            reasons = ("Yawning",)

        return Verdict(target_ceiling=target, reasons=reasons, is_violating=is_yawning)
