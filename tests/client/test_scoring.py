"""
בדיקות ליבת הניקוד - ממחישות למה תבנית ה-Decorator כל כך שימושית כאן:
אפשר לבדוק כל decorator בבידוד מוחלט, בלי מצלמה, בלי Mediapipe, ובלי שאר
השרשרת.
"""
from __future__ import annotations

from client.core.calibration import CalibratedFeatures
from client.scoring.base import BaseEvaluator
from client.scoring.config import ScoringConfig
from client.scoring.decorators.eyes_closed_penalty import EyesClosedPenaltyDecorator
from client.scoring.decorators.movement_penalty import MovementPenaltyDecorator
from client.scoring.evaluator_factory import build_default_focus_evaluator
from client.scoring.score_engine import ScoreEngine


def _features(**overrides) -> CalibratedFeatures:
    defaults = dict(
        avg_ear=0.30, delta_ear=0.0, adjusted_yaw=0.0, adjusted_roll=0.0,
        tilt_magnitude=0.0, mar=0.1, nose_pos=(100.0, 100.0), ear_threshold=0.2,
    )
    defaults.update(overrides)
    return CalibratedFeatures(**defaults)


def test_base_evaluator_never_penalizes():
    evaluator = BaseEvaluator()
    verdict = evaluator.evaluate(_features())
    assert verdict.target_ceiling == 100.0
    assert verdict.reasons == ()
    assert verdict.is_violating is False


def test_eyes_closed_decorator_penalizes_after_threshold():
    config = ScoringConfig(frames_blink_threshold=2, assumed_fps=10.0)
    evaluator = EyesClosedPenaltyDecorator(BaseEvaluator(), config)

    closed = _features(avg_ear=0.05, ear_threshold=0.2)
    for _ in range(5):
        verdict = evaluator.evaluate(closed)

    assert verdict.target_ceiling < 100.0
    assert "Eyes closed too long" in verdict.reasons


def test_decorator_chain_combines_worst_penalty():
    config = ScoringConfig(frames_blink_threshold=1, assumed_fps=10.0, movement_threshold_px=1.0)
    evaluator = build_default_focus_evaluator(config)

    # עיניים סגורות לאורך זמן -> ציון נמוך; שום עונש אחר לא אמור "לרפא" אותו
    closed_still = _features(avg_ear=0.05, ear_threshold=0.2, nose_pos=(100.0, 100.0))
    verdict = None
    for _ in range(20):
        verdict = evaluator.evaluate(closed_still)

    assert verdict.target_ceiling < 100.0


def test_score_engine_recovers_gradually_when_no_violation():
    config = ScoringConfig(assumed_fps=10.0, normal_recovery_rate=5.0)
    evaluator = MovementPenaltyDecorator(BaseEvaluator(), config)
    engine = ScoreEngine(evaluator, config)
    engine.score = 50.0

    result = engine.update(_features(nose_pos=(100.0, 100.0)))

    assert result.score > 50.0  # מתחיל לטפס בהיעדר הפרה
    assert result.score <= 100.0
