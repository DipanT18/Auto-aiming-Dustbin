from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path

from .camera_feed import CameraConfig, CameraFeed
from .object_detection import ObjectDetector
from .serial_controller import SerialController
from .trajectory_prediction import TrajectoryPredictor
from .utils import clamp, load_config

logger = logging.getLogger(__name__)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Auto-aiming Dustbin vision loop")
    p.add_argument(
        "--config",
        type=Path,
        default=Path("config/default.yaml"),
        help="Path to YAML config",
    )
    p.add_argument("--no-serial", action="store_true", help="Camera + vision only")
    p.add_argument("--show", action="store_true", help="Show OpenCV window")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    args = parse_args(argv)
    cfg = load_config(args.config)

    cam_cfg = CameraConfig.from_dict(cfg.get("camera", {}))
    det = ObjectDetector(cfg.get("detection", {}))
    tc = cfg.get("trajectory", {})
    traj = TrajectoryPredictor(
        history=int(tc.get("history", 8)),
        horizon_s=float(tc.get("horizon_s", 0.35)),
    )

    serial_ctrl: SerialController | None = None
    if not args.no_serial:
        serial_ctrl = SerialController(cfg.get("serial", {}))
        try:
            serial_ctrl.connect()
            logger.info("Serial: %s", serial_ctrl.ping())
        except Exception as e:
            logger.warning("Serial unavailable (%s); continuing without motors", e)
            serial_ctrl.close()
            serial_ctrl = None

    aim = cfg.get("aim", {})
    px_to_pan = float(aim.get("pixels_to_pan_steps", -0.15))
    px_to_tilt = float(aim.get("pixels_to_tilt_steps", -0.15))
    center_x = float(aim.get("center_x", cam_cfg.width / 2))
    center_y = float(aim.get("center_y", cam_cfg.height / 2))
    max_step = int(aim.get("max_step_per_frame", 80))

    with CameraFeed(cam_cfg) as cam:
        t0 = time.perf_counter()
        for frame in cam.frames():
            t = time.perf_counter() - t0
            dets = det.detect(frame)
            best = max(dets, key=lambda d: d.score, default=None)
            traj.update(t, best)
            pred = traj.predict_impact(t)

            target = pred if pred is not None else ((best.cx, best.cy) if best else None)
            if target is not None and serial_ctrl is not None:
                ex = target[0] - center_x
                ey = target[1] - center_y
                pan = int(clamp(ex * px_to_pan, -max_step, max_step))
                tilt = int(clamp(ey * px_to_tilt, -max_step, max_step))
                if pan or tilt:
                    if pan:
                        serial_ctrl.pan_steps(pan)
                    if tilt:
                        serial_ctrl.tilt_steps(tilt)

            if args.show:
                import cv2

                if best:
                    x, y, w, h = best.x, best.y, best.w, best.h
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.imshow("dustbin", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

    if serial_ctrl is not None:
        serial_ctrl.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
