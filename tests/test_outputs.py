"""Tests for src/outputs.py."""

from __future__ import annotations

import os
from pathlib import Path

from src.outputs import write_outputs, write_step_summary
from src.report_parser import Report


class TestWriteOutputs:
    def test_writes_all_outputs(self, tmp_path: Path, sample_report: Report) -> None:
        output_file = tmp_path / "github_output"
        output_file.write_text("")
        os.environ["GITHUB_OUTPUT"] = str(output_file)

        try:
            write_outputs(
                report=sample_report,
                threshold_met=True,
                comment_id="12345",
                json_report_path="/tmp/dc-report.json",
                badge_path="/tmp/badge.json",
                exit_code=0,
            )

            content = output_file.read_text()
            assert "total-percent=82" in content
            assert "total-percent-float=82.00" in content
            assert "total-lines=50" in content
            assert "total-violations=9" in content
            assert "files-changed=3" in content
            assert "threshold-met=true" in content
            assert "comment-id=12345" in content
            assert "report-json=/tmp/dc-report.json" in content
            assert "badge-json=/tmp/badge.json" in content
            assert "exit-code=0" in content
        finally:
            os.environ.pop("GITHUB_OUTPUT", None)

    def test_threshold_not_met(self, tmp_path: Path, sample_report: Report) -> None:
        output_file = tmp_path / "github_output"
        output_file.write_text("")
        os.environ["GITHUB_OUTPUT"] = str(output_file)

        try:
            write_outputs(
                report=sample_report,
                threshold_met=False,
                comment_id="",
                json_report_path="/tmp/dc-report.json",
                badge_path="",
                exit_code=1,
            )

            content = output_file.read_text()
            assert "threshold-met=false" in content
            assert "exit-code=1" in content
        finally:
            os.environ.pop("GITHUB_OUTPUT", None)


class TestWriteStepSummary:
    def test_writes_summary(self, tmp_path: Path, sample_report: Report) -> None:
        summary_file = tmp_path / "github_step_summary"
        summary_file.write_text("")
        os.environ["GITHUB_STEP_SUMMARY"] = str(summary_file)

        try:
            write_step_summary(
                report=sample_report,
                mode="coverage",
                fail_under=80.0,
                threshold_met=True,
            )

            content = summary_file.read_text()
            assert "82.0%" in content
            assert "Coverage" in content
            assert "src/foo.py" in content
        finally:
            os.environ.pop("GITHUB_STEP_SUMMARY", None)
