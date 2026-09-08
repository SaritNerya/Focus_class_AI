"""נקודת הכניסה של צד הלקוח (התלמידה). קובץ דק בכוונה - כל הלוגיקה ב-app.py."""
from __future__ import annotations

import logging
import sys

from client.app import FocusSessionApp
from client.config import settings
from client.core.validators import InvalidStudentNameError

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


def main() -> None:
    print("=" * 50)
    raw_name = input("ברוכה הבאה! אנא הקלידי את שמך המלא ולחצי Enter: ")

    try:
        app = FocusSessionApp(settings, raw_name)
    except InvalidStudentNameError as exc:
        print(f"שגיאה: {exc}")
        sys.exit(1)
    except ValueError as exc:
        # למשל API_KEY חסר בקובץ ה-.env
        print(f"שגיאת הגדרות: {exc}")
        sys.exit(1)

    app.run()


if __name__ == "__main__":
    main()
