"""נקודת הכניסה של השרת. הרצה: python -m server.main (מהתיקייה הראשית)."""
from __future__ import annotations

import uvicorn

from server.config import settings


def main() -> None:
    uvicorn.run(
        "server.app:create_app",
        factory=True,
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )


if __name__ == "__main__":
    main()
