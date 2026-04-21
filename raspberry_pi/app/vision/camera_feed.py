from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

import cv2
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class CameraConfig:
    index: int = 0
    width: int = 640
    height: int = 480
    fps: float | None = None

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> CameraConfig:
        return cls(
            index=int(d.get("index", 0)),
            width=int(d.get("width", 640)),
            height=int(d.get("height", 480)),
            fps=d.get("fps"),
        )


class CameraFeed:
    """OpenCV-backed camera capture with simple frame iteration."""

    def __init__(self, config: CameraConfig | dict[str, Any]) -> None:
        if isinstance(config, dict):
            self._cfg = CameraConfig.from_dict(config)
        else:
            self._cfg = config
        self._cap: cv2.VideoCapture | None = None

    def open(self) -> None:
        self._cap = cv2.VideoCapture(self._cfg.index)
        if not self._cap.isOpened():
            raise RuntimeError(f"Cannot open camera index {self._cfg.index}")
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self._cfg.width)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self._cfg.height)
        if self._cfg.fps is not None:
            self._cap.set(cv2.CAP_PROP_FPS, float(self._cfg.fps))

    def close(self) -> None:
        if self._cap is not None:
            self._cap.release()
            self._cap = None

    def read(self) -> tuple[bool, np.ndarray]:
        if self._cap is None:
            raise RuntimeError("Camera not opened")
        return self._cap.read()

    def frames(self):
        """Yield BGR frames until read fails."""
        while True:
            ok, frame = self.read()
            if not ok:
                break
            yield frame

    def __enter__(self) -> CameraFeed:
        self.open()
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
