"""
עטיפה דקה סביב MediaPipe FaceMesh.

זו נקודת התלות היחידה במדיהפייפ בכל שכבת ה-vision (Dependency Inversion) -
אם בעתיד נרצה להחליף ספריית זיהוי פנים, רק קובץ זה צריך להשתנות.
"""
from __future__ import annotations

from typing import List, Optional, Sequence, Tuple

import mediapipe as mp
import numpy as np

from client.vision.landmark_types import Landmark


class FaceMeshDetector:
    """מזהה נקודות ציון של פנים בפריים בודד, ומאפשר ציור שלהן."""

    def __init__(
        self,
        max_num_faces: int = 1,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
    ) -> None:
        self._mp_face_mesh = mp.solutions.face_mesh
        self._mp_drawing = mp.solutions.drawing_utils
        self._face_mesh = self._mp_face_mesh.FaceMesh(
            max_num_faces=max_num_faces,
            refine_landmarks=True,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )
        self._last_raw_landmarks = None

    def process(self, frame_rgb: np.ndarray) -> Optional[List[Landmark]]:
        """מחזיר את נקודות הציון של הפנים הראשונות שזוהו בפריים, או None.

        שומרת פנימית גם את האובייקט הגולמי (protobuf) לצורך draw(), כדי
        שהצרכנים החיצוניים יעבדו רק מול רשימת נקודות פשוטה וניתנת לאינדוקס.
        """
        results = self._face_mesh.process(frame_rgb)
        if not results.multi_face_landmarks:
            self._last_raw_landmarks = None
            return None
        raw = results.multi_face_landmarks[0]
        self._last_raw_landmarks = raw
        return raw.landmark

    def draw(self, frame: np.ndarray, color: Tuple[int, int, int]) -> None:
        """מצייר את קווי המתאר של הפנים (מהזיהוי האחרון) על גבי הפריים, in-place."""
        if self._last_raw_landmarks is None:
            return
        self._mp_drawing.draw_landmarks(
            image=frame,
            landmark_list=self._last_raw_landmarks,
            connections=self._mp_face_mesh.FACEMESH_CONTOURS,
            landmark_drawing_spec=None,
            connection_drawing_spec=self._mp_drawing.DrawingSpec(color=color, thickness=1, circle_radius=1),
        )

    def close(self) -> None:
        self._face_mesh.close()

    def __enter__(self) -> "FaceMeshDetector":
        return self

    def __exit__(self, *_exc_info) -> None:
        self.close()
