from __future__ import annotations

from vision.object_detection import Detection
from vision.trajectory_prediction import TrajectoryPredictor


def test_predict_requires_history():
    tr = TrajectoryPredictor(history=8, horizon_s=0.2)
    assert tr.predict_impact(0.0) is None


def test_constant_velocity_extrapolation():
    tr = TrajectoryPredictor(history=8, horizon_s=0.1)
    tr.update(0.0, Detection(0, 0, 10, 10))
    tr.update(0.1, Detection(10, 0, 10, 10))
    pred = tr.predict_impact(0.1)
    assert pred is not None
    cx, cy = pred
    assert cx > 10
    assert cy == 5.0
