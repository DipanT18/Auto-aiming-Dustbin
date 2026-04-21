from __future__ import annotations

from unittest.mock import MagicMock, patch

from vision.serial_controller import SerialController


@patch("vision.serial_controller.serial.Serial")
def test_serial_connect_and_ping(mock_serial_cls):
    mock_ser = MagicMock()
    mock_ser.readline.return_value = b"OK PONG\n"
    mock_serial_cls.return_value = mock_ser

    ctrl = SerialController({"port": "/dev/null", "baud_rate": 115200})
    ctrl.connect()
    reply = ctrl.ping()
    assert "PONG" in reply
    mock_ser.write.assert_called()
    ctrl.close()


@patch("vision.serial_controller.serial.Serial")
def test_pan_tilt_commands(mock_serial_cls):
    mock_ser = MagicMock()
    mock_serial_cls.return_value = mock_ser

    ctrl = SerialController({"port": "/dev/null", "baud_rate": 115200})
    ctrl.connect()
    ctrl.pan_steps(10)
    ctrl.tilt_steps(-3)
    written = b"".join(call.args[0] for call in mock_ser.write.call_args_list)
    assert b"P 10" in written
    assert b"T -3" in written
    ctrl.close()
