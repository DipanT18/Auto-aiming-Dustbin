from __future__ import annotations

"""Integration-style tests for motor commands; uses mocked serial."""

from unittest.mock import MagicMock, patch

from vision.serial_controller import SerialController


@patch("vision.serial_controller.serial.Serial")
def test_movement_sequence(mock_serial_cls):
    mock_ser = MagicMock()
    mock_serial_cls.return_value = mock_ser

    ctrl = SerialController({"port": "/dev/ttyFAKE", "baud_rate": 115200})
    ctrl.connect()
    for delta in (5, -5, 20):
        ctrl.pan_steps(delta)
    ctrl.close()
    assert mock_ser.write.call_count >= 3
