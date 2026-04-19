# Prototype Phase Guide: Laptop + Arduino Setup

A complete, beginner-friendly guide for building the Auto-Aiming Dustbin using a **laptop for vision processing** and **Arduino microcontroller for motor control**.

---

## Table of Contents
1. [System Architecture](#system-architecture)
2. [Bill of Materials](#bill-of-materials)
3. [Hardware Assembly](#hardware-assembly)
4. [Software Setup](#software-setup)
5. [Calibration](#calibration)
6. [First Run & Testing](#first-run--testing)
7. [Troubleshooting](#troubleshooting)

---

## System Architecture

### Prototype Phase vs Original Design

**Original Design (Raspberry Pi):**
- All processing (vision + motor control) on Pi
- Advantage: Integrated, portable
- Disadvantage: Limited processing power

**Prototype Phase (Laptop + Arduino):**
- Vision processing on laptop (powerful, flexible)
- Motor control on Arduino (lightweight, real-time)
- Advantage: Better performance, easier debugging, modular

```
FLOW:
Overhead Camera 
    ↓ (USB video stream)
Laptop (Python + OpenCV)
    ↓ (serial command via USB)
Arduino / ESP32
    ↓ (PWM signals via GPIO pins)
Motor Drivers (L298N)
    ↓
DC Motors → Omni-Wheel Platform → [TRASH CAN]
```

---

## Bill of Materials

### 🎥 Vision System

| Component | Specification | Quantity | Approx Cost | Link |
|---|---|---|---|---|
| USB Webcam | 1080p, 90-120° FOV, 30+ FPS | 1 | ₹1000-2000 | Amazon/eBay |
| Tripod/Mount | 2-2.5m adjustable stand | 1 | ₹500-1500 | Any photo store |

### 🧠 Microcontroller

| Component | Specification | Quantity | Approx Cost | Link |
|---|---|---|---|---|
| Arduino Uno / ESP32 | 5V/3.3V output, 12+ GPIO pins | 1 | ₹300-800 | Amazon/ElectronicComp |
| USB Cable | For uploading sketches | 1 | ₹50 | Any store |

### ⚙️ Motion System

| Component | Specification | Quantity | Approx Cost | Notes |
|---|---|---|---|---|
| 100mm Omni Wheel | 45° roller wheels | 4 | ₹800-1200 | Find on Robotics India/DJI |
| 12V DC Motor | 300-400 RPM, with encoder | 4 | ₹1000-2000 | Important: encoder for feedback |
| L298N Motor Driver | 2A per channel, dual motors | 2 | ₹200-400 | One driver per 2 motors |
| Aluminum Frame / Plywood | Base platform structure | 1 | ₹500 | DIY or pre-made kit |
| Castor Wheel | Small support wheel (optional) | 2 | ₹100 | For platform stability |

### 🔋 Power System

| Component | Specification | Quantity | Approx Cost | Notes |
|---|---|---|---|---|
| 12V LiPo Battery | 3S, 5000mAh capacity | 1 | ₹1500-2500 | Powers motors |
| Buck Converter | 12V → 5V, 2A output | 1 | ₹100-200 | Powers Arduino |
| Battery Charger | 3S LiPo compatible | 1 | ₹500-1000 | Don't cheap out on charger! |
| Power Switch | Inline switch for battery | 1 | ₹30 | Safety |

### 🔧 Miscellaneous

| Item | Approx Cost | Notes |
|---|---|---|
| Breadboard | ₹50 | For prototyping connections |
| Jumper Wires | ₹50 | 40-pin M-F and M-M sets |
| Soldering Kit | ₹200 | For permanent connections |
| Plastic Trash Can | ₹100 | Lightweight (< 500g) |
| Heat Shrink Tubing | ₹30 | Protects solder joints |
| M3 Bolts & Nuts | ₹50 | For assembly |

### 💻 Laptop Requirements

- **OS:** Windows, macOS, or Linux
- **RAM:** 4GB minimum (8GB recommended)
- **USB:** At least 2 USB ports (camera + Arduino)
- **Python:** 3.8+ installed

**Total Approx Budget: ₹6,000 - 12,000** (~$75-150 USD)

---

## Hardware Assembly

### Step 1: Build the Omni-Wheel Platform

**Goal:** Create a stable, movable base that can hold the trash can

**Materials:**
- Aluminum channel or plywood (500mm × 500mm base)
- 4x 100mm omni wheels
- 4x 12V DC motors
- Bolts, nuts, brackets

**Process:**

1. Cut/obtain a 500mm × 500mm square base
2. Mount motors at each corner using L-brackets
3. Attach omni wheels to motor shafts
4. Ensure all 4 wheels are level and at same height
5. Add castor wheels at corners for stability (optional)

```
Top view:
    Motor1 ←─→ Motor2
       ↑         ↑
       │         │ 500mm
       │         │
    Motor3 ←─→ Motor4

Each motor at 45° angle for omni-directional movement
```

**Test:** Manually spin each wheel — should rotate smoothly without resistance

---

### Step 2: Wire Motor Drivers to Motors

**Each L298N controls 2 motors**

**Pinout (L298N Motor Driver):**
```
┌─────────────────────────────────────┐
│          L298N Motor Driver          │
├─────────────────────────────────────┤
│ Pin 1 (EN1)  → PWM pin for Motor 1  │
│ Pin 2 (IN1)  → Direction for Motor 1│
│ Pin 3 (IN2)  → Direction for Motor 1│
│ Pin 4 (GND)  → Ground               │
│ Pin 5 (GND)  → Ground               │
│ Pin 6 (IN3)  → Direction for Motor 2│
│ Pin 7 (IN4)  → Direction for Motor 2│
│ Pin 8 (EN2)  → PWM pin for Motor 2  │
│                                     │
│ +12V, GND    → Battery connections  │
└─────────────────────────────────────┘
```

**Connections for Motor 1 (to L298N #1):**
- Motor 1 (+) → L298N pin 6
- Motor 1 (-) → L298N pin 7
- Motor 2 (+) → L298N pin 2
- Motor 2 (-) → L298N pin 3

**Connections for Motor 3 & 4 (to L298N #2):**
- Same pattern as above

---

### Step 3: Connect L298N Drivers to Arduino

**Arduino to L298N #1:**
```
Arduino Pin 3   → L298N #1 EN1 (PWM for Motor 1)
Arduino Pin 4   → L298N #1 IN1 (Direction)
Arduino Pin 5   → L298N #1 IN2 (Direction)
Arduino Pin 6   → L298N #1 EN2 (PWM for Motor 2)
Arduino Pin 7   → L298N #1 IN3 (Direction)
Arduino Pin 8   → L298N #1 IN4 (Direction)
Arduino GND     → L298N #1 GND
```

**Arduino to L298N #2:**
```
Arduino Pin 9   → L298N #2 EN1 (PWM for Motor 3)
Arduino Pin 10  → L298N #2 IN1 (Direction)
Arduino Pin 11  → L298N #2 IN2 (Direction)
Arduino Pin 12  → L298N #2 EN2 (PWM for Motor 4)
Arduino Pin 13  → L298N #2 IN3 (Direction)
Arduino Pin A0  → L298N #2 IN4 (Direction)
Arduino GND     → L298N #2 GND
```

**Power Connections (to L298N drivers):**
```
Battery +12V    → Both L298N +12V pins
Battery GND     → Both L298N GND pins
Buck Converter +5V → Arduino +5V
Buck Converter GND → Arduino GND
```

**Wiring Diagram:**
```
[12V Battery]
    ├─→ [Buck Converter] → [Arduino +5V, GND]
    ├─→ [L298N #1 +12V, GND]
    ├─→ [L298N #2 +12V, GND]

[Arduino GPIO]
    ├─→ [L298N #1 PWM/Direction pins]
    └─→ [L298N #2 PWM/Direction pins]

[L298N #1] → [Motors 1 & 2]
[L298N #2] → [Motors 3 & 4]
```

---

### Step 4: Mount Camera

**Setup:**
- Mount camera on tripod or ceiling arm
- Position 2-2.5 meters above the play area
- Center it over the platform
- Ensure 90-120° FOV covers entire play area

**Camera Angle:** Directly overhead (top-down)

```
           [CAMERA]
            ║ 2-2.5m
            ║
    ┌───────┼────────┐
    │       │        │
    │ PLAY  │ AREA   │
    │    [BIN]       │
    └─────────────────┘
```

**Why top-down?**
- Direct X,Y floor coordinates (no 3D math needed)
- Simplest trajectory prediction
- Most reliable detection

---

## Software Setup

### Step 1: Install Python & Dependencies

**Windows:**
```bash
# Download Python 3.10+ from python.org
# During installation: CHECK "Add Python to PATH"

# Open Command Prompt, navigate to project folder
python --version  # Verify installation

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**macOS/Linux:**
```bash
# Python usually pre-installed, but verify
python3 --version

# Navigate to project folder
cd Auto-aiming-Dustbin

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Upload Arduino Firmware

**Using Arduino IDE:**

1. Download [Arduino IDE](https://www.arduino.cc/en/software)
2. Open `firmware/arduino_motor_control.ino`
3. Select Board: Tools → Board → Arduino Uno (or ESP32)
4. Select Port: Tools → Port → COM# (your Arduino port)
5. Click Upload ▶️

**Verify:** Arduino IDE should say "Done Uploading" with no errors

### Step 3: Verify Camera Connection

```bash
# Activate virtual environment if not already
python tests/test_camera.py
```

**Expected Output:**
```
Camera opened successfully!
Frame size: 1280x720
FPS: 30
Press 'q' to quit
```

### Step 4: Verify Arduino Connection

**First, identify your Arduino port:**

**Windows:**
- Device Manager → Ports → COM# (e.g., COM3)

**macOS/Linux:**
```bash
ls /dev/tty.*  # macOS
# or
ls /dev/ttyUSB*  # Linux
```

**Then update config:**

Edit `config/system_config.yaml`:
```yaml
arduino:
  port: COM3          # Windows
  # port: /dev/ttyUSB0  # Linux
  # port: /dev/tty.usbserial-142  # macOS
  baudrate: 9600
```

**Test connection:**
```bash
python tests/test_serial_connection.py
```

**Expected Output:**
```
Arduino connected on COM3 at 9600 baud
Sending test command...
Success!
```

---

## Calibration

### Camera Calibration (Pixel to Real-World Mapping)

This converts pixel coordinates in the image to actual distances (cm) on the floor.

**Setup:**
1. Print or draw a checkerboard pattern (20×20 grid, each square = 10cm)
2. Place on floor in center of play area
3. Position camera 2.5m overhead

**Run calibration:**
```bash
python calibration/calibrate_camera.py
```

**Process:**
- Takes 10-15 images of the checkerboard from different angles
- Calculates pixel-to-cm ratio
- Stores in `calibration/calibration_data.json`

**Verify:** The calibration_data.json should contain:
```json
{
  "camera_matrix": [...],
  "dist_coeffs": [...],
  "pixels_per_cm": 25.5,
  "timestamp": "2026-04-19"
}
```

---

### Motor Calibration (PWM to Speed Mapping)

This finds the optimal PWM values for consistent motor speeds.

**Process:**
1. Platform sits on a flat surface (not elevated)
2. Each motor is tested individually
3. PWM values (0-255) are mapped to actual speeds

**Run calibration:**
```bash
python calibration/calibrate_motors.py
```

**What happens:**
- Motor 1 ramps up: 0 → 255 PWM (takes ~30 seconds)
- Motor 2 ramps up: same process
- Motor 3 ramps up: same process
- Motor 4 ramps up: same process

**Verify:** Watch wheels spin faster as PWM increases. If any wheel doesn't spin, check wiring!

---

## First Run & Testing

### Test 1: Object Detection (No Movement)

```bash
python tests/test_object_detection.py
```

**What happens:**
- Camera shows live feed
- Red rectangle shows detected object
- Console prints (x, y) center position

**Try:** Throw a ball or object near the platform. You should see detection in the video.

---

### Test 2: Motor Movement

```bash
python tests/test_motor_movement.py
```

**What happens:**
- Platform moves in a square: Forward → Right → Backward → Left
- Each direction for 2 seconds
- Then stops

**Verify:** All 4 wheels move in the expected direction

---

### Test 3: Trajectory Prediction

```bash
python tests/test_trajectory.py
```

**What happens:**
- Generates synthetic object trajectory (ball falling)
- Fits parabola
- Predicts landing point
- Shows accuracy percentage

**Expected:** 80%+ prediction accuracy

---

### Test 4: Full System Run

```bash
python vision/main.py
```

**What happens:**
1. Camera feed starts
2. Object detection runs
3. When object detected → trajectory prediction
4. Platform moves to predicted location
5. Catches object!

**Try:** Throw objects near the platform and watch it move!

---

## Troubleshooting

### Camera Issues

**Q: "Cannot open camera" error**
- A: Check USB connection
- A: Try `python tests/test_camera.py` to debug
- A: On Linux, you may need: `sudo usermod -a -G video $USER`

**Q: Camera is upside down**
- A: Edit `vision/camera_feed.py`, add `frame = cv2.flip(frame, -1)`

**Q: Low FPS (< 20)**
- A: Reduce resolution in `config/system_config.yaml`
- A: Close other GPU-heavy applications

---

### Arduino Issues

**Q: "Port not found" error**
- A: Check Device Manager (Windows) or `ls /dev/tty*` (Linux/Mac)
- A: Try different USB port on computer
- A: Restart Arduino IDE

**Q: Upload fails**
- A: Select correct board (Tools → Board)
- A: Select correct COM port
- A: Try different USB cable

**Q: Motors don't move when code runs**
- A: Check 12V battery is connected and powered ON
- A: Verify L298N connections to motor drivers
- A: Run `tests/test_motor_movement.py` to debug

---

### Detection Issues

**Q: Objects not detected**
- A: Adjust threshold in `config/detection_config.yaml`
- A: Ensure good lighting (no shadows on play area)
- A: Try `python tests/test_object_detection.py`

**Q: False detections (detecting shadows, etc.)**
- A: Increase `min_contour_area` in config
- A: Decrease `detection_threshold`
- A: Run background subtraction calibration

---

### Prediction Issues

**Q: Platform moves to wrong location**
- A: Verify camera calibration: `python calibration/calibrate_camera.py`
- A: Check if camera is perfectly overhead
- A: Try `python tests/test_trajectory.py` to test prediction accuracy

**Q: Too slow to catch object**
- A: Increase motor PWM in `config/motor_config.yaml`
- A: Reduce prediction time threshold (predict earlier)
- A: Ensure battery is fully charged

---

## Next Steps

1. ✅ Assemble hardware
2. ✅ Upload firmware
3. ✅ Install software
4. ✅ Run tests
5. 🚀 Optimize and customize
   - Adjust detection thresholds for your environment
   - Tune motor speeds for faster movement
   - Experiment with different object types
   - Add LED indicators for visual feedback
   - Fine-tune trajectory prediction algorithm

---

## Getting Help

- **Hardware issues:** Check `docs/HARDWARE_SPECS.md`
- **Code issues:** Check `docs/TROUBLESHOOTING.md`
- **Questions:** Open an issue on GitHub
- **Want to contribute:** Create a pull request!

---

**You're ready to build! Start with Hardware Assembly and come back here for software steps. Good luck! 🚀**
