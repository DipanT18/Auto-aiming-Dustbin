from __future__ import annotations

from collections import deque
from dataclasses import dataclass

from .object_detection import Detection


@dataclass
class TrajectoryPoint:
    t: float
    cx: float
    cy: float


class TrajectoryPredictor:
    """
    Simple 2D constant-velocity extrapolation from recent centroid samples.
    Times are in seconds (monotonic clock from caller).
    """

    def __init__(self, history: int = 8, horizon_s: float = 0.35) -> None:
        self._buf: deque[TrajectoryPoint] = deque(maxlen=history)
        self._horizon_s = horizon_s

    def update(self, t: float, det: Detection | None) -> None:
        if det is None:
            return
        self._buf.append(TrajectoryPoint(t=t, cx=det.cx, cy=det.cy))

    def predict_impact(self, t_now: float) -> tuple[float, float] | None:
        if len(self._buf) < 2:
            return None
        p0 = self._buf[-2]
        p1 = self._buf[-1]
        dt = p1.t - p0.t
        if dt <= 1e-6:
            return None
        vx = (p1.cx - p0.cx) / dt
        vy = (p1.cy - p0.cy) / dt
        dt_pred = self._horizon_s
        return (p1.cx + vx * dt_pred, p1.cy + vy * dt_pred)
