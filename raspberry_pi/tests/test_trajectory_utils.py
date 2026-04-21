"""Tests for trajectory/utils.py"""

from __future__ import annotations

import math
import pytest
from trajectory.utils import clamp, distance, pixels_to_cm, cm_to_pixels, solve_quadratic


def test_clamp():
    assert clamp(5.0, 0.0, 10.0) == 5.0
    assert clamp(-1.0, 0.0, 10.0) == 0.0
    assert clamp(11.0, 0.0, 10.0) == 10.0


def test_distance():
    assert distance((0, 0), (3, 4)) == pytest.approx(5.0)


def test_pixels_to_cm():
    assert pixels_to_cm(100.0, 10.0) == pytest.approx(10.0)


def test_cm_to_pixels():
    assert cm_to_pixels(10.0, 10.0) == pytest.approx(100.0)


def test_pixels_to_cm_invalid():
    with pytest.raises(ValueError):
        pixels_to_cm(100.0, 0.0)


def test_solve_quadratic_two_roots():
    roots = solve_quadratic(1.0, 0.0, -1.0)  # x^2 - 1 = 0 → x = ±1
    assert roots is not None
    assert roots[0] == pytest.approx(-1.0)
    assert roots[1] == pytest.approx(1.0)


def test_solve_quadratic_no_real_root():
    roots = solve_quadratic(1.0, 0.0, 1.0)  # x^2 + 1 = 0
    assert roots is None


def test_solve_quadratic_linear():
    roots = solve_quadratic(0.0, 2.0, -4.0)  # 2x - 4 = 0 → x = 2
    assert roots is not None
    assert roots[0] == pytest.approx(2.0)
