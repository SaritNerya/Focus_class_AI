"""ראוטר דק - מקבל/מחזיר HTTP בלבד, כל הלוגיקה ב-ScoreService."""
from __future__ import annotations

from typing import Dict

from fastapi import APIRouter, Depends

from server.api.deps import get_score_service
from server.core.security import require_api_key, require_dashboard_auth
from server.domain.schemas import DashboardStudent, ScoreSubmission, ScoreSubmissionResponse
from server.services.score_service import ScoreService

router = APIRouter(prefix="/api/v1", tags=["scores"])


@router.post(
    "/scores",
    response_model=ScoreSubmissionResponse,
    dependencies=[Depends(require_api_key)],
    summary="קבלת עדכון ציון ריכוז מהלקוח (מוגן במפתח API)",
)
def submit_score(
    submission: ScoreSubmission, service: ScoreService = Depends(get_score_service),
) -> ScoreSubmissionResponse:
    service.submit_score(submission)
    return ScoreSubmissionResponse(status="success")


@router.get(
    "/scores",
    response_model=Dict[str, DashboardStudent],
    dependencies=[Depends(require_dashboard_auth)],
    summary="שליפת מצב כל התלמידות הפעילות (מוגן בסיסמת דשבורד)",
)
def get_scores(service: ScoreService = Depends(get_score_service)) -> Dict[str, DashboardStudent]:
    return service.get_dashboard_state()
