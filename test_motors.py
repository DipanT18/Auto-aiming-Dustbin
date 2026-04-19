"""Motor test script — exercises serial communication and kinematics without vision.

Run with:
    python test_motors.py [--config config/default.yaml] [--port /dev/ttyUSB0]

The script sends a sequence of MOVE commands over serial and prints the responses.
No camera is required.
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path

from vision.utils import load_config
from motor_control.serial_comm import SerialComm
from motor_control.kinematics import compute_wheel_speeds

logger = logging.getLogger(__name__)

_TEST_MOVES: list[tuple[int, int, float]] = [
    (100, 0, 0.5),     # move right
    (-100, 0, 0.5),    # move left
    (0, 100, 0.5),     # move forward
    (0, -100, 0.5),    # move backward
    (80, 80, 0.5),     # move diagonally
    (0, 0, 0.3),       # stop
]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Motor test (serial to Arduino, no vision)")
    p.add_argument("--config", type=Path, default=Path("config/default.yaml"))
    p.add_argument("--port", type=str, default=None, help="Override serial port")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    args = parse_args(argv)
    cfg = load_config(args.config)

    serial_cfg = dict(cfg.get("serial", {}))
    if args.port:
        serial_cfg["port"] = args.port

    logger.info("Connecting to Arduino on %s @ %s baud...",
                serial_cfg.get("port"), serial_cfg.get("baud_rate", 115200))

    with SerialComm(serial_cfg) as comm:
        reply = comm.ping()
        logger.info("PING response: %r", reply)
        if "PONG" not in reply:
            logger.error("Did not get PONG — check connection and baud rate")
            return 1

        for vx, vy, duration in _TEST_MOVES:
            speeds = compute_wheel_speeds(float(vx), float(vy))
            logger.info(
                "MOVE vx=%+4d vy=%+4d  → W1=%+4d W2=%+4d W3=%+4d W4=%+4d",
                vx, vy, speeds.w1, speeds.w2, speeds.w3, speeds.w4,
            )
            if vx == 0 and vy == 0:
                comm.stop()
            else:
                comm.move(vx, vy)
            time.sleep(duration)

        comm.stop()
        logger.info("Motor test complete — all motors stopped.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
