from __future__ import annotations

"""Video writing utilities."""

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional, Tuple

import cv2

from .validate import ImageValidationResult


@dataclass
class BuildReport:
    frames_written: int
    skipped: int


def build_video(
    images: Iterable[ImageValidationResult],
    output: Path,
    fps: int,
    codec: str,
    size: Optional[Tuple[int, int]] = None,
    strict: bool = False,
    dry_run: bool = False,
) -> BuildReport:
    """Build a timelapse video from *images*."""
    images = [img for img in images if img.is_valid]
    if not images:
        raise ValueError("no valid images to build video")

    frames_written = 0
    skipped = 0

    if size is None:
        first = cv2.imread(str(images[0].path))
        if first is None:
            raise ValueError("cannot read first image")
        h, w = first.shape[:2]
        size = (w, h)

    writer = None if dry_run else cv2.VideoWriter(
        str(output), cv2.VideoWriter_fourcc(*codec), fps, size
    )

    for img in images:
        frame = cv2.imread(str(img.path))
        if frame is None or frame.size == 0:
            if strict:
                raise ValueError(f"unreadable image {img.path}")
            skipped += 1
            continue
        if (frame.shape[1], frame.shape[0]) != size:
            frame = cv2.resize(frame, size)
        if not dry_run:
            writer.write(frame)
        frames_written += 1

    if writer is not None:
        writer.release()

    return BuildReport(frames_written=frames_written, skipped=skipped)
