"""
תבנית עיצוב Decorator - הליבה של מנוע הניקוד.

FocusEvaluator הוא ה-Component המופשט. BaseEvaluator הוא ה-Concrete Component
(אינו מטיל שום עונש). כל PenaltyDecorator עוטף Evaluator קיים ומוסיף עליו
"שכבת עונש" אחת - כך שאפשר להרכיב שרשרת של עונשים ולהוסיף עונש חדש בעתיד
פשוט ע"י כתיבת מחלקה חדשה שיורשת מ-PenaltyDecorator, בלי לגעת בקוד קיים
(עיקרון Open/Closed).
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Tuple

from client.core.calibration import CalibratedFeatures


@dataclass(frozen=True)
class Verdict:
    """תוצאת הערכה של רכיב ניקוד אחד (או שרשרת שלמה) עבור פריים בודד."""
    target_ceiling: float = 100.0          # "תקרת" הציון שהרכיב הזה מאפשר
    reasons: Tuple[str, ...] = field(default_factory=tuple)
    is_violating: bool = False             # האם יש הפרה פעילה כרגע (חוסם התאוששות)
    is_severe: bool = False                # האם זהו אירוע חמור -> יפעיל התאוששות איטית


class FocusEvaluator(ABC):
    """ה-Component המופשט בתבנית ה-Decorator."""

    @abstractmethod
    def evaluate(self, features: CalibratedFeatures) -> Verdict:
        """מעריכה פריים בודד ומחזירה Verdict (לא שומרת ציון מצטבר - זה תפקיד ScoreEngine)."""
        raise NotImplementedError

    def reset(self) -> None:
        """איפוס מצב פנימי (למשל תחילת סשן חדש). ברירת מחדל: אין מצב לאפס."""
        return None


class BaseEvaluator(FocusEvaluator):
    """ה-Concrete Component: תמיד מחזיר 100 ללא עונשים - נקודת ההתחלה לעיטוף."""

    def evaluate(self, features: CalibratedFeatures) -> Verdict:
        return Verdict()


class PenaltyDecorator(FocusEvaluator, ABC):
    """
    Decorator בסיסי משותף לכל העונשים.

    מחלקות יורשות צריכות לממש רק את _evaluate_self (הלוגיקה הספציפית שלהן),
    וה-decorator כבר דואג למזג את התוצאה עם זו של הרכיב העטוף:
    - target_ceiling: המינימום (העונש המחמיר ביותר "מנצח")
    - reasons: איחוד הרשימות
    - is_violating: OR לוגי
    """

    def __init__(self, wrapped: FocusEvaluator) -> None:
        self._wrapped = wrapped

    def reset(self) -> None:
        self._wrapped.reset()
        self._reset_self()

    def _reset_self(self) -> None:
        return None

    @abstractmethod
    def _evaluate_self(self, features: CalibratedFeatures) -> Verdict:
        raise NotImplementedError

    def evaluate(self, features: CalibratedFeatures) -> Verdict:
        inner = self._wrapped.evaluate(features)
        own = self._evaluate_self(features)

        return Verdict(
            target_ceiling=min(inner.target_ceiling, own.target_ceiling),
            reasons=inner.reasons + own.reasons,
            is_violating=inner.is_violating or own.is_violating,
            is_severe=inner.is_severe or own.is_severe,
        )
