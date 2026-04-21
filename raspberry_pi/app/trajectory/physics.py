"""Physics constants and kinematic helpers used by the trajectory predictor."""

from __future__ import annotations

# Standard gravitational acceleration (m/s²)
GRAVITY = 9.81

# Pixels-per-cm ratio placeholder; set by camera calibration.
# A top-down camera at 2 m height covering a ~2 m × 1.5 m floor area at
# 640×480 resolution gives roughly 32 px/cm — adjust to your setup.
DEFAULT_PX_PER_CM = 32.0


def free_fall_time(height_m: float) -> float:
    """
    Time (seconds) for an object to fall *height_m* metres from rest.

    t = sqrt(2*h / g)
    """
    if height_m <= 0:
        return 0.0
    return (2.0 * height_m / GRAVITY) ** 0.5


def velocity_at_landing(height_m: float) -> float:
    """Impact speed (m/s) after falling *height_m* metres: v = sqrt(2*g*h)."""
    if height_m <= 0:
        return 0.0
    return (2.0 * GRAVITY * height_m) ** 0.5


def horizontal_range(v0_x: float, v0_y: float, height_m: float) -> tuple[float, float]:
    """
    Horizontal displacement (m) after an object is thrown with initial
    horizontal velocity (*v0_x*, *v0_y*) from *height_m* metres above the floor.

    Returns (delta_x, delta_y) in metres.
    """
    t = free_fall_time(height_m)
    return (v0_x * t, v0_y * t)
