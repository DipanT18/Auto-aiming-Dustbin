# Arduino Programming Guide

Step-by-step instructions for uploading and testing the motor controller firmware.

---

## 1. Install Arduino IDE 2.x

Download from [arduino.cc/en/software](https://www.arduino.cc/en/software).

---

## 2. Choose your firmware

| Board | File |
|-------|------|
| Arduino Uno / Mega / Nano | `arduino/motor_controller.ino` |
| ESP32 DevKit | `arduino/motor_controller_esp32.ino` |

---

## 3. Install board support (ESP32 only)

1. Open **File → Preferences**.
2. Paste in the **Additional Board Manager URLs** field:
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
3. Open **Tools → Board → Boards Manager**, search "esp32", and install the Espressif package.

---

## 4. Upload the firmware

1. Open the appropriate `.ino` file in Arduino IDE.
2. Select **Tools → Board** → your board.
3. Select **Tools → Port** → the port shown when the Arduino is plugged in:
   - Windows: `COM3`, `COM4`, …
   - macOS: `/dev/cu.usbserial-…` or `/dev/cu.SLAB_USBtoUART`
   - Linux: `/dev/ttyUSB0` or `/dev/ttyACM0`
4. Click **Upload** (Ctrl+U) and wait for "Done uploading."

---

## 5. Verify with Serial Monitor

1. Open **Tools → Serial Monitor** (Ctrl+Shift+M).
2. Set baud rate to **115200**.
3. Type `PING` and press Enter.

Expected response:

```
OK PONG
```

4. Type `MOVE 100 0` — the front-left and rear-left wheels should spin forward.
5. Type `STOP` — all motors halt.

---

## 6. Adjusting pin assignments

Open the `.ino` file and edit the `#define` lines at the top:

```cpp
// Motor W1 — front-left
#define W1_EN  10    // PWM-capable pin for speed
#define W1_IN1  2    // direction pin 1
#define W1_IN2  3    // direction pin 2
```

Refer to `docs/HARDWARE_GUIDE.md` for the default wiring table.

> **Do not use pins 0 and 1** (TX/RX) — they are reserved for serial
> communication with the laptop.

---

## 7. Motor direction inversion

If a wheel spins the wrong way, swap `W#_IN1` and `W#_IN2` for that motor
**either** in the `.ino` defines **or** by swapping the two motor wires in
the L298N output terminals (easier during testing).

---

## 8. Common upload errors

| Error | Cause | Fix |
|-------|-------|-----|
| `avrdude: stk500_recv()` | Wrong board or baud | Check **Tools → Board** and **Tools → Port** |
| `Port busy` | Serial Monitor still open | Close Serial Monitor before uploading |
| Sketch too large | Uno flash full | Use Mega or remove unused code |
| ESP32: `Failed to connect` | Boot not held | Hold BOOT button while clicking Upload; release after "Connecting…" |

---

## 9. Testing from Python

After uploading, close the Serial Monitor and run:

```bash
python test_motors.py
```

This sends the full MOVE sequence via Python and logs wheel speeds.

---

## 10. Serial protocol reference

See `arduino/README.md` and `docs/COMMUNICATION_PROTOCOL.md` for the full
command reference and response codes.
