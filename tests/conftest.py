from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import cv2
import numpy as np
import pytest


PATTERN = r"metroLocal_IPC_main_(\d{14})\.jpg"
FORMAT = "%Y%m%d%H%M%S"


@pytest.fixture()
def sample_dataset(tmp_path: Path) -> Path:
    """Create a temporary dataset with valid and corrupted images."""
    times = [
        datetime(2023, 1, 1, 0, 0, 0),
        datetime(2023, 1, 1, 0, 5, 0),
        datetime(2023, 1, 1, 0, 20, 0),  # gap of 15 minutes
    ]
    for t in times:
        arr = np.full((100, 100, 3), 255, dtype=np.uint8)
        fname = f"metroLocal_IPC_main_{t.strftime(FORMAT)}.jpg"
        cv2.imwrite(str(tmp_path / fname), arr)
    # corrupted small file
    (tmp_path / "metroLocal_IPC_main_20230101002500.jpg").write_bytes(b"bad")
    # wrong pattern
    (tmp_path / "random.txt").write_text("oops")
    return tmp_path
