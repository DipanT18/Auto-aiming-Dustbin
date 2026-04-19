"""Tests for motor_control/kinematics.py"""

from __future__ import annotations

import pytest
from motor_control.kinematics import compute_wheel_speeds, pixel_error_to_velocity, WheelSpeeds


def test_wheel_speeds_pure_x():
    s = compute_wheel_speeds(vx=100.0, vy=0.0)
    # W1 front-left: +vx - vy = +100
    # W2 front-right: -vx - vy = -100
    # W3 rear-right: -vx + vy = -100
    # W4 rear-left: +vx + vy = +100
    assert s.w1 == 100
    assert s.w2 == -100
    assert s.w3 == -100
    assert s.w4 == 100


def test_wheel_speeds_pure_y():
    s = compute_wheel_speeds(vx=0.0, vy=100.0)
    # W1: 0 - 100 = -100
    # W2: 0 - 100 = -100
    # W3: 0 + 100 = +100
    # W4: 0 + 100 = +100
    assert s.w1 == -100
    assert s.w2 == -100
    assert s.w3 == 100
    assert s.w4 == 100


def test_wheel_speeds_stop():
    s = compute_wheel_speeds(0.0, 0.0)
    assert s == WheelSpeeds(0, 0, 0, 0)


def test_wheel_speeds_clamp():
    s = compute_wheel_speeds(vx=300.0, vy=300.0)
    for v in (s.w1, s.w2, s.w3, s.w4):
        assert -255 <= v <= 255


def test_pixel_error_to_velocity():
    vx, vy = pixel_error_to_velocity(100.0, 50.0, gain=1.0, max_speed=255.0)
    assert vx == pytest.approx(100.0)
    assert vy == pytest.approx(50.0)


def test_pixel_error_to_velocity_clamp():
    vx, vy = pixel_error_to_velocity(1000.0, 1000.0, gain=1.0, max_speed=200.0)
    assert vx == pytest.approx(200.0)
    assert vy == pytest.approx(200.0)
