from __future__ import annotations

from fastapi import APIRouter

from server.api.v1 import dashboard, scores

api_router = APIRouter()
api_router.include_router(scores.router)
api_router.include_router(dashboard.router)
