from __future__ import annotations

from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from vision.camera_feed import CameraConfig, CameraFeed


def test_camera_config_from_dict():
    c = CameraConfig.from_dict({"index": 1, "width": 320, "height": 240, "fps": 30.0})
    assert c.index == 1
    assert c.width == 320
    assert c.height == 240
    assert c.fps == 30.0


@patch("vision.camera_feed.cv2.VideoCapture")
def test_camera_read(mock_cap_cls):
    mock_cap = MagicMock()
    mock_cap.isOpened.return_value = True
    mock_cap.read.return_value = (True, np.zeros((480, 640, 3), dtype=np.uint8))
    mock_cap_cls.return_value = mock_cap

    feed = CameraFeed(CameraConfig(index=0))
    feed.open()
    ok, frame = feed.read()
    assert ok
    assert frame.shape == (480, 640, 3)
    feed.close()


@patch("vision.camera_feed.cv2.VideoCapture")
def test_camera_open_failure(mock_cap_cls):
    mock_cap = MagicMock()
    mock_cap.isOpened.return_value = False
    mock_cap_cls.return_value = mock_cap

    feed = CameraFeed(CameraConfig(index=99))
    with pytest.raises(RuntimeError):
        feed.open()
