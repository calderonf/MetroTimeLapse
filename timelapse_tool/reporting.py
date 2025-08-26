from __future__ import annotations

"""Reporting helpers."""

import csv
import json
from pathlib import Path
from typing import Iterable

from .gaps import Gap
from .validate import ImageValidationResult


def write_image_report(results: Iterable[ImageValidationResult], path: Path) -> None:
    """Write per-image validation info to ``path`` (CSV or JSON)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix.lower() == ".json":
        data = [
            {
                "filename": r.path.name,
                "timestamp": r.timestamp.isoformat() if r.timestamp else None,
                "size_bytes": r.size_bytes,
                "readable": r.readable,
                "width": r.width,
                "height": r.height,
                "reasons": r.reasons,
                "is_flat": r.is_flat,
            }
            for r in results
        ]
        path.write_text(json.dumps(data, indent=2))
    else:
        with path.open("w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "filename",
                "timestamp",
                "size_bytes",
                "readable",
                "width",
                "height",
                "reasons",
                "is_flat",
            ])
            for r in results:
                writer.writerow([
                    r.path.name,
                    r.timestamp.isoformat() if r.timestamp else "",
                    r.size_bytes,
                    r.readable,
                    r.width or "",
                    r.height or "",
                    ";".join(r.reasons),
                    r.is_flat,
                ])


def write_gap_report(gaps: Iterable[Gap], path: Path) -> None:
    """Write gap information to ``path`` (CSV or JSON)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix.lower() == ".json":
        data = [
            {
                "prev_file": g.prev_file.name,
                "prev_ts": g.prev_ts.isoformat(),
                "next_file": g.next_file.name,
                "next_ts": g.next_ts.isoformat(),
                "gap_minutes": g.gap_minutes,
            }
            for g in gaps
        ]
        path.write_text(json.dumps(data, indent=2))
    else:
        with path.open("w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "prev_file",
                "prev_ts",
                "next_file",
                "next_ts",
                "gap_minutes",
            ])
            for g in gaps:
                writer.writerow([
                    g.prev_file.name,
                    g.prev_ts.isoformat(),
                    g.next_file.name,
                    g.next_ts.isoformat(),
                    g.gap_minutes,
                ])
