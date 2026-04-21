# Auto-Aiming Dustbin

A real-time system that uses an overhead USB camera to detect a thrown object,
predicts its landing coordinates with parabola fitting, and drives an
omni-wheel platform to catch it.

**Primary runtime target: Raspberry Pi.**
Laptop is supported for testing and demo (no hardware required for `demo.py`).

```
Camera → Raspberry Pi (Python + OpenCV) → Arduino (USB serial) → 4× DC motors
```

## Project layout

```
Auto-aiming-Dustbin/
│
├── raspberry_pi/                  # System A — Python runtime
│   ├── app/
│   │   ├── main.py                # Full system entry point
│   │   ├── demo.py                # Demo mode (no hardware required)
│   │   ├── test_vision.py         # Camera + detection test (no motors)
│   │   ├── test_motors.py         # Motor test (no camera)
│   │   ├── vision/                # Camera, detection, tracking
│   │   ├── trajectory/            # Parabola fitting & landing prediction
│   │   └── motor_control/         # Serial comm, kinematics, controller
│   ├── config/
│   │   └── local.yaml             # Runtime configuration (edit for your setup)
│   ├── requirements.txt
│   ├── setup.sh                   # Install dependencies (run once on Pi)
│   └── run.sh                     # Start the system
│
├── arduino/                       # System B — firmware
│   ├── uno/
│   │   └── auto_aiming_uno.ino    # Arduino Uno / Mega firmware
│   ├── esp32/
│   │   └── auto_aiming_esp32.ino  # ESP32 firmware
│   ├── mega/
│   │   └── README.md              # Placeholder — Mega-specific sketch
│   └── common/
│       └── protocol.h             # Shared serial protocol constants
│
├── docs/                          # Detailed guides
│   ├── HARDWARE_GUIDE.md
│   ├── CAMERA_CALIBRATION.md
│   ├── ARDUINO_PROGRAMMING.md
│   ├── TRAJECTORY_MATH.md
│   ├── COMMUNICATION_PROTOCOL.md
│   └── TROUBLESHOOTING.md
│
├── calibration_data/              # Saved camera calibration
├── pytest.ini
├── ARCHITECTURE.md
├── BUILD_PLAN.md
├── SETUP.md
└── README.md
```

## Quickstart — Raspberry Pi (primary deployment)

```bash
# 1. Clone and enter the Pi directory
git clone https://github.com/DipanT18/Auto-aiming-Dustbin
cd Auto-aiming-Dustbin/raspberry_pi

# 2. Install dependencies (run once)
chmod +x setup.sh run.sh
./setup.sh

# 3. Edit config for your hardware (serial port, camera index, etc.)
nano config/local.yaml

# 4. Start the system
./run.sh
```

## Quickstart — Laptop (testing / demo)

```bash
# Install dependencies
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r raspberry_pi/requirements.txt

# Run demo (no hardware needed)
python raspberry_pi/app/demo.py --show

# Test vision only (USB camera required, no Arduino)
python raspberry_pi/app/test_vision.py --show

# Test motors only (Arduino required, no camera)
python raspberry_pi/app/test_motors.py

# Full system (camera + Arduino)
python raspberry_pi/app/main.py --config raspberry_pi/config/local.yaml --show
```

Use `--no-serial` to run the vision pipeline without an Arduino connected.

## Arduino flashing

1. Install the [Arduino IDE](https://www.arduino.cc/en/software) (2.x recommended).
2. Open the `.ino` file for your board:
   - Uno / Mega → `arduino/uno/auto_aiming_uno.ino`
   - ESP32      → `arduino/esp32/auto_aiming_esp32.ino`
3. Select **Tools → Board** and choose your board.
4. Select **Tools → Port** and choose the correct COM port.
5. Click **Upload** (Ctrl+U).

Once uploaded, open the Serial Monitor at **115200 baud** and type `PING`.
You should see `OK PONG`.

## Serial protocol (brief)

All messages are newline-terminated ASCII at 115200 baud.
Constants are defined in `arduino/common/protocol.h`.

| Command (Pi → Arduino) | Description |
|------------------------|-------------|
| `MOVE <vx> <vy>` | Drive platform; signed integers -255..255 |
| `STOP` | Halt all motors |
| `PING` | Health check |

| Response (Arduino → Pi) | Meaning |
|-------------------------|---------|
| `OK PONG` | Reply to PING |
| `OK` | Command accepted |
| `ERR PARSE` | Unknown command |

See [docs/COMMUNICATION_PROTOCOL.md](docs/COMMUNICATION_PROTOCOL.md) for the full spec.

## Running unit tests

```bash
pytest
```

All tests mock hardware — no camera or Arduino required.

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
| [docs/COMMUNICATION_PROTOCOL.md](docs/COMMUNICATION_PROTOCOL.md) | Serial protocol spec |

## License

Use and modify for your course project as needed.
