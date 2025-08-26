from __future__ import annotations

"""Gap detection between images."""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, List

from .validate import ImageValidationResult


@dataclass
class Gap:
    prev_file: Path
    prev_ts: datetime
    next_file: Path
    next_ts: datetime
    gap_minutes: float


def find_gaps(images: Iterable[ImageValidationResult], gap_minutes: int) -> List[Gap]:
    """Return gaps greater than ``gap_minutes`` between consecutive images."""
    imgs = [img for img in images if img.timestamp is not None]
    imgs.sort(key=lambda i: i.timestamp)
    gaps: List[Gap] = []
    for prev, nxt in zip(imgs, imgs[1:]):
        delta = (nxt.timestamp - prev.timestamp).total_seconds() / 60.0
        if delta > gap_minutes:
            gaps.append(
                Gap(
                    prev_file=prev.path,
                    prev_ts=prev.timestamp,  # type: ignore[union-attr]
                    next_file=nxt.path,
                    next_ts=nxt.timestamp,  # type: ignore[union-attr]
                    gap_minutes=delta,
                )
            )
    return gaps
