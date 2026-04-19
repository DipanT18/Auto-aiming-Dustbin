"""Tests for motor_control/serial_comm.py"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from motor_control.serial_comm import SerialComm


@patch("motor_control.serial_comm.serial.Serial")
def test_connect_and_ping(mock_serial_cls):
    mock_ser = MagicMock()
    mock_ser.readline.return_value = b"OK PONG\n"
    mock_serial_cls.return_value = mock_ser

    comm = SerialComm({"port": "/dev/null", "baud_rate": 115200})
    comm.connect()
    reply = comm.ping()
    assert "PONG" in reply
    comm.close()


@patch("motor_control.serial_comm.serial.Serial")
def test_move_command(mock_serial_cls):
    mock_ser = MagicMock()
    mock_serial_cls.return_value = mock_ser

    comm = SerialComm({"port": "/dev/null", "baud_rate": 115200})
    comm.connect()
    comm.move(100, -50)
    written = b"".join(call.args[0] for call in mock_ser.write.call_args_list)
    assert b"MOVE 100 -50" in written
    comm.close()


@patch("motor_control.serial_comm.serial.Serial")
def test_stop_command(mock_serial_cls):
    mock_ser = MagicMock()
    mock_serial_cls.return_value = mock_ser

    comm = SerialComm({"port": "/dev/null", "baud_rate": 115200})
    comm.connect()
    comm.stop()
    written = b"".join(call.args[0] for call in mock_ser.write.call_args_list)
    assert b"STOP" in written
    comm.close()


@patch("motor_control.serial_comm.serial.Serial")
def test_move_clamps_to_255(mock_serial_cls):
    mock_ser = MagicMock()
    mock_serial_cls.return_value = mock_ser

    comm = SerialComm({"port": "/dev/null"})
    comm.connect()
    comm.move(500, -600)
    written = b"".join(call.args[0] for call in mock_ser.write.call_args_list)
    assert b"MOVE 255 -255" in written
    comm.close()
