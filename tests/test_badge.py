"""Tests for src/badge.py."""

from __future__ import annotations

import json
from pathlib import Path

from src.badge import _color_for_percent, generate_badge


class TestColorForPercent:
    def test_brightgreen(self) -> None:
        assert _color_for_percent(95.0) == "brightgreen"
        assert _color_for_percent(90.0) == "brightgreen"

    def test_green(self) -> None:
        assert _color_for_percent(85.0) == "green"
        assert _color_for_percent(80.0) == "green"

    def test_yellowgreen(self) -> None:
        assert _color_for_percent(75.0) == "yellowgreen"
        assert _color_for_percent(70.0) == "yellowgreen"

    def test_yellow(self) -> None:
        assert _color_for_percent(65.0) == "yellow"
        assert _color_for_percent(60.0) == "yellow"

    def test_orange(self) -> None:
        assert _color_for_percent(50.0) == "orange"
        assert _color_for_percent(40.0) == "orange"

    def test_red(self) -> None:
        assert _color_for_percent(30.0) == "red"
        assert _color_for_percent(0.0) == "red"


class TestGenerateBadge:
    def test_coverage_badge(self, tmp_path: Path) -> None:
        outfile = str(tmp_path / "badge.json")
        result = generate_badge(percent=85.0, mode="coverage", filename=outfile)
        assert result == outfile

        with open(outfile) as f:
            data = json.load(f)

        assert data["schemaVersion"] == 1
        assert data["label"] == "diff coverage"
        assert data["message"] == "85.0%"
        assert data["color"] == "green"

    def test_quality_badge(self, tmp_path: Path) -> None:
        outfile = str(tmp_path / "badge.json")
        generate_badge(percent=95.0, mode="quality", filename=outfile)

        with open(outfile) as f:
            data = json.load(f)

        assert data["label"] == "diff quality"
        assert data["message"] == "95.0%"
        assert data["color"] == "brightgreen"

    def test_low_coverage_badge(self, tmp_path: Path) -> None:
        outfile = str(tmp_path / "badge.json")
        generate_badge(percent=25.0, mode="coverage", filename=outfile)

        with open(outfile) as f:
            data = json.load(f)

        assert data["color"] == "red"
