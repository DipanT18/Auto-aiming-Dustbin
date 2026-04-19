from __future__ import annotations

import numpy as np

from vision.object_detection import ObjectDetector


def test_detector_warms_up():
    det = ObjectDetector({"min_area": 10, "motion_threshold": 10})
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    assert det.detect(frame) == []
    assert det.detect(frame) == []


def test_motion_blob():
    det = ObjectDetector({"min_area": 50, "motion_threshold": 5, "blur": 3})
    a = np.zeros((120, 160, 3), dtype=np.uint8)
    b = a.copy()
    b[40:80, 50:100] = 255
    det.detect(a)
    dets = det.detect(b)
    assert len(dets) >= 1
    assert dets[0].w > 0 and dets[0].h > 0
