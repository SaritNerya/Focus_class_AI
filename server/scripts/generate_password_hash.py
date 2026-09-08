"""
כלי עזר: מייצר bcrypt hash לסיסמת הדשבורד, כדי שלעולם לא תישמר סיסמה
בטקסט גלוי בקובץ ה-.env.

שימוש:
    python -m server.scripts.generate_password_hash
"""
from __future__ import annotations

import getpass

from server.domain.password_hashing import hash_password


def main() -> None:
    password = getpass.getpass("הקלידי את סיסמת הדשבורד הרצויה: ")
    confirm = getpass.getpass("אימות סיסמה: ")
    if password != confirm:
        print("הסיסמאות אינן תואמות.")
        return
    if len(password) < 8:
        print("מומלץ סיסמה של 8 תווים לפחות.")

    print("\nהוסיפי את השורה הבאה לקובץ server/.env:")
    print(f"DASHBOARD_PASSWORD_HASH={hash_password(password)}")


if __name__ == "__main__":
    main()
