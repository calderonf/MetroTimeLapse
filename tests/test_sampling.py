from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

from timelapse_tool.sampling import sample_images
from timelapse_tool.validate import ImageValidationResult


def _make_img(ts: datetime) -> ImageValidationResult:
    return ImageValidationResult(
        path=Path("f.jpg"),
        timestamp=ts,
        size_bytes=1000,
        readable=True,
        width=10,
        height=10,
        reasons=[],
    )


def test_sample_images():
    start = datetime(2023, 1, 1, 0, 0, 0)
    imgs = [_make_img(start + timedelta(minutes=i)) for i in range(5)]
    sampled = sample_images(imgs, 2)
    assert len(sampled) == 3
