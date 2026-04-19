# Trajectory Prediction Math

Explains the mathematics behind the parabola-fitting approach used in
`trajectory/predictor.py`.

---

## 1. The problem

A ball is thrown across the camera's field of view. We observe its pixel
position `(cx, cy)` in frames at times `t0, t1, t2, …`. We need to predict
where it will land before it gets there so the platform has time to move.

---

## 2. Physics model

Under gravity the ball follows a parabolic path:

```
cx(t) = vx₀·t + cx₀          (horizontal — linear)
cy(t) = ½·g_eff·t² + vy₀·t + cy₀   (vertical — quadratic)
```

Where `g_eff` is the apparent pixel-space gravity (depends on camera
orientation and `px_per_cm`).

Rather than estimating `g_eff` explicitly, we **fit** the quadratic directly
to the observed `cy` samples using NumPy's `polyfit`.

---

## 3. Curve fitting

Given `n ≥ 3` samples `(tᵢ, cxᵢ, cyᵢ)`:

```python
# Normalise time to reduce numerical error
ts = t_i - t_0          # array of relative times

# Fit quadratic to vertical axis
a, b, c = numpy.polyfit(ts, cy_samples, deg=2)

# Fit linear to horizontal axis
m, k = numpy.polyfit(ts, cx_samples, deg=1)
```

The fitted model:

```
cy(t) = a·t² + b·t + c
cx(t) = m·t + k
```

---

## 4. Finding the landing time

The ball lands when `cy(t) = floor_row` (the pixel row corresponding to the
floor level — typically `camera.height`).

Solve the quadratic:

```
a·t² + b·t + (c - floor_row) = 0
```

Using the quadratic formula:

```
discriminant = b² - 4·a·(c - floor_row)
t_land = (-b ± √discriminant) / (2·a)
```

We select the **future** root (t > t_now).

---

## 5. Predicting landing x-coordinate

Substitute `t_land` into the linear model:

```
x_land = m·t_land + k
```

The predicted landing point is `(x_land, floor_row)` in pixels.

---

## 6. Converting to real-world coordinates

```python
from trajectory.physics import DEFAULT_PX_PER_CM

x_land_cm = x_land / px_per_cm
```

This gives the distance in centimetres from the camera's left edge.

---

## 7. Timing: when to predict

| # Samples | Behaviour |
|-----------|-----------|
| < 3 | No prediction yet |
| 3–5 | Early prediction — less accurate, more time to move |
| 6–8 | More accurate prediction |
| > 8 | Buffer wraps; oldest samples discarded |

Tuning `trajectory.history` (default: 8) and `trajectory.min_samples`
(default: 3) in `config/default.yaml` controls this trade-off.

---

## 8. Fallback when discriminant < 0

If the quadratic has no real roots (the ball's arc doesn't reach
`floor_row` within the visible frame), the predictor falls back to
extrapolating `horizon_s` seconds ahead of the last observation.

---

## 9. Accuracy considerations

- **Frame rate**: Higher FPS reduces sample spacing, improving curve fit.
- **Noise**: Detection jitter adds noise to cy samples; the quadratic fit
  smooths this out better than pairwise velocity estimates.
- **Parabola assumption**: Works well for a top-down camera. For a side-view
  camera, `cx` may also be parabolic depending on throw angle.

---

## 10. Example (numbers)

Suppose at 30 fps the ball is observed at:

| t (s) | cx | cy |
|-------|----|----|
| 0.00 | 80 | 200 |
| 0.033 | 140 | 230 |
| 0.067 | 200 | 280 |
| 0.100 | 260 | 360 |

`polyfit` gives approximately:

```
cy(t) ≈ 4300·t² + 650·t + 200
```

Solving `cy(t) = 480`:

```
4300·t² + 650·t - 280 = 0
t_land ≈ 0.21 s
```

```
cx(t_land) ≈ 600·0.21 + 80 ≈ 206 px
```

Predicted landing: **(206, 480)**.
