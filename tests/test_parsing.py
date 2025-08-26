from __future__ import annotations

import re

from timelapse_tool.parsing import parse_timestamp
from .conftest import PATTERN, FORMAT


def test_parse_timestamp():
    pattern = re.compile(PATTERN)
    res = parse_timestamp("metroLocal_IPC_main_20230101000000.jpg", pattern, FORMAT)
    assert res.matched and res.timestamp and res.timestamp.year == 2023
    res2 = parse_timestamp("badname.jpg", pattern, FORMAT)
    assert not res2.matched
