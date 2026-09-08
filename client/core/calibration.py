"""
כיול אישי: אוסף נתוני בסיס (baseline) בתחילת הסשן ומתרגם תכונות גולמיות
לתכונות "מכוילות" (deltas מהבסיס האישי + סף עיניים אישי).

הערה על תיקון ארכיטקטוני: בקוד המקורי היה כיול כפול ולא עקבי - main.py כייל
לפי מספר פריימים קבוע (90), ובנפרד FocusScorer כייל שוב לפי זמן (3 שניות) עם
סף EAR דינמי מבוסס סטיית תקן. שני הכיולים חפפו חלקית וסתרו אחד את השני.
כאן יש מקור אמת יחיד לכיול, המשמש את כל שאר האפליקציה.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from client.vision.feature_extractor import FrameFeatures
from client.vision.landmark_types import Point2D


@dataclass(frozen=True)
class CalibratedFeatures:
    """תכונות אחרי כיול: פערים (deltas) מהבסיס האישי + החלקה (EMA) לזוויות."""
    avg_ear: float
    delta_ear: float
    adjusted_yaw: float
    adjusted_roll: float
    tilt_magnitude: float
    mar: float
    nose_pos: Point2D
    ear_threshold: float


@dataclass
class CalibrationConfig:
    duration_seconds: float = 3.0
    ear_std_dev_multiplier: float = 2.0
    ear_threshold_min: float = 0.08
    ear_threshold_max: float = 0.30
    angle_smoothing_alpha: float = 0.4  # EMA - קטן יותר = החלקה חזקה יותר


class Calibrator:
    """
    שלב 1: אוסף מדגמים למשך duration_seconds.
    שלב 2: מחשב בסיס אישי (EAR, yaw, roll) וסף EAR דינמי.
    לאחר הכיול: מתרגם כל פריים חדש ל-CalibratedFeatures עם EMA smoothing.
    """

    def __init__(self, config: Optional[CalibrationConfig] = None) -> None:
        self._config = config or CalibrationConfig()
        self._samples: List[Tuple[float, float, float]] = []  # (ear, yaw, roll)
        self._elapsed_seconds = 0.0

        self.is_calibrated = False
        self.baseline_ear = 0.30
        self.baseline_yaw = 0.0
        self.baseline_roll = 0.0
        self.ear_threshold = 0.22

        self._smoothed_yaw: Optional[float] = None
        self._smoothed_roll: Optional[float] = None

    @property
    def remaining_seconds(self) -> float:
        return max(0.0, self._config.duration_seconds - self._elapsed_seconds)

    def add_sample(self, features: FrameFeatures, dt_seconds: float) -> None:
        """מוסיפה מדגם בזמן שלב הכיול. dt_seconds = זמן שחלף מהפריים הקודם."""
        if self.is_calibrated:
            return

        self._samples.append((features.avg_ear, features.yaw, features.roll))
        self._elapsed_seconds += dt_seconds

        if self._elapsed_seconds >= self._config.duration_seconds and self._samples:
            self._finalize_calibration()

    def _finalize_calibration(self) -> None:
        ear_values = [s[0] for s in self._samples]
        yaw_values = [s[1] for s in self._samples]
        roll_values = [s[2] for s in self._samples]

        n = len(self._samples)
        mean_ear = sum(ear_values) / n
        variance = sum((e - mean_ear) ** 2 for e in ear_values) / n
        std_ear = variance ** 0.5

        self.baseline_ear = mean_ear
        self.baseline_yaw = sum(yaw_values) / n
        self.baseline_roll = sum(roll_values) / n

        # סף אישי: ממוצע פחות 2 סטיות תקן, עם טווח בטיחות - מתאים את עצמו
        # לכל צורת עין, כולל עיניים צרות מהממוצע, בלי לכפות טווח אחיד לכולם.
        dynamic_threshold = mean_ear - self._config.ear_std_dev_multiplier * std_ear
        self.ear_threshold = max(
            self._config.ear_threshold_min,
            min(self._config.ear_threshold_max, dynamic_threshold),
        )
        self.is_calibrated = True

    def calibrate_frame(self, features: FrameFeatures) -> CalibratedFeatures:
        """מתרגמת פריים (אחרי שהכיול הושלם) לתכונות מכוילות עם EMA smoothing."""
        if not self.is_calibrated:
            raise RuntimeError("calibrate_frame נקראה לפני סיום שלב הכיול")

        alpha = self._config.angle_smoothing_alpha
        if self._smoothed_yaw is None:
            self._smoothed_yaw = features.yaw
            self._smoothed_roll = features.roll
        else:
            self._smoothed_yaw = alpha * features.yaw + (1 - alpha) * self._smoothed_yaw
            self._smoothed_roll = alpha * features.roll + (1 - alpha) * self._smoothed_roll

        adjusted_yaw = self._smoothed_yaw - self.baseline_yaw
        adjusted_roll = self._smoothed_roll - self.baseline_roll
        tilt_magnitude = (adjusted_yaw ** 2 + adjusted_roll ** 2) ** 0.5

        return CalibratedFeatures(
            avg_ear=features.avg_ear,
            delta_ear=features.avg_ear - self.baseline_ear,
            adjusted_yaw=adjusted_yaw,
            adjusted_roll=adjusted_roll,
            tilt_magnitude=tilt_magnitude,
            mar=features.mar,
            nose_pos=features.nose_pos,
            ear_threshold=self.ear_threshold,
        )
