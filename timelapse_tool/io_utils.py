from __future__ import annotations

"""Helpers for filesystem interactions."""

from pathlib import Path
from typing import Iterable


def iter_files(folder: Path) -> Iterable[Path]:
    """Yield files in *folder* sorted by name."""
    return sorted([p for p in folder.iterdir() if p.is_file()])
