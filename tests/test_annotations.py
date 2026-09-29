"""Tests for src/annotations.py."""

from __future__ import annotations

from src.annotations import _group_consecutive_lines, create_annotations
from src.report_parser import FileReport, Report


class TestGroupConsecutiveLines:
    def test_empty(self) -> None:
        assert _group_consecutive_lines([]) == []

    def test_single_line(self) -> None:
        assert _group_consecutive_lines([5]) == [(5, 5)]

    def test_consecutive(self) -> None:
        assert _group_consecutive_lines([1, 2, 3]) == [(1, 3)]

    def test_gaps(self) -> None:
        assert _group_consecutive_lines([1, 2, 3, 7, 8, 12]) == [(1, 3), (7, 8), (12, 12)]

    def test_duplicates(self) -> None:
        assert _group_consecutive_lines([5, 5, 6, 6]) == [(5, 6)]

    def test_unsorted(self) -> None:
        assert _group_consecutive_lines([8, 3, 1, 2]) == [(1, 3), (8, 8)]


class TestCreateAnnotations:
    def test_creates_annotations(self, sample_report: Report, capsys: object) -> None:
        create_annotations(report=sample_report, mode="coverage")
        captured = capsys.readouterr()  # type: ignore[attr-defined]
        assert "::warning" in captured.out
        assert "src/bar.py" in captured.out

    def test_respects_limit(self, capsys: object) -> None:
        # Use non-consecutive lines so each gets its own annotation
        violation_lines = [1, 10, 20, 30, 40, 50, 60, 70, 80, 90]
        report = Report(
            report_name="XML",
            diff_name="",
            files=[
                FileReport(
                    path="big.py",
                    percent_covered=0.0,
                    violation_lines=violation_lines,
                )
            ],
            total_num_lines=100,
            total_num_violations=len(violation_lines),
            total_percent_covered=1.0,
        )
        create_annotations(report=report, mode="coverage", limit=3)
        captured = capsys.readouterr()  # type: ignore[attr-defined]
        # Should have exactly 3 annotation lines plus the summary line
        annotation_lines = [
            line for line in captured.out.splitlines() if line.startswith("::warning")
        ]
        assert len(annotation_lines) == 3

    def test_empty_report_no_annotations(self, empty_report: Report, capsys: object) -> None:
        create_annotations(report=empty_report, mode="coverage")
        captured = capsys.readouterr()  # type: ignore[attr-defined]
        assert "No annotations needed" in captured.out

    def test_quality_mode_label(self, sample_report: Report, capsys: object) -> None:
        create_annotations(report=sample_report, mode="quality")
        captured = capsys.readouterr()  # type: ignore[attr-defined]
        assert "quality violations" in captured.out

    def test_annotation_type_error(self, sample_report: Report, capsys: object) -> None:
        create_annotations(report=sample_report, mode="coverage", annotation_type="error")
        captured = capsys.readouterr()  # type: ignore[attr-defined]
        assert "::error" in captured.out

    def test_annotation_type_notice(self, sample_report: Report, capsys: object) -> None:
        create_annotations(report=sample_report, mode="coverage", annotation_type="notice")
        captured = capsys.readouterr()  # type: ignore[attr-defined]
        assert "::notice" in captured.out

    def test_prioritizes_worst_files(self, capsys: object) -> None:
        report = Report(
            report_name="XML",
            diff_name="",
            files=[
                FileReport(path="good.py", percent_covered=90.0, violation_lines=[5]),
                FileReport(path="bad.py", percent_covered=10.0, violation_lines=[1, 2, 3]),
            ],
            total_num_lines=20,
            total_num_violations=4,
            total_percent_covered=50.0,
        )
        create_annotations(report=report, mode="coverage", limit=2)
        captured = capsys.readouterr()  # type: ignore[attr-defined]
        lines = [line for line in captured.out.splitlines() if line.startswith("::warning")]
        # bad.py should come first (lower coverage)
        assert "bad.py" in lines[0]

    def test_message_body_includes_filename(self, capsys: object) -> None:
        # The log view of a workflow command shows only the message body, not the
        # file= property, so the path has to be in the message itself.
        report = Report(
            report_name="XML",
            diff_name="",
            files=[
                FileReport(path="src/Foo.cs", percent_covered=50.0, violation_lines=[14, 21, 22]),
            ],
            total_num_lines=10,
            total_num_violations=3,
            total_percent_covered=50.0,
        )
        create_annotations(report=report, mode="coverage")
        captured = capsys.readouterr()  # type: ignore[attr-defined]
        bodies = [
            line.split("::", 2)[2]
            for line in captured.out.splitlines()
            if line.startswith("::warning")
        ]
        assert bodies == [
            "src/Foo.cs line 14 is not covered by tests",
            "src/Foo.cs lines 21-22 are not covered by tests",
        ]

    def test_quality_message_body_is_grammatical(self, capsys: object) -> None:
        report = Report(
            report_name="ruff.check",
            diff_name="",
            files=[
                FileReport(path="src/foo.py", percent_covered=50.0, violation_lines=[3, 7, 8]),
            ],
            total_num_lines=10,
            total_num_violations=3,
            total_percent_covered=50.0,
        )
        create_annotations(report=report, mode="quality")
        captured = capsys.readouterr()  # type: ignore[attr-defined]
        bodies = [
            line.split("::", 2)[2]
            for line in captured.out.splitlines()
            if line.startswith("::warning")
        ]
        assert bodies == [
            "src/foo.py line 3 has quality violations",
            "src/foo.py lines 7-8 have quality violations",
        ]

    def test_groups_consecutive_lines(self, capsys: object) -> None:
        report = Report(
            report_name="XML",
            diff_name="",
            files=[
                FileReport(path="file.py", percent_covered=50.0, violation_lines=[1, 2, 3, 10]),
            ],
            total_num_lines=10,
            total_num_violations=4,
            total_percent_covered=60.0,
        )
        create_annotations(report=report, mode="coverage")
        captured = capsys.readouterr()  # type: ignore[attr-defined]
        # Lines 1-3 grouped, line 10 separate = 2 annotations
        annotation_lines = [
            line for line in captured.out.splitlines() if line.startswith("::warning")
        ]
        assert len(annotation_lines) == 2
        assert "line=1,endLine=3" in annotation_lines[0]
        assert "line=10" in annotation_lines[1]
