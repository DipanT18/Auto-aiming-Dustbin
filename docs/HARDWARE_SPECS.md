# Hardware Specifications & Wiring Diagrams

Complete technical documentation for all hardware components and connections.

---

## Table of Contents
1. [Microcontroller Pinout](#microcontroller-pinout)
2. [Motor Driver Connections](#motor-driver-connections)
3. [Power System](#power-system)
4. [Component Specifications](#component-specifications)
5. [Wiring Checklists](#wiring-checklists)

---

## Microcontroller Pinout

### Arduino Uno / Arduino Nano

```
┌────────────────────────────────────────┐
│           ARDUINO UNO                   │
├────────────────────────────────────────┤
│  Digital Pins (PWM capable: ~)         │
│  0 (RX)  ┤├ D13 (LED) SCK             │
│  1 (TX)  ┤├ D12                        │
│  2       ┤├ D11 ~ (L298N #2 EN2)      │
│  3 ~     ┤├ D10 ~ (L298N #2 EN1)      │
│  4       ┤├ D9  ~ (L298N #1 EN2)      │
│  5 ~     ┤├ D8   (L298N #1 IN4)       │
│  6 ~     ┤├ D7   (L298N #1 IN3)       │
│  7       ┤├ D6 ~ (L298N #1 EN1)       │
│  8       ┤├ D5 ~ (L298N #1 IN2)       │
│  9 ~     ┤├ D4   (L298N #1 IN1)       │
│  10 ~    ┤├ D3 ~ (L298N #2 IN2)       │
│  11 ~    ┤├ D2   (L298N #2 IN1)       │
│  12      ┤├ D1 (TX)                    │
│  13 ~ LED│├ D0 (RX)                    │
│          ├                             │
│  Analog Pins (Serial)                  │
│  A0 (L298N #2 IN4) A5                  │
│  A1              A4 (SDA)              │
│  A2              A3 (SCL)              │
│  5V ──────────── GND                   │
└────────────────────────────────────────┘
```

### ESP32

```
┌────────────────────────────────────────┐
│             ESP32 DEVKIT                │
├────────────────────────────────────────┤
│  GPIO Pins (PWM capable: most pins)    │
│  GND     ┤├ VIN (12V through regulator)│
│  TX/RX   ┤├ GND                        │
│  IO34    ┤├ IO35                       │
│  IO32    ┤├ IO33 (L298N #2 EN2) ~     │
│  IO5 ~   ┤├ IO25 (L298N #2 EN1) ~     │
│  IO18    ┤├ IO26 (L298N #1 EN2) ~     │
│  IO19    ┤├ IO27 (L298N #1 IN4)       │
│  IO21    ┤├ IO14 (L298N #1 IN3) ~     │
│  IO3(RX) ┤├ IO12 (L298N #1 EN1) ~     │
│  IO1(TX) ┤├ IO13 (L298N #1 IN2)       │
│  IO22    ┤├ IO15 (L298N #2 IN1)       │
│  IO23    ┤├ IO2  (L298N #2 IN2) ~     │
│  GND     ┤├ GND                        │
│  3.3V    ┤├ EN                         │
│          ├                             │
│  5V ────────── GND (via regulator)     │
└────────────────────────────────────────┘
```

---

## Motor Driver Connections

### L298N Motor Driver Pinout

```
┌─────────────────────────┐
│    L298N MOTOR DRIVER    │
│   (Dual Motor Control)   │
├─────────────────────────┤
│          Top View        │
│                          │
│    OUT1  OUT2           │  Motor A connections
│  ┌─────┬─────┐          │
│  │ OUT1│ OUT2│◄─ Motor A│
│  │     │     │          │
│  │ IN1 │ IN2 │◄─ Direction (Motor A)
│  │ EN  │ EN  │◄─ Speed PWM (Motor A)
│  ├─────┴─────┤          │
│  │ GND │ GND │◄─ Ground │
│  │ +12V│ +12V│◄─ 12V Power
│  │ GND │ GND │◄─ Ground │
│  ├─────┬─────┤          │
│  │ EN  │ EN  │◄─ Speed PWM (Motor B)
│  │ IN3 │ IN4 │◄─ Direction (Motor B)
│  │     │     │          │
│  │ OUT3│ OUT4│◄─ Motor B│
│  └─────┴─────┘          │
│   OUT3  OUT4            │  Motor B connections
└─────────────────────────┘
```

### Pin Function Table

| Pin # | Pin Name | Function | Direction | Connected To |
|---|---|---|---|---|
| 1 | OUT1 | Motor A (+) | Output | Motor positive |
| 2 | OUT2 | Motor A (-) | Output | Motor negative |
| 3 | GND | Ground | — | Arduino GND |
| 4 | IN1 | Motor A Dir 1 | Input | Arduino GPIO |
| 5 | IN2 | Motor A Dir 2 | Input | Arduino GPIO |
| 6 | EN | Motor A Speed | Input | Arduino PWM |
| 7 | IN3 | Motor B Dir 1 | Input | Arduino GPIO |
| 8 | IN4 | Motor B Dir 2 | Input | Arduino GPIO |
| 9 | +12V | Power Supply | Input | 12V Battery |
| 10 | GND | Power Ground | — | Battery GND |
| 11 | GND | Ground | — | Arduino GND |
| 12 | EN | Motor B Speed | Input | Arduino PWM |
| 13 | OUT3 | Motor B (+) | Output | Motor positive |
| 14 | OUT4 | Motor B (-) | Output | Motor negative |

---

## Motor Control Logic

### Direction Control

Motor direction is controlled by IN1 and IN2 pins:

```
IN1 | IN2 | Motor Direction
----|-----|─────────────────
 0  |  0  | STOP
 1  |  0  | FORWARD
 0  |  1  | BACKWARD
 1  |  1  | STOP (short brake)
```

### Speed Control

Motor speed is controlled by PWM on the EN pin:

```
PWM Value | Motor Speed
----------|────────────
    0     | STOP
   127    | 50% speed
   255    | Maximum speed
```

### Example: Motor Running Forward at 70% Speed

```
IN1 = 1 (HIGH)
IN2 = 0 (LOW)
EN  = 178 (70% of 255)
```

---

## Full Wiring Diagram

### Arduino to Motor Drivers (Complete)

```
ARDUINO UNO                  L298N #1 (Motors 1 & 2)
────────────                ──────────────���──────────
D2 ──────────────────────── IN1
D3 ──────────────────────── IN2
D4 ──────────────────────── EN (PWM)
D5 ──────────────────────── IN3
D6 ──────────────────────── IN4
D7 ──────────────────────── EN (PWM)
GND ──────────────────────── GND


ARDUINO UNO                  L298N #2 (Motors 3 & 4)
────────────                ─────────────────────────
D8 ──────────────────────── IN1
D9 ──────────────────────── IN2
D10 (PWM) ────────────────── EN
D11 (PWM) ────────────────── IN3
D12 ──────────────────────── IN4
D13 ──────────────────────── EN (PWM)
GND ──────────────────────── GND


POWER CONNECTIONS
─────────────────
12V Battery ──── +12V pins on both L298N drivers
Battery GND ──── GND pins on both L298N drivers
Buck Converter:
  12V input ──── Battery +12V
  GND ────────── Battery GND
  5V output ──── Arduino +5V
  GND ────────── Arduino GND

MOTOR CONNECTIONS (to L298N #1)
───────────────────────────────
Motor 1 (+) ──── OUT1
Motor 1 (-) ──── OUT2
Motor 2 (+) ──── OUT3
Motor 2 (-) ──── OUT4

MOTOR CONNECTIONS (to L298N #2)
───────────────────────────────
Motor 3 (+) ──── OUT1
Motor 3 (-) ──── OUT2
Motor 4 (+) ──── OUT3
Motor 4 (-) ──── OUT4
```

### Breadboard Layout (for prototyping)

```
Power Bus:                Arduino Row:
+12V ────────┐          D2  ├─ [wire to L298N #1 IN1]
             │          D3  ├─ [wire to L298N #1 IN2]
            ===          D4  ├─ [wire to L298N #1 EN]
            GND          D5  ├─ [wire to L298N #1 IN3]
             │          D6  ├─ [wire to L298N #1 EN]
           [Bridge to L298N +12V]

Motor Connections:
Motor 1 ──┬─ OUT1 ���─ L298N #1
          └─ OUT2 ── L298N #1
Motor 2 ──┬─ OUT3 ── L298N #1
          └─ OUT4 ── L298N #1
Motor 3 ──┬─ OUT1 ── L298N #2
          └─ OUT2 ── L298N #2
Motor 4 ──┬─ OUT3 ── L298N #2
          └─ OUT4 ── L298N #2
```

---

## Power System

### 12V LiPo Battery Specifications

```
Voltage:      11.1V - 12.6V (3S LiPo = 3 cells × 3.7-4.2V)
Capacity:     5000 mAh
Discharge:    50C rating (for high current draw)
Connector:    XT60 (common on large batteries)
```

### Buck Converter (12V to 5V)

```
┌────────────────────────┐
│   BUCK CONVERTER       │
├────────────────────────┤
│ Input:   12V ── GND   │
│ Output:  5V  ── GND   │
│                       │
│ Adjust: Trim pot for 5V output
│                       │
│ Typical specs:        │
│ - 2A max output       │
│ - Efficiency: 92%+    │
└────────────────────────┘

Input (12V):                Output (5V):
+12V ──── [Buck Conv] ──── +5V  → Arduino +5V
GND  ──── [Buck Conv] ──── GND  → Arduino GND
```

### Power Distribution

```
[12V LiPo Battery]
        │
        ├─── Switch (Power ON/OFF)
        │
        ├─ (+12V) ───┬─ L298N #1 +12V
        │            ├─ L298N #2 +12V
        │            └─ Buck Converter Input
        │
        ├─ (GND) ────┬─ L298N #1 GND
        │            ├─ L298N #2 GND
        │            └─ Buck Converter GND
        │
        └─ [Buck Converter] 
               │
               ├─ (+5V)  ─ Arduino +5V
               └─ (GND)  ─ Arduino GND
```

**Why this configuration?**
- Single battery powers everything
- Buck converter steps down 12V to 5V safely for Arduino
- Motors draw current directly from battery (high current capacity)
- Arduino draws minimal current (< 200mA)

---

## Component Specifications

### Motors

**Typical 12V DC Motor with Encoder:**
- Voltage: 12V DC
- No-load Speed: 300-400 RPM (for slow, controlled movement)
- Torque: 0.5-1.0 kg·cm
- Current (no-load): 0.2A
- Current (stalled): 2-3A
- Encoder: 64 CPR (counts per revolution) — optional but useful for speed control

**Why encoder?**
- Allows feedback on actual motor speed
- Helps detect stalled motors
- Can implement closed-loop speed control

### Omni-Directional Wheels

```
┌──────────────────┐
│  OMNI WHEEL      │
│  100mm diameter  │
├──────────────────┤
│  Side view:      │
│  ┌────────────┐  │
│  │ ◯◯◯◯◯◯◯◯ │  │ Small rollers at 45°
│  │◯ Main ◯   │  │
│  │◯ Wheel ◯  │  │
│  │◯◯◯◯◯◯◯◯ │  │
│  └────────────┘  │
│                  │
│ Allows movement  │
│ in any direction │
│ without turning  │
└──────────────────┘
```

**Specifications:**
- Diameter: 100mm
- Width: 50-70mm
- Material: Rubber/TPE
- Hub: Aluminum or plastic
- Suitable for: Indoor, flat surfaces
- Max load: 5-10 kg total platform

### L298N Motor Driver IC

```
┌─────────────────────────┐
│      L298N IC CHIP      │
├─────────────────────────┤
│ Technology:             │
│ Dual Bridge Driver      │
│                         │
│ Specifications:         │
│ - Logic Voltage: 5V     │
│ - Motor Voltage: 5-35V  │
│ - Max Current: 2A/ch    │
│ - PWM Frequency: <25kHz │
│ - Operating Temp: 0-70°C│
│                         │
│ Each L298N controls:    │
│ - 2 motors              │
│ - Direction + Speed     │
└─────────────────────────┘
```

### Camera (USB Webcam)

**Recommended Specifications:**
- Resolution: 1080p (1920×1080)
- Frame Rate: 30 FPS minimum (60 FPS ideal)
- FOV: 90-120° (wide angle, top-down)
- Focus: Auto-focus or manual focus
- Lens: Standard or wide-angle
- USB: 2.0 or 3.0 (3.0 for faster streaming)

**Why these specs?**
- High resolution: Better object tracking
- 30+ FPS: Enough for trajectory prediction
- Wide FOV: Covers entire play area
- USB plug-and-play: Easy to connect

### Arduino Uno vs ESP32

| Feature | Arduino Uno | ESP32 |
|---|---|---|
| CPU | 8-bit @ 16MHz | 32-bit Dual @ 240MHz |
| RAM | 2KB | 520KB |
| Flash | 32KB | 4MB |
| GPIO | 14 pins | 30+ pins |
| PWM | 6 channels | 16 channels |
| Serial | 1 UART | 3 UARTs |
| Wi-Fi | ❌ | ✅ |
| Bluetooth | ❌ | ✅ |
| Cost | ₹300-400 | ₹400-600 |
| **Best for** | **Simple projects** | **Advanced projects** |

**For this project:** Either works! Arduino Uno is simpler, ESP32 has more power and future expansion.

---

## Wiring Checklists

### Pre-Assembly Checklist

- [ ] All components received and tested
- [ ] Arduino programmed and flashing LED
- [ ] Motors rotate when manually spun
- [ ] Wheels are securely attached
- [ ] Platform is stable on all 4 wheels
- [ ] No loose connections on breadboard

### Motor Driver Setup Checklist

- [ ] L298N #1 wired to Motors 1 & 2
- [ ] L298N #2 wired to Motors 3 & 4
- [ ] All motor connections double-checked
- [ ] 12V battery connected (WITH SWITCH OFF)
- [ ] No short circuits visible

### Arduino Connections Checklist

- [ ] PWM pins (D3, D4, D6, D9, D10, D12) connected to L298N EN pins
- [ ] Direction pins (D2, D5, D7, D8, D11, D13) connected to L298N IN pins
- [ ] All GND connections secure
- [ ] Buck converter connected and outputting 5V
- [ ] Arduino powered on (green LED lit)

### Power System Checklist

- [ ] 12V battery connector secure
- [ ] Switch installed and working
- [ ] Buck converter testing 5V output
- [ ] No exposed wires (heat shrink applied)
- [ ] All solder joints are clean and strong
- [ ] Battery charger compatible with LiPo

### Motor Test Checklist

- [ ] Motor 1 spins forward/backward
- [ ] Motor 2 spins forward/backward
- [ ] Motor 3 spins forward/backward
- [ ] Motor 4 spins forward/backward
- [ ] All motors spin at similar speeds
- [ ] No grinding or unusual noises

### Final Assembly Checklist

- [ ] Trash can mounted securely on platform
- [ ] Camera mounted overhead at 2-2.5m height
- [ ] USB cable from camera to laptop
- [ ] USB cable from Arduino to laptop
- [ ] 12V battery inside protective enclosure
- [ ] All moving parts clear of obstacles

---

## Troubleshooting Connection Issues

### Motor Won't Spin

1. Check 12V battery connection (look for green LED on board)
2. Verify L298N connections to motor
3. Test with simple Arduino code: set IN1=HIGH, IN2=LOW, EN=255
4. Check motor encoder pin isn't creating drag
5. If still stuck: Manually rotate motor shaft — should rotate freely

### Erratic Motor Behavior

1. Check Arduino GND connection to L298N
2. Verify PWM signal (use multimeter if available)
3. Check for loose wires on breadboard
4. Reduce PWM value (high values may cause oscillation)
5. Ensure separate GND rail for power and Arduino

### Arduino Won't Recognize Motor Pins

1. Verify pins in code match physical connections
2. Use multimeter to check continuity
3. Try different GPIO pins
4. Reload Arduino sketch

### Battery Not Powering Motors

1. Check battery connector for corrosion
2. Test battery voltage with multimeter (should be 11V+)
3. Verify battery switch is ON
4. Check for broken wires at battery connector
5. Test with different motor driver

---

**All connections verified? Move on to Software Setup! 🚀**