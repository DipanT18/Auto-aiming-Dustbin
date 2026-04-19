"""Auto-Aiming Dustbin — main application entry point.

Architecture
------------
Laptop (Python + OpenCV)  ←USB serial→  Arduino (omni-wheel motor control)

Loop
----
capture → detect → track → predict → move

Usage
-----
    python main.py                        # use config/default.yaml
    python main.py --config config/local.yaml --show
    python main.py --no-serial            # vision only, no Arduino
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
from motor_control.serial_comm import SerialComm
from motor_control.controller import MotorController

logger = logging.getLogger(__name__)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Auto-Aiming Dustbin — Laptop + Arduino edition"
    )
    p.add_argument(
        "--config",
        type=Path,
        default=Path("config/default.yaml"),
        help="Path to YAML config file (default: config/default.yaml)",
    )
    p.add_argument(
        "--no-serial",
        action="store_true",
        help="Run vision pipeline only (no Arduino required)",
    )
    p.add_argument(
        "--show",
        action="store_true",
        help="Display OpenCV window with detection overlay",
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )
    args = parse_args(argv)
    cfg = load_config(args.config)

    # ── Initialise subsystems ────────────────────────────────────────────────

    cam_cfg = CameraConfig.from_dict(cfg.get("camera", {}))
    detector = ObjectDetector(cfg.get("detection", {}))
    tracker = ObjectTracker.from_config(cfg.get("tracker", {}))
    traj_cfg = cfg.get("trajectory", {})
    predictor = TrajectoryPredictor.from_config({
        **traj_cfg,
        "floor_row": float(cam_cfg.height),
    })

    motor_ctrl: MotorController | None = None
    serial_comm: SerialComm | None = None
    if not args.no_serial:
        serial_comm = SerialComm(cfg.get("serial", {}))
        try:
            serial_comm.connect()
            reply = serial_comm.ping()
            logger.info("Arduino: %s", reply)
            motor_ctrl = MotorController(serial_comm, cfg.get("motor_control", {}))
        except Exception as exc:
            logger.warning("Serial unavailable (%s) — continuing without motors", exc)
            if serial_comm is not None:
                serial_comm.close()
            serial_comm = None

    # ── Main loop ────────────────────────────────────────────────────────────

    logger.info("Starting main loop. Press Ctrl-C or 'q' to quit.")
    t0 = time.perf_counter()
    frames_processed = 0

    try:
        with CameraFeed(cam_cfg) as cam:
            for frame in cam.frames():
                t = time.perf_counter() - t0
                frames_processed += 1

                # Detect
                dets = detector.detect(frame)
                best = max(dets, key=lambda d: d.score, default=None)

                # Track
                track = tracker.update(best)

                # Predict
                if best is not None:
                    predictor.add(t, best.cx, best.cy)
                pred = predictor.predict()

                # Move
                target = pred if pred is not None else (
                    (best.cx, best.cy) if best is not None else None
                )
                if target is not None and motor_ctrl is not None:
                    motor_ctrl.move_to(target[0], target[1])

                # Optional display
                if args.show:
                    import cv2
                    if best:
                        x, y, w, h = best.x, best.y, best.w, best.h
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    if pred:
                        cv2.circle(frame, (int(pred[0]), int(pred[1])), 8, (0, 0, 255), -1)
                    cv2.imshow("Auto-Aiming Dustbin", frame)
                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        break

    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    finally:
        if motor_ctrl is not None:
            motor_ctrl.stop()
        if serial_comm is not None:
            serial_comm.close()
        elapsed = time.perf_counter() - t0
        if elapsed > 0:
            logger.info(
                "Processed %d frames in %.1fs (%.1f fps)",
                frames_processed,
                elapsed,
                frames_processed / elapsed,
            )

    return 0


if __name__ == "__main__":
    sys.exit(main())
