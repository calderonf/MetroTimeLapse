from __future__ import annotations

import re

from timelapse_tool.gaps import find_gaps
from timelapse_tool.validate import scan_folder
from .conftest import PATTERN, FORMAT


def test_find_gaps(sample_dataset):
    pattern = re.compile(PATTERN)
    results = scan_folder(sample_dataset, pattern, FORMAT, min_bytes=0)
    valid = [r for r in results if r.is_valid]
    gaps = find_gaps(valid, 10)
    assert len(gaps) == 1
    assert abs(gaps[0].gap_minutes - 15) < 0.1
