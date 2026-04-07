"""Build diff-cover or diff-quality CLI commands from action inputs."""

from __future__ import annotations

import glob as globmod

JSON_REPORT_PATH = "/tmp/dc-report.json"
MD_REPORT_PATH = "/tmp/dc-report.md"
HTML_REPORT_PATH = "/tmp/dc-report.html"


def _expand_globs(pattern_string: str) -> list[str]:
    """Expand space-separated glob patterns into a list of matched file paths."""
    paths: list[str] = []
    for pattern in pattern_string.split():
        pattern = pattern.strip()
        if not pattern:
            continue
        matched = globmod.glob(pattern, recursive=True)
        if matched:
            paths.extend(sorted(matched))
        else:
            # Keep the original pattern — diff-cover will report the error
            paths.append(pattern)
    return paths


def _split_multiline(text: str) -> list[str]:
    """Split a newline-separated string into a list of non-empty stripped values."""
    return [line.strip() for line in text.splitlines() if line.strip()]


def build_command(
    *,
    mode: str,
    coverage_files: str,
    violations: str,
    quality_input_reports: str,
    quality_options: str,
    compare_branch: str,
    diff_range_notation: str,
    diff_file: str,
    ignore_staged: bool,
    ignore_unstaged: bool,
    include_untracked: bool,
    ignore_whitespace: bool,
    exclude: str,
    include: str,
    src_roots: str,
    expand_coverage_report: bool,
    show_uncovered: bool,
    quiet: bool,
    config_file: str,
    fail_under: float,
) -> list[str]:
    """Build the complete diff-cover or diff-quality CLI command.

    Returns a list of command-line arguments ready for subprocess.
    """
    if mode == "coverage":
        return _build_coverage_command(
            coverage_files=coverage_files,
            compare_branch=compare_branch,
            diff_range_notation=diff_range_notation,
            diff_file=diff_file,
            ignore_staged=ignore_staged,
            ignore_unstaged=ignore_unstaged,
            include_untracked=include_untracked,
            ignore_whitespace=ignore_whitespace,
            exclude=exclude,
            include=include,
            src_roots=src_roots,
            expand_coverage_report=expand_coverage_report,
            show_uncovered=show_uncovered,
            quiet=quiet,
            config_file=config_file,
            fail_under=fail_under,
        )
    elif mode == "quality":
        return _build_quality_command(
            violations=violations,
            quality_input_reports=quality_input_reports,
            quality_options=quality_options,
            compare_branch=compare_branch,
            diff_range_notation=diff_range_notation,
            diff_file=diff_file,
            ignore_staged=ignore_staged,
            ignore_unstaged=ignore_unstaged,
            include_untracked=include_untracked,
            ignore_whitespace=ignore_whitespace,
            exclude=exclude,
            include=include,
            quiet=quiet,
            config_file=config_file,
            fail_under=fail_under,
        )
    else:
        raise ValueError(f"Invalid mode: {mode!r}. Must be 'coverage' or 'quality'.")


def _add_shared_flags(
    cmd: list[str],
    *,
    compare_branch: str,
    diff_range_notation: str,
    diff_file: str,
    ignore_staged: bool,
    ignore_unstaged: bool,
    include_untracked: bool,
    ignore_whitespace: bool,
    exclude: str,
    include: str,
    quiet: bool,
    config_file: str,
    fail_under: float,
) -> None:
    """Append flags shared between diff-cover and diff-quality to the command list."""
    # Config file goes first so explicit flags override it
    if config_file:
        cmd.extend(["--config-file", config_file])

    # Always generate JSON and markdown reports
    cmd.extend(["--json-report", JSON_REPORT_PATH])
    cmd.extend(["--markdown-report", MD_REPORT_PATH])
    cmd.extend(["--html-report", HTML_REPORT_PATH])

    if compare_branch:
        cmd.extend(["--compare-branch", compare_branch])

    if diff_range_notation and diff_range_notation != "...":
        cmd.extend(["--diff-range-notation", diff_range_notation])

    if diff_file:
        cmd.extend(["--diff-file", diff_file])

    if ignore_staged:
        cmd.append("--ignore-staged")

    if ignore_unstaged:
        cmd.append("--ignore-unstaged")

    if include_untracked:
        cmd.append("--include-untracked")

    if ignore_whitespace:
        cmd.append("--ignore-whitespace")

    for pattern in _split_multiline(exclude):
        cmd.extend(["--exclude", pattern])

    for pattern in _split_multiline(include):
        cmd.extend(["--include", pattern])

    if quiet:
        cmd.append("--quiet")

    if fail_under > 0:
        cmd.extend(["--fail-under", str(fail_under)])


def _build_coverage_command(
    *,
    coverage_files: str,
    compare_branch: str,
    diff_range_notation: str,
    diff_file: str,
    ignore_staged: bool,
    ignore_unstaged: bool,
    include_untracked: bool,
    ignore_whitespace: bool,
    exclude: str,
    include: str,
    src_roots: str,
    expand_coverage_report: bool,
    show_uncovered: bool,
    quiet: bool,
    config_file: str,
    fail_under: float,
) -> list[str]:
    """Build a diff-cover command."""
    cmd = ["diff-cover"]

    # Positional coverage files
    files = _expand_globs(coverage_files)
    if not files:
        raise ValueError(
            "No coverage files specified. Set the 'coverage-files' input "
            "(e.g., 'coverage.xml' or '**/coverage*.xml')."
        )
    cmd.extend(files)

    _add_shared_flags(
        cmd,
        compare_branch=compare_branch,
        diff_range_notation=diff_range_notation,
        diff_file=diff_file,
        ignore_staged=ignore_staged,
        ignore_unstaged=ignore_unstaged,
        include_untracked=include_untracked,
        ignore_whitespace=ignore_whitespace,
        exclude=exclude,
        include=include,
        quiet=quiet,
        config_file=config_file,
        fail_under=fail_under,
    )

    if src_roots:
        cmd.extend(["--src-roots", *src_roots.split()])

    if expand_coverage_report:
        cmd.append("--expand-coverage-report")

    if show_uncovered:
        cmd.append("--show-uncovered")

    return cmd


def _build_quality_command(
    *,
    violations: str,
    quality_input_reports: str,
    quality_options: str,
    compare_branch: str,
    diff_range_notation: str,
    diff_file: str,
    ignore_staged: bool,
    ignore_unstaged: bool,
    include_untracked: bool,
    ignore_whitespace: bool,
    exclude: str,
    include: str,
    quiet: bool,
    config_file: str,
    fail_under: float,
) -> list[str]:
    """Build a diff-quality command."""
    if not violations:
        raise ValueError(
            "No violations tool specified. Set the 'violations' input "
            "(e.g., 'flake8', 'pylint', 'ruff.check', 'eslint')."
        )

    cmd = ["diff-quality", f"--violations={violations}"]

    # Optional pre-generated report files
    if quality_input_reports:
        for report_file in quality_input_reports.split():
            if report_file.strip():
                cmd.append(report_file.strip())

    _add_shared_flags(
        cmd,
        compare_branch=compare_branch,
        diff_range_notation=diff_range_notation,
        diff_file=diff_file,
        ignore_staged=ignore_staged,
        ignore_unstaged=ignore_unstaged,
        include_untracked=include_untracked,
        ignore_whitespace=ignore_whitespace,
        exclude=exclude,
        include=include,
        quiet=quiet,
        config_file=config_file,
        fail_under=fail_under,
    )

    if quality_options:
        cmd.extend(["--options", quality_options])

    return cmd
