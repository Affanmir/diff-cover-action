"""Shared test fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.report_parser import FileReport, Report

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_coverage_json() -> Path:
    return FIXTURES_DIR / "sample_coverage.json"


@pytest.fixture
def sample_quality_json() -> Path:
    return FIXTURES_DIR / "sample_quality.json"


@pytest.fixture
def empty_diff_json() -> Path:
    return FIXTURES_DIR / "empty_diff.json"


@pytest.fixture
def sample_report() -> Report:
    return Report(
        report_name="XML",
        diff_name="origin/main...HEAD",
        files=[
            FileReport(path="src/foo.py", percent_covered=85.0, violation_lines=[13, 27, 42]),
            FileReport(path="src/bar.py", percent_covered=60.0, violation_lines=[5, 6, 7, 8, 15, 22]),
            FileReport(path="src/baz.py", percent_covered=100.0, violation_lines=[]),
        ],
        total_num_lines=50,
        total_num_violations=9,
        total_percent_covered=82.0,
    )


@pytest.fixture
def empty_report() -> Report:
    return Report(
        report_name="XML",
        diff_name="origin/main...HEAD",
        files=[],
        total_num_lines=0,
        total_num_violations=0,
        total_percent_covered=100.0,
    )
