"""Demo mode — run the full vision + prediction pipeline without Arduino hardware.

Simulates a thrown object using a synthetic parabolic trajectory so you can
verify the detection, tracking, and prediction pipeline on any laptop.

Usage
-----
    python demo.py               # synthesised object, no window
    python demo.py --show        # show OpenCV window
    python demo.py --config config/default.yaml --show
"""

from __future__ import annotations

import argparse
import logging
import math
import sys
import time
from pathlib import Path

import cv2
import numpy as np

from vision.object_detection import Detection, ObjectDetector
from vision.tracker import ObjectTracker
from vision.utils import load_config
from trajectory.predictor import TrajectoryPredictor

logger = logging.getLogger(__name__)

WIDTH, HEIGHT = 640, 480
FPS = 30
TOTAL_FRAMES = 90  # ~3 seconds


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Auto-Aiming Dustbin — demo mode (no hardware)")
    p.add_argument("--config", type=Path, default=Path(__file__).parent.parent / "config" / "local.yaml")
    p.add_argument("--show", action="store_true", help="Display OpenCV window")
    return p.parse_args(argv)


def _synthetic_throw(frame_idx: int, total: int) -> tuple[int, int] | None:
    """Return pixel (cx, cy) for a simulated parabolic throw, or None if off-screen."""
    t = frame_idx / FPS
    flight_time = total / FPS
    if t > flight_time:
        return None
    # horizontal: left to right
    cx = int(WIDTH * 0.1 + (WIDTH * 0.8) * (t / flight_time))
    # vertical: parabola — starts at mid-height, peaks, then falls to bottom
    vy0 = -HEIGHT * 0.8 / (flight_time / 2)
    cy = int(HEIGHT * 0.5 + vy0 * t + 0.5 * 250 * t * t)
    cy = min(cy, HEIGHT - 1)
    return cx, cy


def _draw_object(frame: np.ndarray, cx: int, cy: int) -> None:
    cv2.circle(frame, (cx, cy), 15, (0, 165, 255), -1)


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    args = parse_args(argv)
    cfg = load_config(args.config)

    traj_cfg = cfg.get("trajectory", {})
    predictor = TrajectoryPredictor.from_config({**traj_cfg, "floor_row": float(HEIGHT)})
    tracker = ObjectTracker.from_config(cfg.get("tracker", {}))

    t0 = time.perf_counter()

    for i in range(TOTAL_FRAMES):
        t = time.perf_counter() - t0
        pos = _synthetic_throw(i, TOTAL_FRAMES)

        frame = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
        cv2.putText(
            frame, "DEMO MODE — no hardware needed", (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1
        )

        det: Detection | None = None
        if pos is not None:
            cx, cy = pos
            det = Detection(x=cx - 15, y=cy - 15, w=30, h=30, label="ball")
            predictor.add(t, float(cx), float(cy))
            if args.show:
                _draw_object(frame, cx, cy)

        tracker.update(det)
        pred = predictor.predict()

        if pred is not None:
            logger.info("Frame %3d  pos=%s  predicted_landing=(%.1f, %.1f)", i, pos, *pred)
            if args.show:
                cv2.circle(frame, (int(pred[0]), int(pred[1])), 10, (0, 0, 255), -1)
                cv2.putText(
                    frame,
                    f"Land: ({int(pred[0])}, {int(pred[1])})",
                    (int(pred[0]) + 12, int(pred[1])),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1,
                )
        else:
            logger.info("Frame %3d  pos=%s  (collecting samples...)", i, pos)

        if args.show:
            cv2.imshow("Auto-Aiming Dustbin — Demo", frame)
            if cv2.waitKey(int(1000 / FPS)) & 0xFF == ord("q"):
                break

        time.sleep(max(0.0, (1.0 / FPS) - (time.perf_counter() - t0 - i / FPS)))

    if args.show:
        cv2.destroyAllWindows()

    logger.info("Demo complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
