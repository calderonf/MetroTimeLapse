from __future__ import annotations

"""Filename parsing utilities."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Pattern


@dataclass
class ParseResult:
    """Result of parsing a filename for timestamp."""

    timestamp: Optional[datetime]
    matched: bool


def parse_timestamp(name: str, pattern: Pattern[str], ts_format: str) -> ParseResult:
    """Parse *name* using *pattern* extracting a datetime.

    Parameters
    ----------
    name: str
        Filename to inspect.
    pattern: Pattern[str]
        Compiled regular expression with a single capture group for the
        timestamp portion.
    ts_format: str
        ``datetime.strptime`` format string.
    """
    match = pattern.match(name)
    if not match:
        return ParseResult(timestamp=None, matched=False)
    ts_str = match.group(1)
    try:
        return ParseResult(datetime.strptime(ts_str, ts_format), matched=True)
    except ValueError:
        return ParseResult(timestamp=None, matched=True)
