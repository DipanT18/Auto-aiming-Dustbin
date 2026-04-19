# System Architecture

This document describes the data flow, component interactions, and timing
budget of the Auto-Aiming Dustbin.

---

## High-level overview

```
┌─────────────────────────────────────────────────────┐
│                  OVERHEAD CAMERA                    │
│          (fixed, top-down, 640×480 @ 30fps)         │
└──────────────────────┬──────────────────────────────┘
                       │ USB / CSI
┌──────────────────────▼──────────────────────────────┐
│                 LAPTOP (Python)                     │
│                                                     │
│  vision/          trajectory/     motor_control/    │
│  ┌────────────┐  ┌────────────┐  ┌───────────────┐  │
│  │ CameraFeed │→ │ Detector   │→ │ Predictor     │  │
│  └────────────┘  └─────┬──────┘  └──────┬────────┘  │
│                        │ Detection       │ (x,y)     │
│                        ▼                ▼            │
│                  ┌───────────┐  ┌───────────────┐   │
│                  │ Tracker   │  │ MotorController│   │
│                  └───────────┘  └──────┬────────┘   │
│                                        │ MOVE vx vy  │
└────────────────────────────────────────┼────────────┘
                                         │ USB Serial (115200 baud)
┌────────────────────────────────────────▼────────────┐
│                   ARDUINO                           │
│              (Uno / Mega / ESP32)                   │
│                                                     │
│  Receives MOVE commands → X-drive mixing → PWM      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │ L298N  A │  │ L298N  B │  │ SerialRx │           │
│  └────┬─────┘  └─────┬────┘  └──────────┘           │
│    W1   W2         W3   W4                          │
└─────┬───┴─────────────┴──┬──────────────────────────┘
      └──── Omni-Wheel Platform ────┘
                  │
            [TRASH CAN]
```

---

## Module responsibilities

| Module | Responsibility |
|--------|---------------|
| `vision/camera_feed.py` | Open USB camera, yield BGR frames |
| `vision/object_detection.py` | Frame-diff motion detection, return `Detection` |
| `vision/tracker.py` | Maintain centroid history, detect landing |
| `trajectory/predictor.py` | Fit parabola to samples, predict floor intercept |
| `motor_control/serial_comm.py` | ASCII serial protocol to Arduino |
| `motor_control/kinematics.py` | Pixel error → vx/vy → per-wheel PWM mixing |
| `motor_control/controller.py` | Deadband, gain, coordinate the above two |
| `arduino/*.ino` | Parse serial commands, drive L298N PWM outputs |

---

## Serial protocol

All messages are newline-terminated ASCII over USB at **115200 baud**.

### Laptop → Arduino

```
MOVE <vx> <vy>    vx,vy: signed integers -255..255
STOP              halt all motors
HOME              stop (no encoder homing in current firmware)
PING              health check
```

### Arduino → Laptop

```
OK PONG           response to PING
OK                command accepted
ERR PARSE         unrecognised command
```

---

## Data flow (single frame)

```
t=0  ms  CameraFeed.read() → BGR frame (640×480)
t=1  ms  ObjectDetector.detect() → Detection or None
t=2  ms  ObjectTracker.update() → Track
t=2  ms  TrajectoryPredictor.add(t, cx, cy)
t=3  ms  TrajectoryPredictor.predict() → (x_land, y_land) or None
t=3  ms  MotorController.move_to(x_land, y_land)
t=4  ms  SerialComm.move(vx, vy) → "MOVE vx vy\n" over USB
t=5  ms  Arduino receives, mixes, sets PWM
t=6  ms  Motors begin accelerating
```

**Total laptop-to-motor latency: ~5–8 ms** (dominated by USB serial latency).

---

## Timing budget

A 30 fps camera gives a **33 ms** frame budget.

| Stage | Target budget |
|-------|--------------|
| Frame capture | ≤ 5 ms |
| Detection + tracking | ≤ 8 ms |
| Trajectory prediction | ≤ 2 ms |
| Serial write | ≤ 5 ms |
| Arduino processing | ≤ 3 ms |
| **Total** | **≤ 23 ms** (fits within 33 ms frame) |

For a fast throw at 3 m/s crossing a 1 m platform, the object is airborne
for ~300 ms.  After collecting 3 frames (≈100 ms), the system has ~200 ms
to move the platform — enough for the motors to traverse ~30 cm at 200 rpm.

---

## Configuration keys

All tunable parameters live in `config/default.yaml`.  Override in
`config/local.yaml` (gitignored) for machine-specific settings.

| Key | Default | Effect |
|-----|---------|--------|
| `camera.fps` | 30 | Higher FPS = faster tracking, more CPU |
| `trajectory.history` | 8 | More samples = smoother fit, more lag |
| `trajectory.horizon_s` | 0.35 | Fallback look-ahead when no floor intercept |
| `motor_control.gain` | 0.5 | Higher = faster response, risk of overshoot |
| `motor_control.deadband_px` | 10 | Prevents jitter near target |
