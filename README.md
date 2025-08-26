# Metro Time-lapse Tool

A small utility to validate camera image datasets, report timestamp gaps and
build time‑lapse videos.  It consolidates the previous scripts into a single
CLI entry point.

## Features

* Validate image naming, size and readability (`check`).
* Detect gaps between consecutive images (`report-gaps`).
* Build a time‑lapse video with optional sampling (`build`).
* Combined dataset test (`test-dataset`).

## Installation

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

## Examples

```bash
python timelapse_tool.py check --image-folder D:/metro --min-bytes 5000 --report-out report.csv
python timelapse_tool.py report-gaps --image-folder D:/metro --gap-minutes 10 --report-out gaps.json
python timelapse_tool.py build --image-folder D:/metro --output-video timelapse.mp4 --fps 30
python timelapse_tool.py build --image-folder D:/metro --output-video timelapse.mp4 --fps 30 --sample-minutes 5
python timelapse_tool.py build --image-folder D:/metro --output-video timelapse_720p.mp4 --resize 1280x720 --codec mp4v
python timelapse_tool.py test-dataset --image-folder D:/metro --gap-minutes 10 --min-bytes 5000
```

## Testing

Run the automated tests with:

```bash
pytest -q
```
