"""Parse diff-cover/diff-quality JSON reports into structured dataclasses."""

from __future__ import annotations

import json
from dataclasses import dataclass, field


@dataclass
class FileReport:
    path: str
    percent_covered: float
    violation_lines: list[int] = field(default_factory=list)


@dataclass
class Report:
    report_name: str
    diff_name: str
    files: list[FileReport]
    total_num_lines: int
    total_num_violations: int
    total_percent_covered: float


def parse_report(json_path: str) -> Report:
    """Parse a diff-cover JSON report file into a Report dataclass.

    The JSON format (diff-cover 10.x):
    {
        "report_name": "XML",
        "diff_name": "origin/main...HEAD, staged and unstaged changes",
        "src_stats": {
            "src/foo.py": {
                "percent_covered": 85.0,
                "violation_lines": [13, 27, 42],
                "violations": [[13, null], [27, null], [42, null]]
            }
        },
        "total_num_lines": 100,
        "total_num_violations": 15,
        "total_percent_covered": 85.0,
        "num_changed_lines": 100
    }
    """
    try:
        with open(json_path) as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"::warning::JSON report not found at {json_path}. Using empty report.")
        return _empty_report()
    except json.JSONDecodeError as e:
        print(f"::warning::Failed to parse JSON report at {json_path}: {e}")
        return _empty_report()

    src_stats = data.get("src_stats", {})
    files: list[FileReport] = []

    for filepath, stats in src_stats.items():
        files.append(FileReport(
            path=filepath,
            percent_covered=stats.get("percent_covered", 0.0),
            violation_lines=stats.get("violation_lines", []),
        ))

    return Report(
        report_name=data.get("report_name", ""),
        diff_name=data.get("diff_name", ""),
        files=files,
        total_num_lines=data.get("total_num_lines", data.get("num_changed_lines", 0)),
        total_num_violations=data.get("total_num_violations", 0),
        total_percent_covered=data.get("total_percent_covered", 100.0),
    )


def _empty_report() -> Report:
    return Report(
        report_name="",
        diff_name="",
        files=[],
        total_num_lines=0,
        total_num_violations=0,
        total_percent_covered=100.0,
    )
