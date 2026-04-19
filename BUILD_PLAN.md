# Build Plan — 2-Week Roadmap

A day-by-day guide to building the Auto-Aiming Dustbin from parts to a working demo.

---

## Week 1 — Hardware & Basic Control

| Day | Goal | Tasks |
|-----|------|-------|
| **1–2** | Build the omni-wheel platform frame | Cut / drill the base plate. Mount four omni-wheels at 90° intervals. Attach DC motors with brackets. Verify smooth manual rolling. |
| **3** | Wire motors to L298N drivers | Connect W1/W2 to Driver A, W3/W4 to Driver B. Wire ENA/ENB (PWM) and IN1–IN4 (direction) pins. Tie 12V motor supply and 5V logic supply with common GND. |
| **4** | Upload Arduino firmware and test serial | Flash `arduino/motor_controller.ino`. Open Serial Monitor at 115200 baud. Type `PING` → expect `OK PONG`. Type `MOVE 100 0` → wheels should spin. |
| **5** | Run motor test script from laptop | `python test_motors.py` — platform should execute the test sequence. Fix wiring if any wheel direction is wrong. |
| **6** | Mount USB camera overhead | Fix camera on stand 1.8–2.5 m above the play area. Run `python test_vision.py --show` to confirm feed is live. |
| **7** | Buffer day | Fix any wiring issues, redo cable management, charge batteries. |

---

## Week 2 — Vision, Prediction & Integration

| Day | Goal | Tasks |
|-----|------|-------|
| **8** | Basic detection | Tune `detection.min_area` and `detection.motion_threshold` in `config/local.yaml` until thrown objects are consistently detected. |
| **9** | Tracking & trajectory fit | Throw a ball through the field of view while `test_vision.py --show` runs. Verify the red prediction dot appears after 3+ frames. |
| **10** | Calibrate pixel → cm | Follow `docs/CAMERA_CALIBRATION.md`. Update `px_per_cm` in `calibration_data/camera_calib.yaml`. |
| **11** | First full integration run | `python main.py --config config/local.yaml --show`. Observe platform moving toward predicted landing. |
| **12** | Tune gains and latency | Adjust `motor_control.gain`, `motor_control.max_speed`, and `trajectory.horizon_s`. Log frame rate and motor latency. |
| **13** | Mount trash can & full test | Attach lightweight bin on platform. Throw balls and measure catch rate. Log and address failures. |
| **14** | Polish & demo prep | Record demo video. Label emergency stop (power switch). Rehearse explanation. Prepare backup video in case of live failure. |

---

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Component shipping delay | Order parts at least 1 week before Week 1 |
| Incorrect motor direction | Software-invertible in `motor_control/kinematics.py` |
| Low frame rate on laptop | Reduce resolution to 320×240; disable `--show` in production |
| Serial port conflicts | Close Arduino Serial Monitor before running Python scripts |
| Poor detection in bright light | Use a coloured ball and tune `detection.min_area`; avoid direct sunlight |
| Platform overshoots | Reduce `motor_control.gain` and increase `motor_control.deadband_px` |

---

## Demo checklist

- [ ] Platform moves in all four cardinal directions and diagonally
- [ ] Camera detects a thrown ball consistently across 3+ frames
- [ ] Prediction dot lands near the actual drop point
- [ ] Full system (`main.py`) tracks and moves before ball lands
- [ ] Emergency power switch is accessible and labelled
- [ ] Backup recorded video ready
- [ ] Marked throw zone on floor for reproducible demos
