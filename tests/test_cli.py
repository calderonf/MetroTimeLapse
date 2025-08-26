from __future__ import annotations

import subprocess
import sys

from pathlib import Path


def run_tool(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, "timelapse_tool.py", *args], capture_output=True, text=True)


def test_cli_build_and_gaps(sample_dataset: Path):
    out_video = sample_dataset / "out.mp4"
    res = run_tool([
        "--image-folder",
        str(sample_dataset),
        "build",
        "--min-bytes",
        "0",
        "--output-video",
        str(out_video),
        "--dry-run",
    ])
    assert res.returncode == 0
    assert "dry-run" in res.stderr

    res2 = run_tool([
        "--image-folder",
        str(sample_dataset),
        "report-gaps",
        "--min-bytes",
        "0",
        "--gap-minutes",
        "10",
    ])
    assert res2.returncode == 0
    assert "15.0" in res2.stdout
