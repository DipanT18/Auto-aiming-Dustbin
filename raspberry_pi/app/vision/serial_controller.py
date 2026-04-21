from __future__ import annotations

import logging
import time
from typing import Any

import serial

logger = logging.getLogger(__name__)


class SerialController:
    """Send text commands to the Arduino (see docs/COMMUNICATION_PROTOCOL.md)."""

    def __init__(self, config: dict[str, Any]) -> None:
        self._port = config.get("port", "/dev/ttyUSB0")
        self._baud = int(config.get("baud_rate", 115200))
        self._timeout = float(config.get("timeout", 1.0))
        self._ser: serial.Serial | None = None

    def connect(self) -> None:
        self._ser = serial.Serial(self._port, self._baud, timeout=self._timeout)
        time.sleep(2.0)

    def close(self) -> None:
        if self._ser is not None:
            self._ser.close()
            self._ser = None

    def _write_line(self, line: str) -> None:
        if self._ser is None:
            raise RuntimeError("Serial not connected")
        data = (line.rstrip() + "\n").encode("ascii", errors="ignore")
        self._ser.write(data)
        self._ser.flush()

    def ping(self) -> str:
        self._write_line("PING")
        if self._ser is None:
            return ""
        return self._ser.readline().decode("ascii", errors="ignore").strip()

    def pan_steps(self, steps: int) -> None:
        self._write_line(f"P {int(steps)}")

    def tilt_steps(self, steps: int) -> None:
        self._write_line(f"T {int(steps)}")

    def __enter__(self) -> SerialController:
        self.connect()
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
