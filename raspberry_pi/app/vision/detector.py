"""Detector module — re-exports :class:`vision.object_detection.ObjectDetector`.

Provides the ``vision.detector`` import path described in the project
structure documentation while delegating all work to the existing
:class:`ObjectDetector` implementation.
"""

from __future__ import annotations

from .object_detection import Detection, ObjectDetector  # re-export

__all__ = ["Detector", "Detection", "ObjectDetector"]


class Detector(ObjectDetector):
    """
    Alias for :class:`ObjectDetector` exposed under the ``detector`` module.

    All detection logic lives in :class:`~vision.object_detection.ObjectDetector`;
    this class exists purely for import-path consistency.
    """
