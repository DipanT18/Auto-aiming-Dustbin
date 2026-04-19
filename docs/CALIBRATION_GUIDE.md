# Calibration guide

Calibration maps camera pixels to pan/tilt commands so thrown objects are intercepted at the bin opening.

## What you need

- Working camera feed (`vision.camera_feed`)
- Serial link to Arduino (`vision.serial_controller`)
- Known reference: a static target or marked points at the rim

## Steps

1. **Camera**: Fix exposure and white balance if possible (reduces drift). Set `camera.width`, `camera.height`, and `camera.index` in config.

2. **Collect correspondences**: For several pixel positions \((u, v)\), command the rig until the laser crosshair (or mechanical pointer) aligns, record pan/tilt steps or angles \((p, t)\).

3. **Fit a model**: Store coefficients in `calibration/` (e.g. affine or polynomial). `vision.utils` can load `calibration/transform.npz` when you add the loader in `main.py`.

4. **Trajectory**: Record short clips of throws; tune `trajectory_prediction` time horizon and gravity/scale factors so predicted impact matches the rim plane.

5. **Validate**: Repeat with new throws; adjust smoothing and deadband in config.

## Files

- Save numeric tables under `calibration/` (gitignored by default for machine-specific data)
- Keep a short note of date and lighting conditions when you calibrated

See also `docs/COMMUNICATION_PROTOCOL.md` for test moves over serial.
