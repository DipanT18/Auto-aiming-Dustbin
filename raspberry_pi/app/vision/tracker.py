"""Multi-frame object tracker.

Maintains a history of centroid positions and detects when an object
has landed (moved less than *landed_threshold_px* for *landed_patience*
consecutive frames).
"""

from __future__ import annotations

import logging
from collections import deque
from dataclasses import dataclass, field
from typing import Any

from .object_detection import Detection

logger = logging.getLogger(__name__)


@dataclass
class Track:
    """State for a single tracked object."""

    cx: float = 0.0
    cy: float = 0.0
    history: list[tuple[float, float]] = field(default_factory=list)
    frames_since_seen: int = 0
    is_active: bool = False
    landed: bool = False


class ObjectTracker:
    """
    Simple nearest-neighbour single-object tracker.

    Maintains position history across frames and exposes ``landed``
    once the object stops moving significantly.

    Parameters
    ----------
    max_history:
        Maximum number of (cx, cy) positions to keep.
    max_lost_frames:
        Frames without a detection before the track is dropped.
    landed_threshold_px:
        Pixel distance below which motion is considered "landed".
    landed_patience:
        Consecutive near-zero-motion frames required to declare landing.
    """

    def __init__(
        self,
        max_history: int = 30,
        max_lost_frames: int = 5,
        landed_threshold_px: float = 8.0,
        landed_patience: int = 3,
    ) -> None:
        self._max_history = max_history
        self._max_lost = max_lost_frames
        self._threshold = landed_threshold_px
        self._patience = landed_patience

        self._track: Track = Track()
        self._still_count: int = 0
        self._history: deque[tuple[float, float]] = deque(maxlen=max_history)

    @classmethod
    def from_config(cls, cfg: dict[str, Any]) -> ObjectTracker:
        return cls(
            max_history=int(cfg.get("max_history", 30)),
            max_lost_frames=int(cfg.get("max_lost_frames", 5)),
            landed_threshold_px=float(cfg.get("landed_threshold_px", 8.0)),
            landed_patience=int(cfg.get("landed_patience", 3)),
        )

    def update(self, det: Detection | None) -> Track:
        """
        Update tracker with the latest detection.

        Pass ``None`` when no detection is available this frame.
        Returns the current :class:`Track` state.
        """
        if det is None:
            self._track.frames_since_seen += 1
            if self._track.frames_since_seen > self._max_lost:
                self._reset()
            return self._track

        new_cx, new_cy = det.cx, det.cy

        if self._track.is_active:
            dx = new_cx - self._track.cx
            dy = new_cy - self._track.cy
            dist = (dx * dx + dy * dy) ** 0.5
            if dist < self._threshold:
                self._still_count += 1
            else:
                self._still_count = 0
            self._track.landed = self._still_count >= self._patience
        else:
            self._track.is_active = True
            self._still_count = 0

        self._track.cx = new_cx
        self._track.cy = new_cy
        self._track.frames_since_seen = 0
        self._history.append((new_cx, new_cy))
        self._track.history = list(self._history)
        return self._track

    def _reset(self) -> None:
        self._track = Track()
        self._still_count = 0
        self._history.clear()

    def reset(self) -> None:
        """Manually reset the tracker (e.g. between throws)."""
        self._reset()

    @property
    def history(self) -> list[tuple[float, float]]:
        """Recent centroid positions as a list of (cx, cy) tuples."""
        return list(self._history)

    @property
    def landed(self) -> bool:
        """``True`` once the tracked object appears to have stopped."""
        return self._track.landed
