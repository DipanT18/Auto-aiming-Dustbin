# Prototype setup guide

This guide walks through assembling and running the Auto-aiming Dustbin prototype: Raspberry Pi (or PC) vision stack, Arduino motor driver, and mechanical mounting.

## Prerequisites

- **Compute**: Raspberry Pi 4 (recommended) or Linux/Windows PC with USB camera
- **MCU**: Arduino Uno/Nano (or compatible) flashed with `firmware/arduino_motor_control.ino`
- **Motors**: Two-axis pan/tilt or X/Y platform driven by steppers or servos (match wiring to `docs/HARDWARE_SPECS.md`)
- **Python**: 3.10+

## Software setup

1. Clone the repository and create a virtual environment:

   ```bash
   cd Auto-aiming-Dustbin
   python3 -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Copy `config/default.yaml` to `config/local.yaml` and adjust camera index, serial port, and detection settings.

3. Flash the Arduino with the motor sketch and verify the serial baud rate matches `config/default.yaml` (`serial.baud_rate`).

4. Run calibration (see `docs/CALIBRATION_GUIDE.md`) once the hardware is stable.

5. Start the vision pipeline:

   ```bash
   python -m vision.main --config config/local.yaml
   ```

## Physical checklist

- Camera fixed above the opening, aimed at the throw zone; avoid glare and motion blur
- Bin opening unobstructed; safe clearance for moving parts
- USB cables secured; strain relief on the camera ribbon/USB if used
- Emergency stop: unplug motor power if anything binds

## Troubleshooting

| Symptom | Things to check |
|--------|------------------|
| No camera | Device index in config; `ls /dev/video*` (Linux); other apps closed |
| No serial | Correct port (`/dev/ttyUSB0`, `COM3`, etc.); baud; only one program open |
| Jittery aim | Lighting, exposure, calibration; reduce PID gains in firmware if applicable |
| Misses throws | Retrain or tune detector; revisit trajectory calibration |

For protocol details, see `docs/COMMUNICATION_PROTOCOL.md`.
