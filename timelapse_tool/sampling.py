from __future__ import annotations

"""Frame sampling logic."""

from datetime import datetime
from typing import Iterable, List, Optional

from .validate import ImageValidationResult


def sample_images(
    images: Iterable[ImageValidationResult], sample_minutes: Optional[int]
) -> List[ImageValidationResult]:
    """Return a subset of *images* spaced by at least ``sample_minutes``.

    If ``sample_minutes`` is ``None`` or ``0`` the original list is returned.
    Images must be sorted by timestamp.
    """
    images = list(images)
    if not sample_minutes:
        return images
    sampled: List[ImageValidationResult] = []
    last_ts: Optional[datetime] = None
    for img in images:
        if img.timestamp is None:
            continue
        if last_ts is None:
            sampled.append(img)
            last_ts = img.timestamp
            continue
        delta = (img.timestamp - last_ts).total_seconds() / 60.0
        if delta >= sample_minutes:
            sampled.append(img)
            last_ts = img.timestamp
    return sampled
