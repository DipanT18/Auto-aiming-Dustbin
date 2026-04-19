"""Vision system test script — exercises camera + detection without motors.

Run with:
    python test_vision.py [--config config/default.yaml] [--show]

Press 'q' to quit the window if --show is used.
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path

from vision.camera_feed import CameraConfig, CameraFeed
from vision.object_detection import ObjectDetector
from vision.tracker import ObjectTracker
from vision.utils import load_config
from trajectory.predictor import TrajectoryPredictor

logger = logging.getLogger(__name__)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Vision system test (no motors)")
    p.add_argument("--config", type=Path, default=Path("config/default.yaml"))
    p.add_argument("--show", action="store_true", help="Show OpenCV window")
    p.add_argument("--frames", type=int, default=0, help="Stop after N frames (0=unlimited)")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    args = parse_args(argv)
    cfg = load_config(args.config)

    cam_cfg = CameraConfig.from_dict(cfg.get("camera", {}))
    detector = ObjectDetector(cfg.get("detection", {}))
    tracker = ObjectTracker.from_config(cfg.get("tracker", {}))
    traj_cfg = cfg.get("trajectory", {})
    predictor = TrajectoryPredictor.from_config({
        **traj_cfg,
        "floor_row": float(cam_cfg.height),
    })

    t0 = time.perf_counter()
    n = 0

    try:
        with CameraFeed(cam_cfg) as cam:
            for frame in cam.frames():
                t = time.perf_counter() - t0
                n += 1

                dets = detector.detect(frame)
                best = max(dets, key=lambda d: d.score, default=None)
                tracker.update(best)
                if best is not None:
                    predictor.add(t, best.cx, best.cy)
                pred = predictor.predict()

                if best:
                    logger.info(
                        "Frame %4d  det=(%.1f, %.1f)  pred=%s",
                        n, best.cx, best.cy,
                        f"({pred[0]:.1f}, {pred[1]:.1f})" if pred else "None",
                    )

                if args.show:
                    import cv2
                    if best:
                        x, y, w, h = best.x, best.y, best.w, best.h
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    if pred:
                        cv2.circle(frame, (int(pred[0]), int(pred[1])), 8, (0, 0, 255), -1)
                    cv2.imshow("Vision Test", frame)
                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        break

                if args.frames and n >= args.frames:
                    break

    except KeyboardInterrupt:
        pass

    elapsed = time.perf_counter() - t0
    logger.info("Processed %d frames in %.1fs (%.1f fps)", n, elapsed, n / elapsed if elapsed else 0)
    return 0


if __name__ == "__main__":
    sys.exit(main())
