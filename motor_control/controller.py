"""High-level motor controller.

Converts a predicted landing position to wheel commands and sends them
to the Arduino via :class:`~motor_control.serial_comm.SerialComm`.
"""

from __future__ import annotations

import logging
from typing import Any

from .kinematics import WheelSpeeds, compute_wheel_speeds, pixel_error_to_velocity
from .serial_comm import SerialComm

logger = logging.getLogger(__name__)


class MotorController:
    """
    Translate target pixel coordinates to motor commands.

    Parameters
    ----------
    serial_comm:
        Open :class:`SerialComm` instance (already connected).
    config:
        Optional dict with keys:

        ``center_x``, ``center_y`` — pixel origin of the platform centre.
        ``gain`` — proportional gain (pixels → PWM units).
        ``max_speed`` — maximum PWM value (default 255).
        ``deadband_px`` — ignore errors smaller than this (default 5).
    """

    def __init__(self, serial_comm: SerialComm, config: dict[str, Any] | None = None) -> None:
        self._comm = serial_comm
        cfg = config or {}
        self._center_x = float(cfg.get("center_x", 320.0))
        self._center_y = float(cfg.get("center_y", 240.0))
        self._gain = float(cfg.get("gain", 0.5))
        self._max_speed = float(cfg.get("max_speed", 255.0))
        self._deadband = float(cfg.get("deadband_px", 5.0))

    def move_to(self, target_x: float, target_y: float) -> WheelSpeeds:
        """
        Compute and send the MOVE command to aim the bin at (*target_x*, *target_y*).

        Returns the :class:`~motor_control.kinematics.WheelSpeeds` that were sent.
        """
        ex = target_x - self._center_x
        ey = target_y - self._center_y

        if abs(ex) < self._deadband and abs(ey) < self._deadband:
            logger.debug("Within deadband — STOP")
            self._comm.stop()
            return WheelSpeeds(0, 0, 0, 0)

        vx, vy = pixel_error_to_velocity(ex, ey, gain=self._gain, max_speed=self._max_speed)
        speeds = compute_wheel_speeds(vx, vy)
        self._comm.move(int(vx), int(vy))
        logger.debug("move_to(%.1f, %.1f) → vx=%d vy=%d", target_x, target_y, int(vx), int(vy))
        return speeds

    def stop(self) -> None:
        """Halt the platform immediately."""
        self._comm.stop()

    def update_center(self, cx: float, cy: float) -> None:
        """Update the platform's current estimated position in pixel space."""
        self._center_x = cx
        self._center_y = cy
