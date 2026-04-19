# Auto-Aiming Dustbin

A real-time system that uses an overhead USB camera to detect a thrown object,
predicts its landing coordinates with parabola fitting, and drives an
omni-wheel platform to catch it — all on a laptop + Arduino.

```
Camera → Laptop (Python + OpenCV) → Arduino (USB serial) → 4× DC motors
```

## Project layout

```
Auto-aiming-Dustbin/
├── main.py                    # Full system entry point
├── demo.py                    # Demo mode (no hardware required)
├── test_vision.py             # Camera + detection test (no motors)
├── test_motors.py             # Motor test (no camera)
├── config.yaml                # Root-level config reference
├── requirements.txt
│
├── vision/                    # Camera, detection, tracking, calibration
├── trajectory/                # Parabola fitting & landing prediction
├── motor_control/             # Serial comm, omni-wheel kinematics, controller
│
├── arduino/                   # Arduino firmware (Uno/Mega + ESP32 variants)
├── config/                    # default.yaml (copy to local.yaml for your machine)
├── calibration_data/          # Saved camera calibration
│
└── docs/                      # Detailed guides
    ├── HARDWARE_GUIDE.md
    ├── CAMERA_CALIBRATION.md
    ├── ARDUINO_PROGRAMMING.md
    ├── TRAJECTORY_MATH.md
    └── TROUBLESHOOTING.md
```

## Quick start

```bash
# 1. Install dependencies
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2. Run demo (no hardware needed)
python demo.py --show

# 3. Test vision only (USB camera required)
python test_vision.py --show

# 4. Full system (camera + Arduino)
cp config/default.yaml config/local.yaml  # edit port, camera index, etc.
python main.py --config config/local.yaml --show
```

Use `--no-serial` to run without an Arduino.

## Documentation

| Guide | Contents |
|-------|----------|
| [SETUP.md](SETUP.md) | Python environment, Arduino IDE, first-run |
| [BUILD_PLAN.md](BUILD_PLAN.md) | 2-week day-by-day build roadmap |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Data flow, serial protocol, timing |
| [docs/HARDWARE_GUIDE.md](docs/HARDWARE_GUIDE.md) | BOM, wiring diagrams, assembly |
| [docs/CAMERA_CALIBRATION.md](docs/CAMERA_CALIBRATION.md) | px→cm calibration |
| [docs/ARDUINO_PROGRAMMING.md](docs/ARDUINO_PROGRAMMING.md) | Firmware upload & pin config |
| [docs/TRAJECTORY_MATH.md](docs/TRAJECTORY_MATH.md) | Parabola fitting math |
| [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | Common issues & fixes |
| [arduino/README.md](arduino/README.md) | Firmware protocol & pin table |
| [docs/COMMUNICATION_PROTOCOL.md](docs/COMMUNICATION_PROTOCOL.md) | Serial protocol spec |

## Running tests

```bash
pytest tests/ -v
```

All tests mock hardware — no camera or Arduino required.

## License

Use and modify for your course project as needed.
