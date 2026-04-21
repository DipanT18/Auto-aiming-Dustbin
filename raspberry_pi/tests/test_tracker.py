"""Tests for vision/tracker.py"""

from __future__ import annotations

import pytest

from vision.object_detection import Detection
from vision.tracker import ObjectTracker


def test_tracker_initial_state():
    t = ObjectTracker()
    track = t.update(None)
    assert not track.is_active
    assert not track.landed


def test_tracker_activates_on_detection():
    t = ObjectTracker()
    det = Detection(x=45, y=45, w=10, h=10)
    track = t.update(det)
    assert track.is_active
    assert track.cx == pytest.approx(50.0)


def test_tracker_landed_detection():
    t = ObjectTracker(landed_threshold_px=20.0, landed_patience=3)
    # Object barely moves — should be detected as landed after 3 frames
    for i in range(5):
        det = Detection(x=98 + i % 2, y=98, w=4, h=4)
        track = t.update(det)
    assert track.landed


def test_tracker_reset():
    t = ObjectTracker()
    det = Detection(x=0, y=0, w=10, h=10)
    t.update(det)
    t.reset()
    assert t.history == []


def test_tracker_drops_after_max_lost():
    t = ObjectTracker(max_lost_frames=2)
    det = Detection(x=100, y=100, w=10, h=10)
    t.update(det)  # activate
    for _ in range(3):
        track = t.update(None)  # lost frames
    assert not track.is_active
