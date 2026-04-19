"""Serial communication with the Arduino motor controller.

The protocol is line-oriented ASCII over USB serial (115200 baud default).
See docs/COMMUNICATION_PROTOCOL.md and arduino/README.md for the full spec.

Commands sent by this module:

    MOVE <vx> <vy>      — drive omni-wheel platform (signed integers, -255..255)
    STOP                — halt all motors immediately
    HOME                — return to origin (if firmware supports it)
    PING                — health check; Arduino replies with "OK PONG"

Responses from Arduino:

    OK                  — command acknowledged
    OK PONG             — reply to PING
    ERR <code>          — error from firmware
"""

from __future__ import annotations

import logging
import time
from typing import Any

import serial

logger = logging.getLogger(__name__)

_CONNECT_SETTLE_S = 2.0  # time to let the Arduino reset after DTR pulse


class SerialComm:
    """USB serial bridge to the Arduino motor controller."""

    def __init__(self, config: dict[str, Any]) -> None:
        self._port = config.get("port", "/dev/ttyUSB0")
        self._baud = int(config.get("baud_rate", 115200))
        self._timeout = float(config.get("timeout", 1.0))
        self._ser: serial.Serial | None = None

    # ------------------------------------------------------------------
    # Connection lifecycle
    # ------------------------------------------------------------------

    def connect(self) -> None:
        """Open the serial port and wait for the Arduino to boot."""
        self._ser = serial.Serial(self._port, self._baud, timeout=self._timeout)
        time.sleep(_CONNECT_SETTLE_S)
        logger.info("Serial connected: %s @ %d baud", self._port, self._baud)

    def close(self) -> None:
        """Close the serial port."""
        if self._ser is not None:
            self._ser.close()
            self._ser = None
            logger.info("Serial closed")

    def is_connected(self) -> bool:
        return self._ser is not None and self._ser.is_open

    # ------------------------------------------------------------------
    # Low-level I/O
    # ------------------------------------------------------------------

    def _write(self, line: str) -> None:
        if self._ser is None:
            raise RuntimeError("Serial not connected; call connect() first")
        data = (line.rstrip() + "\n").encode("ascii", errors="ignore")
        self._ser.write(data)
        self._ser.flush()

    def _readline(self) -> str:
        if self._ser is None:
            return ""
        return self._ser.readline().decode("ascii", errors="ignore").strip()

    # ------------------------------------------------------------------
    # Commands
    # ------------------------------------------------------------------

    def ping(self) -> str:
        """Send PING and return the raw response line."""
        self._write("PING")
        reply = self._readline()
        logger.debug("PING -> %r", reply)
        return reply

    def move(self, vx: int, vy: int) -> None:
        """
        Command the platform to move at velocity (*vx*, *vy*).

        Values are signed integers in the range -255 to 255 (PWM duty cycle
        equivalent).  Positive vx = move right, positive vy = move forward.
        """
        vx = int(max(-255, min(255, vx)))
        vy = int(max(-255, min(255, vy)))
        self._write(f"MOVE {vx} {vy}")
        logger.debug("MOVE %d %d", vx, vy)

    def stop(self) -> None:
        """Send STOP to halt all motors."""
        self._write("STOP")
        logger.debug("STOP")

    def home(self) -> None:
        """Send HOME to return to the origin position."""
        self._write("HOME")
        logger.debug("HOME")

    # ------------------------------------------------------------------
    # Context manager
    # ------------------------------------------------------------------

    def __enter__(self) -> SerialComm:
        self.connect()
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
