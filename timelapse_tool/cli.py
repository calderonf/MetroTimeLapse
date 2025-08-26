from __future__ import annotations

"""Command line interface for the timelapse tool."""

from dataclasses import dataclass
from typing import List, Optional
import argparse
import logging
import re
from pathlib import Path

from .gaps import find_gaps
from .reporting import write_gap_report, write_image_report
from .sampling import sample_images
from .validate import ImageValidationResult, scan_folder
from .video import build_video

DEFAULT_PATTERN = r"metroLocal_IPC_main_(\d{14})\.jpg"
DEFAULT_TS_FORMAT = "%Y%m%d%H%M%S"


@dataclass
class Summary:
    total: int
    matched: int
    valid: int
    invalid: int
    flat: int


def _setup_logging(level: str) -> None:
    logging.basicConfig(level=getattr(logging, level.upper()), format="%(levelname)s:%(message)s")


def _scan(args: argparse.Namespace) -> List[ImageValidationResult]:
    pattern = re.compile(args.pattern)
    return scan_folder(
        folder=args.image_folder,
        pattern=pattern,
        ts_format=args.timestamp_format,
        min_bytes=args.min_bytes,
        flat_threshold=args.flat_frame_threshold,
    )


def _summary(results: List[ImageValidationResult]) -> Summary:
    matched = sum(1 for r in results if "pattern" not in r.reasons)
    valid = sum(r.is_valid for r in results)
    flat = sum(1 for r in results if r.is_flat)
    return Summary(
        total=len(results),
        matched=matched,
        valid=valid,
        invalid=len(results) - valid,
        flat=flat,
    )


def cmd_check(args: argparse.Namespace) -> int:
    results = _scan(args)
    if args.report_out:
        write_image_report(results, args.report_out)
    summary = _summary(results)
    logging.info(
        "scanned %s files: %s valid, %s invalid", summary.total, summary.valid, summary.invalid
    )
    if summary.flat:
        logging.info("%s suspected flat frames", summary.flat)
    return 0


def cmd_report_gaps(args: argparse.Namespace) -> int:
    results = _scan(args)
    valid = [r for r in results if r.is_valid]
    gaps = find_gaps(valid, args.gap_minutes)
    for g in gaps:
        print(
            f"{g.prev_file.name}, {g.prev_ts}, {g.next_file.name}, {g.next_ts}, {g.gap_minutes:.1f}"
        )
    if args.report_out:
        write_gap_report(gaps, args.report_out)
    logging.info("%s gaps found", len(gaps))
    return 0


def cmd_build(args: argparse.Namespace) -> int:
    results = _scan(args)
    valid = [r for r in results if r.is_valid]
    sampled = sample_images(valid, args.sample_minutes)
    if args.dry_run:
        logging.info("dry-run: %s frames would be written", len(sampled))
        return 0
    size = None
    if args.resize:
        w, h = map(int, args.resize.lower().split("x"))
        size = (w, h)
    report = build_video(
        sampled,
        output=args.output_video,
        fps=args.fps,
        codec=args.codec,
        size=size,
        strict=args.strict,
        dry_run=False,
    )
    logging.info(
        "wrote %s frames to %s (%s skipped)", report.frames_written, args.output_video, report.skipped
    )
    return 0


def cmd_test_dataset(args: argparse.Namespace) -> int:
    # run check
    check_code = cmd_check(args)
    # run gaps
    gaps_args = argparse.Namespace(**vars(args))
    gaps_args.gap_minutes = args.gap_minutes
    gaps_code = cmd_report_gaps(gaps_args)
    # simple failure policy: fail if any invalid or gaps
    results = _scan(args)
    summary = _summary(results)
    gaps = find_gaps([r for r in results if r.is_valid], args.gap_minutes)
    if summary.invalid or gaps:
        return 1
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Timelapse dataset tool")
    parser.add_argument("--image-folder", type=Path, required=True)
    parser.add_argument("--pattern", default=DEFAULT_PATTERN)
    parser.add_argument("--timestamp-format", default=DEFAULT_TS_FORMAT)
    parser.add_argument("--log-level", default="INFO", choices=["INFO", "DEBUG", "WARNING", "ERROR"])
    parser.add_argument("--report-out", type=Path)

    sub = parser.add_subparsers(dest="command", required=True)

    p_check = sub.add_parser("check", help="validate images")
    p_check.add_argument("--min-bytes", type=int, default=5000)
    p_check.add_argument("--flat-frame-threshold", type=float)
    p_check.set_defaults(func=cmd_check)

    p_gaps = sub.add_parser("report-gaps", help="report timestamp gaps")
    p_gaps.add_argument("--min-bytes", type=int, default=5000)
    p_gaps.add_argument("--flat-frame-threshold", type=float)
    p_gaps.add_argument("--gap-minutes", type=int, default=10)
    p_gaps.set_defaults(func=cmd_report_gaps)

    p_build = sub.add_parser("build", help="build video")
    p_build.add_argument("--min-bytes", type=int, default=5000)
    p_build.add_argument("--flat-frame-threshold", type=float)
    p_build.add_argument("--output-video", type=Path, required=True)
    p_build.add_argument("--fps", type=int, default=30)
    p_build.add_argument("--codec", type=str, default="mp4v")
    p_build.add_argument("--resize")
    p_build.add_argument("--sample-minutes", type=int)
    p_build.add_argument("--strict", action="store_true")
    p_build.add_argument("--dry-run", action="store_true")
    p_build.set_defaults(func=cmd_build)

    p_test = sub.add_parser("test-dataset", help="quick integrity test")
    p_test.add_argument("--min-bytes", type=int, default=5000)
    p_test.add_argument("--flat-frame-threshold", type=float)
    p_test.add_argument("--gap-minutes", type=int, default=10)
    p_test.set_defaults(func=cmd_test_dataset)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    _setup_logging(args.log_level)
    return args.func(args)
