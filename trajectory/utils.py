"""Math utility functions shared across trajectory calculations."""

from __future__ import annotations

import math


def clamp(value: float, lo: float, hi: float) -> float:
    """Clamp *value* to [*lo*, *hi*]."""
    return max(lo, min(hi, value))


def distance(p1: tuple[float, float], p2: tuple[float, float]) -> float:
    """Euclidean distance between two 2-D points."""
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def pixels_to_cm(pixels: float, px_per_cm: float) -> float:
    """Convert a pixel measurement to centimetres using a calibration factor."""
    if px_per_cm <= 0:
        raise ValueError("px_per_cm must be positive")
    return pixels / px_per_cm


def cm_to_pixels(cm: float, px_per_cm: float) -> float:
    """Convert centimetres to pixels using a calibration factor."""
    if px_per_cm <= 0:
        raise ValueError("px_per_cm must be positive")
    return cm * px_per_cm


def solve_quadratic(a: float, b: float, c: float) -> tuple[float, float] | None:
    """
    Return both real roots of a*x^2 + b*x + c = 0, or *None* if no real roots.

    Returns the two roots as a tuple (smaller, larger).
    """
    discriminant = b * b - 4.0 * a * c
    if discriminant < 0:
        return None
    sqrt_d = math.sqrt(discriminant)
    if abs(a) < 1e-12:
        if abs(b) < 1e-12:
            return None
        root = -c / b
        return (root, root)
    r1 = (-b - sqrt_d) / (2.0 * a)
    r2 = (-b + sqrt_d) / (2.0 * a)
    return (min(r1, r2), max(r1, r2))
