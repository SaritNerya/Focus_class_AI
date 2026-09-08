"""
ScoreEngine - אחראי אך ורק על "מרדף אחר היעד" לאורך זמן: ירידה מיידית
לעונש, עלייה הדרגתית כשאין הפרה פעילה, ומצב "התאוששות איטית" אחרי אירוע
חמור. הלוגיקה הזו אורתוגונלית לשאלה אילו עונשים קיימים (זה תפקיד ה-
FocusEvaluator המעוטר) - הפרדת אחריות נקייה (SRP).
"""
from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass
from typing import Deque, List, Tuple

from client.core.calibration import CalibratedFeatures
from client.scoring.base import FocusEvaluator, Verdict
from client.scoring.config import ScoringConfig


@dataclass(frozen=True)
class ScoreResult:
    score: float
    reasons: Tuple[str, ...]


class ScoreEngine:
    def __init__(self, evaluator: FocusEvaluator, config: ScoringConfig) -> None:
        self._evaluator = evaluator
        self._config = config
        self.score = 100.0
        self._severe_recovery_active = False
        self._recovery_anchored = False
        self._score_history: Deque[Tuple[float, float]] = deque()

    def reset(self) -> None:
        self._evaluator.reset()
        self.score = 100.0
        self._severe_recovery_active = False
        self._recovery_anchored = False
        self._score_history.clear()

    def _rolling_average(self) -> float:
        if not self._score_history:
            return self.score
        return sum(s for _, s in self._score_history) / len(self._score_history)

    def update(self, features: CalibratedFeatures) -> ScoreResult:
        cfg = self._config
        verdict: Verdict = self._evaluator.evaluate(features)

        if verdict.is_severe and not self._severe_recovery_active:
            self._severe_recovery_active = True
            self._recovery_anchored = False

        if self.score > verdict.target_ceiling:
            # ירידה תמיד מיידית - אין "חסד" לעונשים
            self.score = verdict.target_ceiling
        elif self.score < verdict.target_ceiling and not verdict.is_violating:
            if self._severe_recovery_active:
                if not self._recovery_anchored:
                    # מעגנים פעם אחת לממוצע הדקה האחרונה, לא נמוך מהציון
                    # הנוכחי ולא גבוה מהיעד - כדי שהעלייה תהיה איטית ואמינה
                    avg = self._rolling_average()
                    self.score = max(self.score, min(avg, verdict.target_ceiling))
                    self._recovery_anchored = True
                self.score = min(verdict.target_ceiling, self.score + cfg.slow_recovery_rate)
            else:
                self.score = min(verdict.target_ceiling, self.score + cfg.normal_recovery_rate)

        self.score = max(0.0, min(100.0, self.score))

        if self.score >= 100.0 - 1e-6:
            self._severe_recovery_active = False
            self._recovery_anchored = False

        now = time.time()
        self._score_history.append((now, self.score))
        while self._score_history and now - self._score_history[0][0] > cfg.rolling_window_seconds:
            self._score_history.popleft()

        return ScoreResult(score=self.score, reasons=verdict.reasons)
