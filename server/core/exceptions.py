"""חריגות ייעודיות לשכבת הדומיין/שירותים, כדי שראוטרים לא יזרקו HTTPException
ישירות (הפרדת שכבות - הדומיין לא אמור להכיר HTTP)."""
from __future__ import annotations

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse


class DomainError(Exception):
    """שגיאה עסקית כללית."""


class InvalidScoreSubmissionError(DomainError):
    """נתוני הגשת ציון אינם תקינים."""


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def _handle_domain_error(request: Request, exc: DomainError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"status": "error", "message": str(exc)},
        )

    @app.exception_handler(Exception)
    async def _handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        # לא חושפים פרטי implementation/stack trace ללקוח - רק ל-log השרת.
        app.state.logger.exception("Unhandled server error: %s", exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "error", "message": "אירעה שגיאה בלתי צפויה בשרת"},
        )
