# Camera Calibration

This guide explains how to calibrate the overhead camera so that pixel
coordinates map accurately to real-world centimetres on the floor.

---

## Why calibrate?

The vision pipeline tracks objects in pixel space. The motor controller
needs to know how far (in real units) the platform must move. Calibration
provides:

1. **px_per_cm** — the pixel-to-centimetre scale factor (used in `trajectory/physics.py`).
2. **Lens distortion** coefficients (optional, but improves accuracy near frame edges).

---

## Method 1 — Checkerboard (recommended)

### Equipment

- OpenCV-compatible checkerboard (print or buy); 9×6 inner corners is standard.
- Flat surface at the play level.

### Steps

1. Place the checkerboard flat on the floor inside the camera's field of view.
2. Run the calibration script:

   ```bash
   python -c "
   from vision.calibrator import Calibrator
   import cv2

   cal = Calibrator(board_cols=9, board_rows=6, square_size_cm=2.5)
   cap = cv2.VideoCapture(0)

   count = 0
   while count < 15:
       ret, frame = cap.read()
       if not ret:
           break
       if cal.collect_frame(frame):
           count += 1
           print(f'Collected {count}/15')
       cv2.imshow('Calibration', frame)
       if cv2.waitKey(200) & 0xFF == ord('q'):
           break

   cap.release()
   cal.save('calibration_data/camera_calib.yaml')
   print('Saved.')
   "
   ```

3. Move the board slightly between captures to cover different positions.
4. The script saves `calibration_data/camera_calib.yaml` with `px_per_cm` and distortion data.

---

## Method 2 — Known distance (quick)

If you don't have a checkerboard, place two markers exactly **30 cm** apart
on the floor and measure their pixel separation in a captured frame:

```python
import cv2
import numpy as np

img = cv2.imread("frame.png")
# Click two points and measure pixel distance
# px_per_cm = pixel_distance / 30.0
```

Update `calibration_data/camera_calib.yaml`:

```yaml
px_per_cm: 21.3    # example; replace with your measurement
```

---

## Using calibration data

The `trajectory/physics.py` module reads `px_per_cm` from config. Update
`config/local.yaml`:

```yaml
calibration:
  px_per_cm: 21.3
```

The `vision.calibrator.Calibrator.load()` method can reload saved YAML:

```python
from vision.calibrator import Calibrator
data = Calibrator.load("calibration_data/camera_calib.yaml")
px_per_cm = data["px_per_cm"]
```

---

## Validation

After calibration, place an object at a known position (e.g., 50 cm from the
camera centre) and verify the pixel measurement matches expectation:

```
expected_pixels = 50 * px_per_cm
```

Re-run calibration if the error exceeds 5%.

---

## Tips

- Re-calibrate whenever you change camera height or angle.
- Use consistent, diffuse lighting; avoid direct sunlight causing shadows.
- A higher-quality checkerboard print reduces corner-detection errors.
- Save the date and lighting conditions as a comment in `camera_calib.yaml`.
