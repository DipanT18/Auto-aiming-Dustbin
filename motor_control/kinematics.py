"""Omni-wheel inverse kinematics.

Four omni-wheels arranged at 90° intervals (each wheel rotated 45° from the
platform axis) allow motion in any direction without yawing the chassis.

Wheel layout (top view):

         Front
    [W1] ←—→ [W2]
       ↑  +Y  ↑
       |  (fwd)|
       |       |
    [W4] ←—→ [W3]
         Rear
    +X →

Each wheel axis is diagonal to the platform.  The kinematic mixing matrix
for this 4-wheel X-drive arrangement is::

    ω1 = +Vx - Vy - ωR
    ω2 = -Vx - Vy + ωR
    ω3 = -Vx + Vy - ωR      (not used — bin doesn't rotate)
    ω4 = +Vx + Vy + ωR

With rotation (ω=0), simplifies to:

    W1 = +Vx - Vy
    W2 = -Vx - Vy
    W3 = -Vx + Vy
    W4 = +Vx + Vy

All values are normalised to [-255, 255] (PWM range).
"""

from __future__ import annotations

from dataclasses import dataclass

_MAX_PWM = 255


@dataclass
class WheelSpeeds:
    """Signed PWM values for each wheel (range: -255 to 255)."""

    w1: int  # front-left
    w2: int  # front-right
    w3: int  # rear-right
    w4: int  # rear-left


def _norm_clamp(values: list[float]) -> list[int]:
    """Scale values so the maximum absolute value maps to *_MAX_PWM*."""
    max_abs = max(abs(v) for v in values) if values else 1.0
    if max_abs < 1e-6:
        return [0] * len(values)
    # Only scale down (never amplify); values already within range are unchanged.
    scale = min(1.0, _MAX_PWM / max_abs)
    return [int(round(v * scale)) for v in values]


def compute_wheel_speeds(vx: float, vy: float, omega: float = 0.0) -> WheelSpeeds:
    """
    Convert desired platform velocity to per-wheel PWM commands.

    Parameters
    ----------
    vx:
        Desired x-axis velocity (positive = right).  Units are arbitrary
        (pixels/s or m/s); values are scaled to the PWM range.
    vy:
        Desired y-axis velocity (positive = forward / up in image).
    omega:
        Rotational rate (rad/s, or arbitrary units).  Pass 0.0 to prevent
        chassis yaw (default).

    Returns
    -------
    WheelSpeeds with each value in [-255, 255].
    """
    r = float(omega)
    raw = [
        +vx - vy - r,  # W1 front-left
        -vx - vy + r,  # W2 front-right
        -vx + vy - r,  # W3 rear-right
        +vx + vy + r,  # W4 rear-left
    ]
    clamped = _norm_clamp(raw)
    return WheelSpeeds(w1=clamped[0], w2=clamped[1], w3=clamped[2], w4=clamped[3])


def pixel_error_to_velocity(
    ex: float,
    ey: float,
    gain: float = 0.5,
    max_speed: float = _MAX_PWM,
) -> tuple[float, float]:
    """
    Convert pixel error between current position and target to (vx, vy).

    Parameters
    ----------
    ex:
        Pixel error in X (target_x - current_x).
    ey:
        Pixel error in Y (target_y - current_y).
    gain:
        Proportional gain (pixels → PWM units).
    max_speed:
        Clip output to ±max_speed.

    Returns
    -------
    (vx, vy) in PWM units.
    """
    vx = max(-max_speed, min(max_speed, ex * gain))
    vy = max(-max_speed, min(max_speed, ey * gain))
    return (vx, vy)
