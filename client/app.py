"""
FocusSessionApp - ה-composition root של צד הלקוח: מרכיב את כל הרכיבים
(מצלמה, זיהוי פנים, כיול, ניקוד, רשת, לוגר, UI) ומריץ את לולאת הווידאו
הראשית. זה מחליף את הפונקציה הענקית main() שהייתה בקובץ המקורי.
"""
from __future__ import annotations

import logging
import threading
import time
from typing import Optional, Sequence

import cv2

from client.config import ClientSettings
from client.core.calibration import Calibrator
from client.core.camera_capture import CameraCapture, CameraError, CameraSettings
from client.core.validators import sanitize_student_name
from client.core.virtual_camera import create_virtual_camera
from client.networking.api_client import ScoreApiClient
from client.networking.models import ScoreSubmission
from client.scoring.config import ScoringConfig
from client.scoring.decorators.movement_penalty import MovementPenaltyDecorator
from client.scoring.evaluator_factory import build_default_focus_evaluator
from client.scoring.score_engine import ScoreEngine
from client.session_logging.data_logger import DataLogger
from client.ui.input_handler import InputHandler
from client.ui.overlay_renderer import (
    draw_calibration_overlay, draw_recording_status, draw_score_overlay, score_color,
)
from client.vision.face_mesh_detector import FaceMeshDetector
from client.vision.feature_extractor import FaceFeatureExtractor

logger = logging.getLogger(__name__)

WINDOW_TITLE = "Student Focus Analytics"


class FocusSessionApp:
    """מריצה סשן ריכוז שלם עבור תלמידה אחת: וידאו -> כיול -> ניקוד -> UI + רשת."""

    def __init__(self, settings: ClientSettings, student_name: str) -> None:
        self._settings = settings
        self._student_name = sanitize_student_name(student_name)

        self._camera = CameraCapture(CameraSettings(
            device_index=settings.camera_index, width=settings.camera_width,
            height=settings.camera_height, fps=settings.camera_fps,
        ))
        self._feature_extractor = FaceFeatureExtractor()
        self._calibrator = Calibrator()

        scoring_config = ScoringConfig()
        evaluator = build_default_focus_evaluator(scoring_config)
        self._score_engine = ScoreEngine(evaluator, scoring_config)
        self._movement_probe = _find_movement_decorator(evaluator)

        self._api_client = ScoreApiClient(
            server_url=settings.server_url, api_key=settings.api_key,
            timeout_seconds=settings.request_timeout_seconds,
        )
        self._data_logger = DataLogger(settings.logs_dir, self._student_name)

        self._input_handler = InputHandler()
        self._input_handler.bind("r", self._data_logger.toggle_recording)
        self._input_handler.bind("1", lambda: self._data_logger.set_label(1))
        self._input_handler.bind("0", lambda: self._data_logger.set_label(0))

        self._img_w = 0
        self._img_h = 0
        self._last_send_time = 0.0
        self._last_log_time = 0.0
        self._last_frame_time = 0.0

    def run(self) -> None:
        print("=" * 50)
        print(f"מעולה {self._student_name}, שלב כיול קצר של 3 שניות יתחיל מיד...")
        print("=" * 50)

        try:
            self._img_w, self._img_h = self._camera.open()
        except CameraError as exc:
            print(f"שגיאה: {exc}")
            return

        virtual_cam = create_virtual_camera(self._img_w, self._img_h, fps=self._settings.camera_fps)
        if virtual_cam.is_active:
            print(f"✅ מצלמה וירטואלית מחוברת בהצלחה: {virtual_cam.device_name}")
        else:
            print("⚠️ אזהרה: לא נמצא דרייבר למצלמה וירטואלית (לא Unity ולא OBS).")

        now = time.time()
        self._last_send_time = now
        self._last_log_time = now
        self._last_frame_time = now

        with FaceMeshDetector() as detector:
            try:
                while True:
                    ok, frame = self._camera.read()
                    if not ok or frame is None:
                        break

                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    virtual_cam.send(frame_rgb)

                    now = time.time()
                    dt = now - self._last_frame_time
                    self._last_frame_time = now

                    landmarks = detector.process(frame_rgb)
                    if landmarks is not None:
                        self._process_face(frame, detector, landmarks, dt, now)

                    cv2.imshow(WINDOW_TITLE, frame)
                    if self._input_handler.poll():
                        break
            finally:
                virtual_cam.close()
                self._camera.release()
                cv2.destroyAllWindows()

    def _process_face(self, frame, detector: FaceMeshDetector, landmarks, dt: float, now: float) -> None:
        features = self._feature_extractor.extract(landmarks, self._img_w, self._img_h)

        if not self._calibrator.is_calibrated:
            self._calibrator.add_sample(features, dt)
            detector.draw(frame, color=(0, 255, 255))
            draw_calibration_overlay(frame, self._calibrator.remaining_seconds)
            if self._calibrator.is_calibrated:
                self._last_send_time = now
                self._last_log_time = now
                print(f"✅ כיול הושלם! EAR בסיס: {self._calibrator.baseline_ear:.2f}")
            return

        calibrated = self._calibrator.calibrate_frame(features)
        result = self._score_engine.update(calibrated)

        if now - self._last_send_time > self._settings.send_interval_seconds:
            self._send_score_async(result.score, result.reasons)
            self._last_send_time = now

        if now - self._last_log_time > self._settings.log_interval_seconds:
            self._data_logger.log_data(
                self._student_name, result.score,
                calibrated.delta_ear, calibrated.adjusted_yaw, calibrated.adjusted_roll, features.pitch,
            )
            self._last_log_time = now

        color = score_color(result.score)
        detector.draw(frame, color=color)

        displayed_score = int(5 * round(result.score / 5))
        seconds_moving = self._movement_probe.seconds_moving if self._movement_probe else 0.0
        draw_score_overlay(
            frame, displayed_score, color,
            delta_yaw=calibrated.adjusted_yaw, delta_ear=calibrated.delta_ear, mar=calibrated.mar,
            seconds_moving=seconds_moving, active_reasons=result.reasons,
        )
        draw_recording_status(frame, self._data_logger.is_recording, self._data_logger.current_label)

    def _send_score_async(self, score: float, reasons: Sequence[str]) -> None:
        submission = ScoreSubmission(
            student_id=self._student_name, focus_score=int(score), reasons=list(reasons),
        )
        threading.Thread(target=self._api_client.submit_score, args=(submission,), daemon=True).start()


def _find_movement_decorator(evaluator) -> Optional[MovementPenaltyDecorator]:
    """עוזר קטן לתצוגה בלבד: מאתר את ה-MovementPenaltyDecorator בשרשרת כדי
    להציג את טיימר התזוזה על המסך (שימוש תצוגתי בלבד, לא משפיע על הניקוד)."""
    current = evaluator
    while current is not None:
        if isinstance(current, MovementPenaltyDecorator):
            return current
        current = getattr(current, "_wrapped", None)
    return None
