# Troubleshooting Guide

Symptoms, causes, and fixes for common issues.

---

## Camera issues

| Symptom | Check | Fix |
|---------|-------|-----|
| `RuntimeError: Cannot open camera index 0` | Is another app using the camera? | Close browser, Zoom, etc. Try `index: 1` in config. |
| Black frame / very dark image | Exposure setting | Run `test_vision.py --show`; cover and uncover lens to force auto-exposure reset. |
| Blurry image | Focus ring or distance | Adjust camera focus; ensure camera is stable (no vibration). |
| Camera not listed on Linux | Permissions | `sudo usermod -aG video $USER` then log out and back in. |
| macOS: `AVFoundation capture` error | Permissions | System Preferences → Security & Privacy → Camera → allow Terminal/Python. |

---

## Serial / Arduino issues

| Symptom | Check | Fix |
|---------|-------|-----|
| `serial.SerialException: [Errno 2] No such file or directory` | Port config | Check `serial.port` in config; run `ls /dev/ttyUSB*` or `ls /dev/ttyACM*`. |
| No response to PING | Firmware not uploaded | Re-upload; verify baud matches (115200). |
| `PermissionError: [Errno 13]` on Linux | User not in dialout group | `sudo usermod -aG dialout $USER` then re-login. |
| `ERR PARSE` from Arduino | Wrong command format | Check command does not have extra spaces; verify firmware version matches docs. |
| Motors twitch then stop | Serial TX/RX swapped | Swap TX/RX wires between Arduino and driver, or use dedicated USB-serial cable. |
| Arduino resets on MOVE command | Power supply sag | Use a dedicated 12V supply; add 100µF capacitor across motor supply rails. |

---

## Detection issues

| Symptom | Check | Fix |
|---------|-------|-----|
| No detections (nothing moves) | Camera frame | Ensure `--show` and wave hand; if frame is still, camera isn't working. |
| Constant detections (jitter noise) | Lighting / threshold | Increase `detection.motion_threshold` (e.g., 40); avoid flickering lights. |
| Object detected but bbox too small | `min_area` too high | Decrease `detection.min_area` (e.g., 100); check object is in frame. |
| Detection lags behind object | `blur` too large | Reduce `detection.blur` to 3. |

---

## Trajectory prediction issues

| Symptom | Check | Fix |
|---------|-------|-----|
| `predict()` always returns `None` | Too few samples | Collect ≥ 3 detections; check `trajectory.min_samples`. |
| Prediction is way off target | `floor_row` wrong | Set `trajectory.floor_row` to the camera height (e.g., 480). |
| Prediction point oscillates | Noisy detections | Increase `trajectory.history` (e.g., 10–12); improve detection stability. |
| Discriminant < 0 warning | Ball arc too flat | Normal — predictor falls back to `horizon_s` extrapolation. |

---

## Motor / movement issues

| Symptom | Check | Fix |
|---------|-------|-----|
| Platform doesn't move | Serial connected? | Run `test_motors.py`; check for `OK PONG` response. |
| Only 1–2 wheels spin | Wiring | Check IN1/IN2 vs IN3/IN4 on the L298N; verify ENA/ENB are pulled high or driven. |
| Platform moves wrong direction | Wheel wiring polarity | Swap the two output wires on the offending L298N channel. |
| Platform overshoots target | Gain too high | Reduce `motor_control.gain` (e.g., 0.2); increase `motor_control.deadband_px`. |
| Platform doesn't reach target | Gain too low / max_speed too low | Increase `motor_control.gain` or `motor_control.max_speed`. |
| Motors get very hot | Stall current | Add mechanical stops; reduce `motor_control.max_speed`; check for binding. |

---

## Performance issues

| Symptom | Fix |
|---------|-----|
| Low frame rate (< 15 fps) | Reduce camera resolution (`width: 320`, `height: 240`); run without `--show`. |
| High latency (> 100 ms) | Shorter USB cable; reduce `trajectory.history`; disable logging. |
| Python import errors | Activate venv: `source .venv/bin/activate`; `pip install -r requirements.txt`. |
| `ModuleNotFoundError: trajectory` | Run from repo root: `python main.py`, not `python src/main.py`. |

---

## Collecting diagnostic information

Run with verbose logging:

```bash
python main.py --config config/local.yaml --show 2>&1 | tee run.log
```

Then inspect `run.log` for warning and error lines.

For serial issues, open Arduino Serial Monitor at 115200 and send commands manually.
