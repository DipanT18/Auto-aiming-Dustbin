"""Camera calibration utilities.

Provides helpers to:

1. Collect checkerboard corner correspondences.
2. Run OpenCV's ``calibrateCamera`` to compute intrinsics and the
   pixel-to-centimetre scale factor.
3. Save / load calibration data to ``calibration_data/camera_calib.yaml``.

Typical usage::

    calibrator = Calibrator(board_cols=9, board_rows=6, square_size_cm=2.5)
    calibrator.collect_frame(frame)          # repeat for 10-20 frames
    result = calibrator.calibrate()
    calibrator.save("calibration_data/camera_calib.yaml")
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import cv2
import numpy as np
import yaml

logger = logging.getLogger(__name__)


class Calibrator:
    """
    Wrapper around OpenCV chessboard calibration.

    Parameters
    ----------
    board_cols:
        Number of *inner* corners along the X-axis of the checkerboard.
    board_rows:
        Number of *inner* corners along the Y-axis.
    square_size_cm:
        Physical side length of each square in centimetres.
    """

    def __init__(
        self,
        board_cols: int = 9,
        board_rows: int = 6,
        square_size_cm: float = 2.5,
    ) -> None:
        self._cols = board_cols
        self._rows = board_rows
        self._sq_cm = square_size_cm
        self._obj_points: list[np.ndarray] = []
        self._img_points: list[np.ndarray] = []
        self._img_size: tuple[int, int] | None = None

        # Pre-build the 3-D object-space grid (Z=0 plane).
        self._objp = np.zeros((board_cols * board_rows, 3), np.float32)
        self._objp[:, :2] = (
            np.mgrid[0:board_cols, 0:board_rows].T.reshape(-1, 2) * square_size_cm
        )

    def collect_frame(self, frame_bgr: np.ndarray) -> bool:
        """
        Detect checkerboard corners in *frame_bgr* and store them.

        Returns ``True`` if corners were found, ``False`` otherwise.
        """
        gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
        flags = cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_NORMALIZE_IMAGE
        found, corners = cv2.findChessboardCorners(gray, (self._cols, self._rows), flags)
        if not found:
            logger.debug("Checkerboard not found in this frame")
            return False

        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        corners_refined = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        self._obj_points.append(self._objp)
        self._img_points.append(corners_refined)
        if self._img_size is None:
            self._img_size = (gray.shape[1], gray.shape[0])
        logger.debug("Collected %d calibration frame(s)", len(self._obj_points))
        return True

    def calibrate(self) -> dict[str, Any]:
        """
        Run camera calibration and return a result dict.

        Raises ``RuntimeError`` if fewer than 3 frames have been collected.
        """
        if len(self._obj_points) < 3:
            raise RuntimeError(
                f"Need at least 3 calibration frames; got {len(self._obj_points)}"
            )
        assert self._img_size is not None
        rms, camera_matrix, dist_coeffs, _rvecs, _tvecs = cv2.calibrateCamera(
            self._obj_points, self._img_points, self._img_size, None, None
        )
        logger.info("Calibration RMS reprojection error: %.4f px", rms)

        # Estimate px-per-cm from the camera matrix focal lengths.
        # The focal length in pixels divided by 10 gives a rough px/cm estimate
        # assuming an object-to-camera distance of roughly 10× the focal length
        # in physical units — this is a placeholder; replace with a measured value.
        fx = float(camera_matrix[0, 0])
        fy = float(camera_matrix[1, 1])
        px_per_cm = (fx + fy) / 2.0 / 10.0  # approximate; refine after field measurement

        return {
            "rms": float(rms),
            "camera_matrix": camera_matrix.tolist(),
            "dist_coeffs": dist_coeffs.tolist(),
            "image_size": list(self._img_size),
            "px_per_cm": px_per_cm,
            "board_cols": self._cols,
            "board_rows": self._rows,
            "square_size_cm": self._sq_cm,
        }

    def save(self, path: str | Path, result: dict[str, Any] | None = None) -> None:
        """
        Save calibration result to a YAML file.

        If *result* is not provided, ``calibrate()`` is called first.
        """
        if result is None:
            result = self.calibrate()
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("w", encoding="utf-8") as f:
            yaml.dump(result, f, default_flow_style=False)
        logger.info("Calibration saved to %s", p)

    @staticmethod
    def load(path: str | Path) -> dict[str, Any]:
        """Load a previously saved calibration YAML."""
        with Path(path).open("r", encoding="utf-8") as f:
            return yaml.safe_load(f)
