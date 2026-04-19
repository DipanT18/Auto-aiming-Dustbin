# Hardware Guide

Complete bill of materials, wiring diagrams, and assembly instructions for
the Auto-Aiming Dustbin omni-wheel platform.

---

## Bill of Materials

### Processing & Vision

| Component | Purpose | Approx cost (₹) |
|-----------|---------|-----------------|
| Laptop (any) | Runs Python + OpenCV | — (already have) |
| USB webcam (640×480, 30fps+) | Overhead object detection | ₹800–1500 |
| USB cable (type A–B or USB-C) | Camera to laptop | ₹100 |

### Microcontroller

| Component | Purpose | Approx cost (₹) |
|-----------|---------|-----------------|
| Arduino Uno / Mega **or** ESP32 DevKit | Motor control via serial | ₹400–800 |
| USB cable (Arduino to laptop) | Serial communication | ₹100 |

### Motion Platform

| Component | Qty | Purpose | Approx cost (₹) |
|-----------|-----|---------|-----------------|
| 100 mm omni-directional wheels | 4 | Move in any direction | ₹250–400 each |
| 12V DC motor with gearbox (~200 RPM) | 4 | Drive each wheel | ₹300–500 each |
| L298N dual-channel motor driver | 2 | Control 2 motors each | ₹80–120 each |
| 20×40 mm aluminium extrusion / plywood (400×400 mm) | 1 | Platform base | ₹200–400 |
| Motor mounting brackets | 4 | Fix motors to frame | ₹50 each |
| M3/M4 bolts, nuts, washers | assorted | Assembly | ₹100 |

### Power

| Component | Spec | Approx cost (₹) |
|-----------|------|-----------------|
| 3S LiPo battery (11.1V, 3000–5000 mAh) | Motor power | ₹800–1500 |
| XT60 connector + wiring | Battery connection | ₹100 |
| Buck converter (12V → 5V, 3A) | Arduino power from battery | ₹80–150 |
| Power switch (rocker, 10A) | Emergency stop | ₹50 |
| Blade fuse holder + 5A fuse | Motor rail protection | ₹60 |

### Miscellaneous

| Item | Purpose |
|------|---------|
| Lightweight plastic bin (< 1 kg) | The bin itself |
| Camera stand / tripod (height ≥ 2 m) | Overhead camera mount |
| Jumper wires (male–male, male–female) | Prototyping connections |
| Breadboard or terminal blocks | Clean wiring |
| Zip ties | Cable management |
| Rubber feet (4×) | Stop platform sliding on smooth floors |

**Estimated total (excluding laptop): ₹6,000–10,000**

---

## Wiring Diagram

### Power distribution

```
[LiPo 3S 11.1V] ──┬──[5A fuse]──[Power switch]──┬── 12V motor rail
                  │                               │
                  │                         [L298N A] (W1, W2)
                  │                         [L298N B] (W3, W4)
                  │
                  └──[Buck 12V→5V]──┬── Arduino Vin (5V)
                                    └── Common GND (all modules)
```

> **Important**: All GND connections must be tied together — Arduino GND,
> L298N logic GND, and battery negative.

---

### L298N to Arduino — Motor Driver A (front wheels)

```
L298N A                    Arduino Uno / Mega
─────────────────────────────────────────────
ENA  ──────────────────── D10 (PWM)   W1 speed
IN1  ──────────────────── D2          W1 direction
IN2  ──────────────────── D3          W1 direction
ENB  ──────────────────── D11 (PWM)   W2 speed
IN3  ──────────────────── D4          W2 direction
IN4  ──────────────────── D5          W2 direction
GND  ──────────────────── Arduino GND
5V   ──────────────────── Arduino 5V (logic supply)
12V  ──────────────────── 12V motor rail
```

### L298N to Arduino — Motor Driver B (rear wheels)

```
L298N B                    Arduino Uno / Mega
─────────────────────────────────────────────
ENA  ──────────────────── D6  (PWM)   W3 speed
IN1  ──────────────────── D7          W3 direction
IN2  ──────────────────── D8          W3 direction
ENB  ──────────────────── D9  (PWM)   W4 speed
IN3  ──────────────────── D12         W4 direction
IN4  ──────────────────── D13         W4 direction
GND  ──────────────────── Arduino GND
5V   ──────────────────── Arduino 5V
12V  ──────────────────── 12V motor rail
```

---

### Platform wheel layout (top view)

```
          FRONT (direction of +Vy)
    ┌──────────────────────────┐
    │  [W1]              [W2]  │
    │  (front-left)  (front-right)
    │                          │
    │        [Arduino]         │
    │        [L298N×2]         │
    │                          │
    │  [W4]              [W3]  │
    │  (rear-left)  (rear-right)│
    └──────────────────────────┘
          REAR
```

Each wheel is mounted at 45° from the chassis edge so rollers engage in
orthogonal directions, enabling X-drive (holonomic) motion.

---

## Arduino pin summary

| Arduino pin | Function |
|-------------|----------|
| D2, D3 | W1 direction (IN1, IN2) |
| D4, D5 | W2 direction (IN3, IN4) |
| D6 (PWM) | W3 speed (ENA) |
| D7, D8 | W3 direction |
| D9 (PWM) | W4 speed (ENB) |
| D10 (PWM) | W1 speed (ENA) |
| D11 (PWM) | W2 speed (ENB) |
| D12, D13 | W4 direction |
| 5V | L298N logic supply |
| GND | Common ground |

---

## Assembly steps

1. **Cut or source the base plate** — 400×400 mm plywood or aluminium.
2. **Mark wheel positions** — 45° diagonals at each corner (approx 60 mm from edge).
3. **Mount motors** — bolt gearboxes to brackets, brackets to base.
4. **Attach omni-wheels** — press onto motor shafts; secure with grub screws.
5. **Install L298N boards** — centre of the base; ensure clearance for wires.
6. **Wire motors to L298N** — match polarity; motors can be reversed in firmware.
7. **Route power** — fuse → switch → L298N 12V terminals + buck converter input.
8. **Wire Arduino** — per the table above; double-check PWM-capable pins.
9. **Verify before powering** — multimeter check: no shorts across 12V/GND.
10. **Attach bin** — lightweight bin centred on top; use hook-and-loop tape for removability.

---

## Safety

- Always turn off motor power before touching wiring.
- Use a current-limited bench supply during initial testing.
- Install a fuse on the motor rail.
- Add mechanical stops if the platform can reach edges of the play area.
