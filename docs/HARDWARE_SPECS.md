# Hardware specifications

Overview of suggested components and wiring for the prototype. Adjust pins in `firmware/arduino_motor_control.ino` to match your board.

## Recommended parts

| Role | Example | Notes |
|------|---------|--------|
| Host | Raspberry Pi 4 | Or PC; Pi enables compact install |
| Camera | USB webcam or Pi Camera Module | Higher FPS helps fast throws |
| MCU | Arduino Uno / Nano | UART to host |
| Motor driver | DRV8825 / A4988 (steppers) or PWM servo driver | Match motor type |
| Motors | 2× steppers or 2× servos | Pan + tilt |

## Power

- **Logic**: 5 V USB to Arduino; 5 V (or 3.3 V per board) to host as per manufacturer
- **Motors**: Separate supply sized for stall current; common ground with logic
- **Decoupling**: Capacitors near drivers per module datasheet

## Pinout (default sketch)

| Arduino pin | Function |
|-------------|----------|
| D2 | Pan step (STEP) or pan servo PWM |
| D3 | Pan direction (DIR) or unused if servo |
| D4 | Tilt step |
| D5 | Tilt direction |
| GND | Common ground with motor driver logic |

Enable pins (`EN`), microstepping (`MS1`/`MS2`), and exact GPIO mapping depend on your driver breakout—update the `.ino` file accordingly.

## Serial

- **Baud**: 115200 (default; configurable in firmware and `config/default.yaml`)
- **Connection**: USB serial to host; use short, shielded USB if possible

## Safety

- Fuse or current-limited supply on motor rail
- Mechanical stops to prevent binding
- Do not leave powered unattended until travel limits are verified
