"""בדיקות לפונקציות האבטחה הגרעיניות - אלה שאמורות לעולם לא להישבר."""
from __future__ import annotations

import secrets

from server.domain.password_hashing import hash_password


def test_hash_password_produces_verifiable_bcrypt_hash():
    from passlib.context import CryptContext

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    password = secrets.token_urlsafe(12)

    hashed = hash_password(password)

    assert hashed != password
    assert pwd_context.verify(password, hashed)
    assert not pwd_context.verify("wrong-password", hashed)


def test_student_id_validator_rejects_script_injection():
    from server.domain.schemas import ScoreSubmission
    import pytest

    with pytest.raises(ValueError):
        ScoreSubmission(student_id="<script>alert(1)</script>", focus_score=50)


def test_student_id_validator_accepts_hebrew_and_english_names():
    from server.domain.schemas import ScoreSubmission

    submission = ScoreSubmission(student_id="נועה כהן", focus_score=90)
    assert submission.student_id == "נועה כהן"
