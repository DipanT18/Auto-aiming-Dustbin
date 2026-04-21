"""Camera module — convenience wrapper around :class:`vision.camera_feed.CameraFeed`.

Exposes a simplified API aligned with the project structure described in
the problem statement while reusing the existing :class:`CameraFeed`
implementation so no functionality is duplicated.
"""

from __future__ import annotations

from .camera_feed import CameraConfig, CameraFeed  # re-export

__all__ = ["Camera", "CameraConfig", "CameraFeed"]


class Camera(CameraFeed):
    """
    Thin subclass of :class:`CameraFeed` that adds convenience helpers.

    Intended as the public entry point for callers that prefer the
    ``camera.Camera`` import path described in the project structure docs.
    """

    def warm_up(self, n_frames: int = 5) -> None:
        """
        Discard the first *n_frames* frames.

        Some cameras need a few frames to auto-adjust exposure / white
        balance before returning a useful image.
        """
        for _ in range(n_frames):
            self.read()
