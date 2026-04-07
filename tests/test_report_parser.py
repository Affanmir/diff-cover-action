"""Tests for src/report_parser.py."""

from __future__ import annotations

from pathlib import Path

from src.report_parser import parse_report


class TestParseReport:
    def test_parse_coverage_report(self, sample_coverage_json: Path) -> None:
        report = parse_report(str(sample_coverage_json))
        assert report.report_name == "XML"
        assert report.total_percent_covered == 82.0
        assert report.total_num_lines == 50
        assert report.total_num_violations == 9
        assert len(report.files) == 3

    def test_file_details(self, sample_coverage_json: Path) -> None:
        report = parse_report(str(sample_coverage_json))
        foo = next(f for f in report.files if f.path == "src/foo.py")
        assert foo.percent_covered == 85.0
        assert foo.violation_lines == [13, 27, 42]

    def test_file_with_no_violations(self, sample_coverage_json: Path) -> None:
        report = parse_report(str(sample_coverage_json))
        baz = next(f for f in report.files if f.path == "src/baz.py")
        assert baz.percent_covered == 100.0
        assert baz.violation_lines == []

    def test_parse_quality_report(self, sample_quality_json: Path) -> None:
        report = parse_report(str(sample_quality_json))
        assert report.report_name == "pylint"
        assert report.total_percent_covered == 80.0
        assert report.total_num_violations == 4
        assert len(report.files) == 1

    def test_parse_empty_diff(self, empty_diff_json: Path) -> None:
        report = parse_report(str(empty_diff_json))
        assert report.total_percent_covered == 100.0
        assert report.total_num_lines == 0
        assert report.total_num_violations == 0
        assert len(report.files) == 0

    def test_missing_file_returns_empty_report(self) -> None:
        report = parse_report("/nonexistent/path.json")
        assert report.total_percent_covered == 100.0
        assert report.total_num_lines == 0
        assert len(report.files) == 0

    def test_invalid_json_returns_empty_report(self, tmp_path: Path) -> None:
        bad_json = tmp_path / "bad.json"
        bad_json.write_text("not json at all")
        report = parse_report(str(bad_json))
        assert report.total_percent_covered == 100.0
        assert len(report.files) == 0
