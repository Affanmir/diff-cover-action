"""Tests for src/runner.py."""

from __future__ import annotations

import sys

from src.runner import run_diff_cover


class TestRunDiffCover:
    def test_successful_command(self) -> None:
        result = run_diff_cover([sys.executable, "-c", "print('hello')"])
        assert result.exit_code == 0
        assert "hello" in result.stdout

    def test_failing_command(self) -> None:
        result = run_diff_cover([sys.executable, "-c", "import sys; sys.exit(2)"])
        assert result.exit_code == 2

    def test_stderr_capture(self) -> None:
        result = run_diff_cover(
            [sys.executable, "-c", "import sys; print('err msg', file=sys.stderr); sys.exit(0)"]
        )
        assert result.exit_code == 0
        assert "err msg" in result.stderr

    def test_multiline_stdout(self) -> None:
        result = run_diff_cover(
            [sys.executable, "-c", "print('line1'); print('line2'); print('line3')"]
        )
        assert "line1" in result.stdout
        assert "line2" in result.stdout
        assert "line3" in result.stdout
