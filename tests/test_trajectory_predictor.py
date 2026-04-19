"""Tests for trajectory/predictor.py"""

from __future__ import annotations

import pytest
from trajectory.predictor import TrajectoryPredictor


def test_predict_requires_min_samples():
    p = TrajectoryPredictor(history=8, floor_row=480, min_samples=3)
    assert p.predict() is None
    p.add(0.0, 100.0, 100.0)
    assert p.predict() is None
    p.add(0.1, 110.0, 130.0)
    assert p.predict() is None


def test_predict_returns_result_after_enough_samples():
    p = TrajectoryPredictor(history=8, floor_row=480, min_samples=3)
    # Simulate parabolic Y, linear X
    for i in range(5):
        t = i * 0.033
        cx = 100.0 + 20.0 * i
        cy = 100.0 + 50.0 * i + 30.0 * i * i
        p.add(t, cx, cy)
    result = p.predict()
    assert result is not None
    x_land, y_land = result
    assert isinstance(x_land, float)
    assert isinstance(y_land, (int, float))


def test_predict_at():
    p = TrajectoryPredictor(history=8, floor_row=480, min_samples=3)
    for i in range(4):
        t = i * 0.1
        p.add(t, float(i * 10), float(i * 5))
    result = p.predict_at(0.5)
    assert result is not None
    assert len(result) == 2


def test_reset_clears_buffer():
    p = TrajectoryPredictor()
    for i in range(5):
        p.add(float(i) * 0.1, float(i), float(i))
    p.reset()
    assert p.predict() is None
