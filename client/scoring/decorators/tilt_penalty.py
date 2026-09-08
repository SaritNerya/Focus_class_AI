"""עונש הטיית ראש / הסחת דעת ממושכת, עם הגבלת זווית ורמפ הדרגתי."""
from __future__ import annotations

from client.core.calibration import CalibratedFeatures
from client.scoring.base import FocusEvaluator, PenaltyDecorator, Verdict
from client.scoring.config import ScoringConfig


class TiltPenaltyDecorator(PenaltyDecorator):
    def __init__(self, wrapped: FocusEvaluator, config: ScoringConfig) -> None:
        super().__init__(wrapped)
        self._config = config
        self._distracted_frames = 0

    def _reset_self(self) -> None:
        self._distracted_frames = 0

    def _evaluate_self(self, features: CalibratedFeatures) -> Verdict:
        cfg = self._config
        is_distracted = features.tilt_magnitude > cfg.tilt_threshold_deg

        self._distracted_frames = self._distracted_frames + 1 if is_distracted else 0

        target = 100.0
        reasons: tuple[str, ...] = ()
        if self._distracted_frames >= cfg.frames_for_distracted:
            seconds_distracted = self._distracted_frames / cfg.assumed_fps
            clamped_magnitude = min(features.tilt_magnitude, cfg.tilt_clamp_angle_deg)
            ramp_factor = min(1.0, seconds_distracted / cfg.tilt_ramp_seconds)
            penalty = clamped_magnitude * ramp_factor
            target = max(cfg.tilt_floor_target, 100.0 - penalty)
            reasons = ("Head turned / tilted away",)

        is_severe = self._distracted_frames >= cfg.severe_tilt_seconds * cfg.assumed_fps
        return Verdict(target_ceiling=target, reasons=reasons, is_violating=is_distracted, is_severe=is_severe)
