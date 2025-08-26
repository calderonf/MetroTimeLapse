from __future__ import annotations

from pathlib import Path

import numpy as np
import cv2

from timelapse_tool.validate import validate_image
from .conftest import PATTERN, FORMAT
import re


def test_size_threshold(tmp_path: Path):
    # create small image
    arr = np.full((10, 10, 3), 255, dtype=np.uint8)
    path = tmp_path / "metroLocal_IPC_main_20230101000000.jpg"
    cv2.imwrite(str(path), arr)
    pattern = re.compile(PATTERN)
    res = validate_image(path, pattern, FORMAT, min_bytes=50000)
    assert "size" in res.reasons


def test_unreadable(tmp_path: Path):
    path = tmp_path / "metroLocal_IPC_main_20230101000000.jpg"
    # write random bytes > min_bytes
    path.write_bytes(b"0" * 6000)
    pattern = re.compile(PATTERN)
    res = validate_image(path, pattern, FORMAT, min_bytes=5000)
    assert "unreadable" in res.reasons


def test_flat_detection(tmp_path: Path):
    arr = np.zeros((10, 10, 3), dtype=np.uint8)
    path = tmp_path / "metroLocal_IPC_main_20230101000000.jpg"
    cv2.imwrite(str(path), arr)
    pattern = re.compile(PATTERN)
    res = validate_image(path, pattern, FORMAT, min_bytes=0, flat_threshold=1.0)
    assert res.is_flat
