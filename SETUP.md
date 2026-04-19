# Setup Guide

Step-by-step instructions to get the Auto-Aiming Dustbin running on a laptop and Arduino.

---

## 1. Prerequisites

| Item | Minimum version | Notes |
|------|----------------|-------|
| Python | 3.10 | Tested on 3.10–3.12 |
| Arduino IDE | 2.x | For uploading firmware |
| USB camera | Any 640×480 | Higher FPS = better prediction |
| Arduino Uno / Mega or ESP32 | — | ESP32 recommended for PWM quality |

---

## 2. Python environment

```bash
# Clone the repository
git clone https://github.com/DipanT18/Auto-aiming-Dustbin.git
cd Auto-aiming-Dustbin

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

### Verify OpenCV

```python
python -c "import cv2; print(cv2.__version__)"
```

If you see a version number, OpenCV is installed correctly.

---

## 3. Arduino IDE setup

1. Download and install [Arduino IDE 2.x](https://www.arduino.cc/en/software).
2. Open `arduino/motor_controller.ino` (Uno/Mega) **or** `arduino/motor_controller_esp32.ino` (ESP32).
3. For ESP32: install the ESP32 board package via **File → Preferences → Board Manager URL**:
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
4. Select **Tools → Board** → your board.
5. Select **Tools → Port** → the COM/ttyUSB port shown when the Arduino is plugged in.
6. Click **Upload** (Ctrl+U).

---

## 4. USB / Serial driver installation

| OS | Driver |
|----|--------|
| Windows | CH340 driver (most clones) or FTDI from manufacturer website |
| macOS | Usually auto-detected; if not, install [CH340 Mac driver](https://github.com/adrianmihalko/ch340g-ch34g-ch34x-mac-os-x-driver) |
| Linux | No driver needed; add your user to the `dialout` group: `sudo usermod -aG dialout $USER` |

Find the correct serial port:

- **Windows**: Device Manager → Ports (COM & LPT)
- **macOS**: `ls /dev/cu.*`
- **Linux**: `ls /dev/ttyUSB* /dev/ttyACM*`

Update `serial.port` in `config/default.yaml` (or `config/local.yaml`) to match.

---

## 5. Configuration

Copy the default config and adjust for your machine:

```bash
cp config/default.yaml config/local.yaml
```

Key settings to check in `config/local.yaml`:

```yaml
camera:
  index: 0        # change if a different camera is detected first

serial:
  port: /dev/ttyUSB0   # update to your actual port

motor_control:
  center_x: 320   # pixel position of the bin centre (calibrate after assembly)
  center_y: 240
```

---

## 6. First-run verification

### 6a. Vision only (no hardware)

Run the demo script — no Arduino or camera required:

```bash
python demo.py --show
```

You should see a synthetic ball arc across the screen with a red landing
prediction dot.

### 6b. Camera only

```bash
python test_vision.py --show
```

You should see the camera feed. Wave your hand to trigger motion detection
(green bounding box).

### 6c. Motors only

Ensure the Arduino is connected and firmware uploaded, then:

```bash
python test_motors.py
```

The platform will execute a short movement sequence and stop.

### 6d. Full system

```bash
python main.py --config config/local.yaml --show
```

---

## 7. Running the tests

```bash
pytest tests/ -v
```

All tests mock hardware, so no camera or Arduino is required.
