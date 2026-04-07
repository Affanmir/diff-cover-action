"""Tests for src/cli_builder.py — the most critical mapping layer."""

from __future__ import annotations

import pytest

from src.cli_builder import build_command, JSON_REPORT_PATH, MD_REPORT_PATH, HTML_REPORT_PATH


def _default_kwargs(**overrides: object) -> dict[str, object]:
    """Return default build_command kwargs with overrides."""
    defaults: dict[str, object] = {
        "mode": "coverage",
        "coverage_files": "coverage.xml",
        "violations": "",
        "quality_input_reports": "",
        "quality_options": "",
        "compare_branch": "origin/main",
        "diff_range_notation": "...",
        "diff_file": "",
        "ignore_staged": False,
        "ignore_unstaged": False,
        "include_untracked": False,
        "ignore_whitespace": False,
        "exclude": "",
        "include": "",
        "src_roots": "",
        "expand_coverage_report": False,
        "show_uncovered": False,
        "quiet": False,
        "config_file": "",
        "fail_under": 0.0,
    }
    defaults.update(overrides)
    return defaults


class TestCoverageMode:
    def test_basic_coverage(self) -> None:
        cmd = build_command(**_default_kwargs())
        assert cmd[0] == "diff-cover"
        assert "coverage.xml" in cmd
        assert "--json-report" in cmd
        assert JSON_REPORT_PATH in cmd
        assert "--markdown-report" in cmd
        assert MD_REPORT_PATH in cmd

    def test_multiple_coverage_files(self, tmp_path: object) -> None:
        cmd = build_command(**_default_kwargs(coverage_files="cov1.xml cov2.xml"))
        assert "cov1.xml" in cmd
        assert "cov2.xml" in cmd

    def test_compare_branch(self) -> None:
        cmd = build_command(**_default_kwargs(compare_branch="origin/develop"))
        idx = cmd.index("--compare-branch")
        assert cmd[idx + 1] == "origin/develop"

    def test_diff_range_notation_default_not_added(self) -> None:
        cmd = build_command(**_default_kwargs())
        assert "--diff-range-notation" not in cmd

    def test_diff_range_notation_custom(self) -> None:
        cmd = build_command(**_default_kwargs(diff_range_notation=".."))
        idx = cmd.index("--diff-range-notation")
        assert cmd[idx + 1] == ".."

    def test_diff_file(self) -> None:
        cmd = build_command(**_default_kwargs(diff_file="/tmp/my.diff"))
        idx = cmd.index("--diff-file")
        assert cmd[idx + 1] == "/tmp/my.diff"

    def test_boolean_flags(self) -> None:
        cmd = build_command(**_default_kwargs(
            ignore_staged=True,
            ignore_unstaged=True,
            include_untracked=True,
            ignore_whitespace=True,
            expand_coverage_report=True,
            show_uncovered=True,
            quiet=True,
        ))
        assert "--ignore-staged" in cmd
        assert "--ignore-unstaged" in cmd
        assert "--include-untracked" in cmd
        assert "--ignore-whitespace" in cmd
        assert "--expand-coverage-report" in cmd
        assert "--show-uncovered" in cmd
        assert "--quiet" in cmd

    def test_boolean_flags_false(self) -> None:
        cmd = build_command(**_default_kwargs())
        assert "--ignore-staged" not in cmd
        assert "--ignore-unstaged" not in cmd
        assert "--include-untracked" not in cmd
        assert "--ignore-whitespace" not in cmd
        assert "--expand-coverage-report" not in cmd
        assert "--show-uncovered" not in cmd
        assert "--quiet" not in cmd

    def test_exclude_patterns(self) -> None:
        cmd = build_command(**_default_kwargs(exclude="tests/*\nsetup.py"))
        # Should have two --exclude flags
        indices = [i for i, x in enumerate(cmd) if x == "--exclude"]
        assert len(indices) == 2
        assert cmd[indices[0] + 1] == "tests/*"
        assert cmd[indices[1] + 1] == "setup.py"

    def test_include_patterns(self) -> None:
        cmd = build_command(**_default_kwargs(include="src/**/*.py\nlib/**/*.py"))
        indices = [i for i, x in enumerate(cmd) if x == "--include"]
        assert len(indices) == 2

    def test_src_roots(self) -> None:
        cmd = build_command(**_default_kwargs(src_roots="src main/java"))
        idx = cmd.index("--src-roots")
        assert cmd[idx + 1] == "src"
        assert cmd[idx + 2] == "main/java"

    def test_fail_under(self) -> None:
        cmd = build_command(**_default_kwargs(fail_under=80.0))
        idx = cmd.index("--fail-under")
        assert cmd[idx + 1] == "80.0"

    def test_fail_under_zero_not_added(self) -> None:
        cmd = build_command(**_default_kwargs(fail_under=0.0))
        assert "--fail-under" not in cmd

    def test_config_file_placed_before_other_flags(self) -> None:
        cmd = build_command(**_default_kwargs(config_file="pyproject.toml"))
        config_idx = cmd.index("--config-file")
        json_idx = cmd.index("--json-report")
        assert config_idx < json_idx

    def test_no_coverage_files_raises(self) -> None:
        with pytest.raises(ValueError, match="No coverage files"):
            build_command(**_default_kwargs(coverage_files=""))

    def test_html_report_always_generated(self) -> None:
        cmd = build_command(**_default_kwargs())
        assert "--html-report" in cmd
        assert HTML_REPORT_PATH in cmd


class TestQualityMode:
    def test_basic_quality(self) -> None:
        cmd = build_command(**_default_kwargs(mode="quality", violations="flake8"))
        assert cmd[0] == "diff-quality"
        assert "--violations=flake8" in cmd

    def test_quality_with_input_reports(self) -> None:
        cmd = build_command(**_default_kwargs(
            mode="quality",
            violations="pylint",
            quality_input_reports="report1.txt report2.txt",
        ))
        assert "report1.txt" in cmd
        assert "report2.txt" in cmd

    def test_quality_options_passthrough(self) -> None:
        cmd = build_command(**_default_kwargs(
            mode="quality",
            violations="ruff.check",
            quality_options="--select E501",
        ))
        idx = cmd.index("--options")
        assert cmd[idx + 1] == "--select E501"

    def test_no_violations_raises(self) -> None:
        with pytest.raises(ValueError, match="No violations tool"):
            build_command(**_default_kwargs(mode="quality", violations=""))

    def test_quality_shared_flags(self) -> None:
        cmd = build_command(**_default_kwargs(
            mode="quality",
            violations="eslint",
            compare_branch="origin/develop",
            ignore_staged=True,
            fail_under=90.0,
        ))
        assert "--compare-branch" in cmd
        assert "--ignore-staged" in cmd
        assert "--fail-under" in cmd


class TestInvalidMode:
    def test_invalid_mode(self) -> None:
        with pytest.raises(ValueError, match="Invalid mode"):
            build_command(**_default_kwargs(mode="invalid"))
