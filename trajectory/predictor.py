"""Parabola-fitting trajectory predictor.

Given a rolling window of (time, cx, cy) pixel samples, fits a quadratic
to the vertical (cy) axis and a linear model to the horizontal (cx) axis,
then predicts the pixel coordinates at a configurable future time or at
a specified floor row.
"""

from __future__ import annotations

import logging
from collections import deque
from dataclasses import dataclass
from typing import Any

import numpy as np

from .utils import solve_quadratic

logger = logging.getLogger(__name__)


@dataclass
class Sample:
    t: float
    cx: float
    cy: float


class TrajectoryPredictor:
    """
    Fit a parabola to the recent vertical pixel trajectory and extrapolate
    to a target row (floor level) to predict the landing coordinates.

    Usage::

        predictor = TrajectoryPredictor(history=8, floor_row=480)
        predictor.add(t, cx, cy)
        result = predictor.predict()   # (x_land, y_land) or None
    """

    def __init__(
        self,
        history: int = 8,
        floor_row: float = 480.0,
        horizon_s: float = 0.35,
        min_samples: int = 3,
    ) -> None:
        self._buf: deque[Sample] = deque(maxlen=history)
        self._floor_row = floor_row
        self._horizon_s = horizon_s
        self._min_samples = max(3, min_samples)

    @classmethod
    def from_config(cls, cfg: dict[str, Any]) -> TrajectoryPredictor:
        return cls(
            history=int(cfg.get("history", 8)),
            floor_row=float(cfg.get("floor_row", 480.0)),
            horizon_s=float(cfg.get("horizon_s", 0.35)),
            min_samples=int(cfg.get("min_samples", 3)),
        )

    def add(self, t: float, cx: float, cy: float) -> None:
        """Append a centroid sample (time in seconds, pixel coords)."""
        self._buf.append(Sample(t=t, cx=cx, cy=cy))

    def reset(self) -> None:
        """Clear all stored samples."""
        self._buf.clear()

    def predict(self) -> tuple[float, float] | None:
        """
        Predict landing coordinates.

        Returns ``(x_land, y_land)`` pixels, or ``None`` if there is
        insufficient history to fit the model.
        """
        if len(self._buf) < self._min_samples:
            return None

        samples = list(self._buf)
        t0 = samples[0].t
        ts = np.array([s.t - t0 for s in samples])
        xs = np.array([s.cx for s in samples])
        ys = np.array([s.cy for s in samples])

        # Fit quadratic to Y (gravity acts along cy in a top-view tilted
        # camera, or directly in a side-view camera).
        try:
            y_coeffs = np.polyfit(ts, ys, 2)
        except np.linalg.LinAlgError:
            logger.warning("polyfit failed for Y axis")
            return None

        # Fit linear to X (no gravity component in horizontal).
        try:
            x_coeffs = np.polyfit(ts, xs, 1)
        except np.linalg.LinAlgError:
            logger.warning("polyfit failed for X axis")
            return None

        a, b, c = float(y_coeffs[0]), float(y_coeffs[1]), float(y_coeffs[2])

        # Solve a*t^2 + b*t + (c - floor_row) = 0
        roots = solve_quadratic(a, b, c - self._floor_row)
        if roots is None:
            # No real root — fall back to horizon-based prediction.
            t_last = samples[-1].t - t0
            t_pred = t_last + self._horizon_s
            x_land = float(np.polyval(x_coeffs, t_pred))
            y_land = float(np.polyval(y_coeffs, t_pred))
            return (x_land, y_land)

        t_now = samples[-1].t - t0
        # Pick the smallest future root; if none exist, use horizon-based fallback.
        future_roots = [r for r in roots if r > t_now]
        if not future_roots:
            t_pred = t_now + self._horizon_s
            x_land = float(np.polyval(x_coeffs, t_pred))
            y_land = float(np.polyval(y_coeffs, t_pred))
            return (x_land, y_land)
        t_land = min(future_roots)

        x_land = float(np.polyval(x_coeffs, t_land))
        y_land = self._floor_row
        return (x_land, y_land)

    def predict_at(self, t_future: float) -> tuple[float, float] | None:
        """Predict position at an absolute timestamp *t_future* (seconds)."""
        if len(self._buf) < self._min_samples:
            return None

        samples = list(self._buf)
        t0 = samples[0].t
        ts = np.array([s.t - t0 for s in samples])
        xs = np.array([s.cx for s in samples])
        ys = np.array([s.cy for s in samples])

        try:
            y_coeffs = np.polyfit(ts, ys, 2)
            x_coeffs = np.polyfit(ts, xs, 1)
        except np.linalg.LinAlgError:
            return None

        dt = t_future - t0
        return (float(np.polyval(x_coeffs, dt)), float(np.polyval(y_coeffs, dt)))
