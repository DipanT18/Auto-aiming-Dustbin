# Arduino Firmware

Two firmware variants are provided for the Auto-Aiming Dustbin motor controller.

| Directory | File | Board target |
|-----------|------|--------------|
| `uno/` | `auto_aiming_uno.ino` | Arduino Uno / Mega / Nano |
| `esp32/` | `auto_aiming_esp32.ino` | ESP32 (any 38-pin DevKit) |
| `mega/` | — | Placeholder (see `mega/README.md`) |

Shared protocol constants live in `common/protocol.h` and are included by both sketches.

## Upload instructions

1. Install the [Arduino IDE](https://www.arduino.cc/en/software) (2.x recommended).
2. Open the `.ino` file for your board:
   - Uno / Mega → `uno/auto_aiming_uno.ino`
   - ESP32      → `esp32/auto_aiming_esp32.ino`
3. Select **Tools → Board** and choose your board.
4. Select **Tools → Port** and choose the correct COM port.
5. Click **Upload** (Ctrl+U).

## Serial protocol

Both sketches implement the same line-oriented ASCII protocol at **115200 baud**.
Constants are defined in `common/protocol.h`.

### Commands (Pi → Arduino)

| Command | Description |
|---------|-------------|
| `MOVE <vx> <vy>` | Drive platform; `vx`, `vy` are signed integers in -255..255 |
| `STOP` | Halt all motors immediately |
| `HOME` | Return to origin (STOP in this firmware) |
| `PING` | Health check |

### Responses (Arduino → Pi)

| Response | Meaning |
|----------|---------|
| `OK PONG` | Reply to `PING` |
| `OK` | Command accepted |
| `ERR PARSE` | Command not recognised |

## Pin assignments

### Uno / Mega (uno/auto_aiming_uno.ino)

| Signal | Arduino pin |
|--------|-------------|
| W1 EN (front-left) | D10 (PWM) |
| W1 IN1 / IN2 | D2 / D3 |
| W2 EN (front-right) | D11 (PWM) |
| W2 IN1 / IN2 | D4 / D5 |
| W3 EN (rear-right) | D6 (PWM) |
| W3 IN1 / IN2 | D7 / D8 |
| W4 EN (rear-left) | D9 (PWM) |
| W4 IN1 / IN2 | D12 / D13 |

### ESP32 (esp32/auto_aiming_esp32.ino)

| Signal | GPIO |
|--------|------|
| W1 EN (front-left) | GPIO32 |
| W1 IN1 / IN2 | GPIO25 / GPIO26 |
| W2 EN (front-right) | GPIO33 |
| W2 IN1 / IN2 | GPIO27 / GPIO14 |
| W3 EN (rear-right) | GPIO15 |
| W3 IN1 / IN2 | GPIO12 / GPIO13 |
| W4 EN (rear-left) | GPIO4 |
| W4 IN1 / IN2 | GPIO16 / GPIO17 |

## Quick test

Once the firmware is uploaded, open the Arduino IDE **Serial Monitor** at 115200 baud and type:

```
PING
```

You should see:

```
OK PONG
```

Then send:

```
MOVE 100 0
```

The platform should move sideways.  Send `STOP` to halt.

## Adjusting pin assignments

Edit the `#define` lines at the top of the `.ino` file to match your wiring.
Do **not** use pins 0 and 1 (TX/RX) — they are reserved for serial communication.
