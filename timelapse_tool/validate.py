from __future__ import annotations

"""Image validation utilities."""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Pattern

import cv2

from .io_utils import iter_files
from .parsing import parse_timestamp


@dataclass
class ImageValidationResult:
    """Information about a validated image file."""

    path: Path
    timestamp: Optional[datetime]
    size_bytes: int
    readable: bool
    width: Optional[int]
    height: Optional[int]
    reasons: List[str]
    is_flat: bool = False

    @property
    def is_valid(self) -> bool:
        return not self.reasons


def validate_image(
    path: Path,
    pattern: Pattern[str],
    ts_format: str,
    min_bytes: int,
    flat_threshold: Optional[float] = None,
) -> ImageValidationResult:
    """Validate a single image file."""
    reasons: List[str] = []
    result = parse_timestamp(path.name, pattern, ts_format)
    timestamp = result.timestamp
    if not result.matched:
        reasons.append("pattern")
    elif timestamp is None:
        reasons.append("timestamp")

    try:
        size_bytes = path.stat().st_size
    except OSError:
        size_bytes = 0
    if size_bytes < min_bytes:
        reasons.append("size")

    readable = False
    width = height = None
    is_flat = False
    frame = None
    if size_bytes >= min_bytes:
        frame = cv2.imread(str(path))
        if frame is None or frame.size == 0:
            reasons.append("unreadable")
        else:
            readable = True
            height, width = frame.shape[:2]
            if flat_threshold is not None:
                mean, std = cv2.meanStdDev(frame)
                mean_v = float(mean.mean())
                std_v = float(std.mean())
                if std_v < flat_threshold or mean_v < 5 or mean_v > 250:
                    is_flat = True
    return ImageValidationResult(
        path=path,
        timestamp=timestamp,
        size_bytes=size_bytes,
        readable=readable,
        width=width,
        height=height,
        reasons=reasons,
        is_flat=is_flat,
    )


def scan_folder(
    folder: Path,
    pattern: Pattern[str],
    ts_format: str,
    min_bytes: int,
    flat_threshold: Optional[float] = None,
) -> List[ImageValidationResult]:
    """Validate all files in *folder*."""
    return [
        validate_image(p, pattern, ts_format, min_bytes, flat_threshold)
        for p in iter_files(folder)
    ]
