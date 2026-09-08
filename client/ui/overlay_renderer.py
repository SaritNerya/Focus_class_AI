"""ציור שכבת המידע (HUD) על גבי פריים הווידאו - מופרד מהלוגיקה העסקית (SRP)."""
from __future__ import annotations

from typing import Sequence, Tuple

import cv2
import numpy as np

Color = Tuple[int, int, int]

_GREEN: Color = (0, 255, 0)
_ORANGE: Color = (0, 165, 255)
_RED: Color = (0, 0, 255)
_WHITE: Color = (255, 255, 255)
_YELLOW: Color = (0, 255, 255)


def score_color(score: float) -> Color:
    if score >= 80:
        return _GREEN
    if score >= 50:
        return _ORANGE
    return _RED


def draw_calibration_overlay(frame: np.ndarray, remaining_seconds: float) -> None:
    cv2.putText(frame, f"Calibrating... {remaining_seconds:.1f}s", (20, 60),
                cv2.FONT_HERSHEY_DUPLEX, 1.2, _YELLOW, 2)
    cv2.putText(frame, "Please look straight at the screen", (20, 100),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, _WHITE, 2)


def draw_score_overlay(
    frame: np.ndarray, displayed_score: int, color: Color,
    delta_yaw: float, delta_ear: float, mar: float, seconds_moving: float,
    active_reasons: Sequence[str],
) -> None:
    img_h, img_w = frame.shape[:2]

    cv2.putText(frame, f"Focus Score: {displayed_score}%", (20, 60),
                cv2.FONT_HERSHEY_DUPLEX, 1.3, color, 2)
    cv2.putText(frame, f"Yaw Delta: {delta_yaw:.1f}", (20, 100),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, _WHITE, 2)
    cv2.putText(frame, f"EAR Delta: {delta_ear:.2f} | MAR: {mar:.2f}", (20, 130),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, _WHITE, 2)
    cv2.putText(frame, f"Move Timer: {seconds_moving:.1f}s", (20, 170),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, _WHITE, 2)

    if seconds_moving > 5.0:
        cv2.putText(frame, "TOO MUCH MOVEMENT!", (20, 200),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, _ORANGE, 3)

    reasons_y = 230
    for reason_text in active_reasons:
        cv2.putText(frame, reason_text, (20, reasons_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, _RED, 2)
        reasons_y += 30

    _ = img_w  # שמור לשימוש עתידי (מיקום יחסי לרוחב המסך)


def draw_recording_status(frame: np.ndarray, is_recording: bool, current_label: int) -> None:
    if not is_recording:
        return
    img_h, img_w = frame.shape[:2]
    label_str = "Focused (1)" if current_label == 1 else "Distracted (0)"
    cv2.putText(frame, f"REC: ON | Label: {label_str}", (img_w - 350, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, _RED, 2)
    cv2.putText(frame, "Press '1' / '0' to change label", (img_w - 350, 70),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, _WHITE, 1)
