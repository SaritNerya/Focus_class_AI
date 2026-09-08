"""
כל קבועי הניקוד במקום אחד - מוזרק ל-decorators ול-ScoreEngine, כדי שלא
יהיו "מספרי קסם" מפוזרים בקוד, ושיהיה קל לכייל את האלגוריתם או לכתוב לו
בדיקות (Dependency Injection במקום global constants).
"""
from __future__ import annotations

from dataclasses import dataclass

ASSUMED_FPS = 30.0


@dataclass(frozen=True)
class ScoringConfig:
    # --- תזוזה (fidgeting) ---
    movement_threshold_px: float = 8.0
    movement_violation_grace_frames: int = 3
    movement_cooldown_step: float = 1.5  # קירור מהיר כשחוזרים לשקט

    # --- עיניים עצומות ---
    frames_blink_threshold: int = 15
    eye_penalty_per_second: float = 10.0

    # --- הטיית ראש / הסחת דעת ---
    tilt_threshold_deg: float = 20.0
    frames_for_distracted: int = 30
    tilt_clamp_angle_deg: float = 60.0
    tilt_floor_target: float = 20.0
    tilt_ramp_seconds: float = 1.0

    # --- פיהוק ---
    mar_threshold: float = 0.5
    frames_for_yawn: int = 15
    yawn_max_penalty: float = 30.0
    yawn_ramp_frames: int = 15

    # --- אירוע חמור -> התאוששות איטית ---
    severe_movement_seconds: float = 10.0
    severe_eyes_closed_seconds: float = 10.0
    severe_tilt_seconds: float = 7.0
    slow_recovery_rate: float = 0.5
    normal_recovery_rate: float = 2.0
    rolling_window_seconds: float = 60.0

    assumed_fps: float = ASSUMED_FPS
