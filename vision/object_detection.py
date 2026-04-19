from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

import cv2
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class Detection:
    """Bounding box in pixel coordinates (x, y, w, h)."""

    x: int
    y: int
    w: int
    h: int
    label: str = "object"
    score: float = 1.0

    @property
    def cx(self) -> float:
        return self.x + self.w / 2.0

    @property
    def cy(self) -> float:
        return self.y + self.h / 2.0


class ObjectDetector:
    """
    Lightweight motion / color-based detection for prototyping.
    Swap in YOLO/MediaPipe later via the same interface.
    """

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self._cfg = config or {}
        self._prev_gray: np.ndarray | None = None
        self._blur = int(self._cfg.get("blur", 5)) | 1
        self._min_area = float(self._cfg.get("min_area", 400.0))
        self._thresh = int(self._cfg.get("motion_threshold", 25))

    def detect(self, frame_bgr: np.ndarray) -> list[Detection]:
        gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (self._blur, self._blur), 0)
        if self._prev_gray is None:
            self._prev_gray = gray
            return []

        diff = cv2.absdiff(gray, self._prev_gray)
        self._prev_gray = gray
        _, mask = cv2.threshold(diff, self._thresh, 255, cv2.THRESH_BINARY)
        mask = cv2.dilate(mask, None, iterations=2)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        out: list[Detection] = []
        for c in contours:
            area = cv2.contourArea(c)
            if area < self._min_area:
                continue
            x, y, w, h = cv2.boundingRect(c)
            out.append(Detection(x=x, y=y, w=w, h=h, label="motion", score=min(1.0, area / 5000.0)))
        return out
