"""
Factory לבניית שרשרת ה-Decorator.

זו נקודת ההרחבה המרכזית: כדי להוסיף עונש חדש (למשל "מבט לצד המסך" או
"שימוש בטלפון") - כותבים מחלקת Decorator חדשה תחת client/scoring/decorators,
ומוסיפים שורה אחת כאן. אין צורך לגעת ב-ScoreEngine או בשאר האפליקציה.
"""
from __future__ import annotations

from client.scoring.base import BaseEvaluator, FocusEvaluator
from client.scoring.config import ScoringConfig
from client.scoring.decorators.eyes_closed_penalty import EyesClosedPenaltyDecorator
from client.scoring.decorators.movement_penalty import MovementPenaltyDecorator
from client.scoring.decorators.tilt_penalty import TiltPenaltyDecorator
from client.scoring.decorators.yawn_penalty import YawnPenaltyDecorator


def build_default_focus_evaluator(config: ScoringConfig) -> FocusEvaluator:
    """מרכיבה את שרשרת העונשים הסטנדרטית של FocusClass."""
    evaluator: FocusEvaluator = BaseEvaluator()
    evaluator = MovementPenaltyDecorator(evaluator, config)
    evaluator = EyesClosedPenaltyDecorator(evaluator, config)
    evaluator = TiltPenaltyDecorator(evaluator, config)
    evaluator = YawnPenaltyDecorator(evaluator, config)
    return evaluator
