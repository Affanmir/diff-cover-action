#!/usr/bin/env python3
"""Main entrypoint for the diff-cover GitHub Action."""

from __future__ import annotations

import os
import sys
import traceback

from src.annotations import create_annotations
from src.badge import generate_badge
from src.cli_builder import build_command
from src.comment import post_or_update_comment
from src.git_setup import ensure_git_history
from src.outputs import write_outputs, write_step_summary
from src.report_parser import parse_report
from src.runner import run_diff_cover


def get_input(name: str, default: str = "") -> str:
    # GitHub Actions sets INPUT_COVERAGE-FILES (with hyphens), not INPUT_COVERAGE_FILES.
    # Check the hyphenated form first (actual GitHub behavior), then underscore fallback.
    env_hyphen = f"INPUT_{name.upper()}"
    env_under = f"INPUT_{name.upper().replace('-', '_')}"
    return os.environ.get(env_hyphen, os.environ.get(env_under, default))


def get_bool_input(name: str, default: bool = False) -> bool:
    value = get_input(name, str(default).lower())
    return value.lower() in ("true", "1", "yes")


def get_github_context() -> dict[str, str]:
    event_name = os.environ.get("GITHUB_EVENT_NAME", "")
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    sha = os.environ.get("GITHUB_SHA", "")
    event_path = os.environ.get("GITHUB_EVENT_PATH", "")
    server_url = os.environ.get("GITHUB_SERVER_URL", "https://github.com")
    api_url = os.environ.get("GITHUB_API_URL", "https://api.github.com")
    workspace = os.environ.get("GITHUB_WORKSPACE", os.getcwd())
    return {
        "event_name": event_name,
        "repository": repo,
        "sha": sha,
        "event_path": event_path,
        "server_url": server_url,
        "api_url": api_url,
        "workspace": workspace,
    }


def main() -> int:
    mode = get_input("mode", "coverage")
    token = get_input("github-token", "") or os.environ.get("GITHUB_TOKEN", "")
    compare_branch = get_input("compare-branch", "origin/main")
    fail_under = float(get_input("fail-under", "0"))
    fail_on_threshold = get_bool_input("fail-on-threshold", default=True)

    github_ctx = get_github_context()

    # Change to the workspace directory
    workspace = github_ctx["workspace"]
    if os.path.isdir(workspace):
        os.chdir(workspace)

    # Step 1: Ensure git history is sufficient for diff-cover
    print("::group::Git Setup")
    ensure_git_history(compare_branch)
    print("::endgroup::")

    # Step 2: Build the CLI command
    print("::group::Building diff-cover command")
    cmd = build_command(
        mode=mode,
        coverage_files=get_input("coverage-files"),
        violations=get_input("violations"),
        quality_input_reports=get_input("quality-input-reports"),
        quality_options=get_input("quality-options"),
        compare_branch=compare_branch,
        diff_range_notation=get_input("diff-range-notation", "..."),
        diff_file=get_input("diff-file"),
        ignore_staged=get_bool_input("ignore-staged"),
        ignore_unstaged=get_bool_input("ignore-unstaged"),
        include_untracked=get_bool_input("include-untracked"),
        ignore_whitespace=get_bool_input("ignore-whitespace"),
        exclude=get_input("exclude"),
        include=get_input("include"),
        src_roots=get_input("src-roots"),
        expand_coverage_report=get_bool_input("expand-coverage-report"),
        show_uncovered=get_bool_input("show-uncovered"),
        quiet=get_bool_input("quiet"),
        config_file=get_input("config-file"),
        fail_under=fail_under,
    )
    print(f"Command: {' '.join(cmd)}")
    print("::endgroup::")

    # Step 3: Execute diff-cover/diff-quality
    print("::group::Running diff-cover")
    result = run_diff_cover(cmd)
    print("::endgroup::")

    # Step 4: Parse the JSON report
    json_report_path = "/tmp/dc-report.json"
    md_report_path = "/tmp/dc-report.md"
    report = parse_report(json_report_path)

    threshold_met = report.total_percent_covered >= fail_under

    # Step 5: Post PR comment if enabled
    comment_id = ""
    if get_bool_input("post-comment", default=True) and token:
        print("::group::PR Comment")
        comment_id = post_or_update_comment(
            token=token,
            api_url=github_ctx["api_url"],
            repository=github_ctx["repository"],
            event_name=github_ctx["event_name"],
            event_path=github_ctx["event_path"],
            sha=github_ctx["sha"],
            report=report,
            mode=mode,
            fail_under=fail_under,
            threshold_met=threshold_met,
            identifier=get_input("comment-identifier", "diff-cover-action"),
            md_report_path=md_report_path,
        )
        print("::endgroup::")

    # Step 6: Create annotations if enabled
    if get_bool_input("create-annotations", default=True):
        print("::group::Annotations")
        create_annotations(
            report=report,
            mode=mode,
            annotation_type=get_input("annotation-type", "warning"),
            limit=int(get_input("annotation-limit", "50")),
        )
        print("::endgroup::")

    # Step 7: Generate badge if enabled
    badge_path = ""
    if get_bool_input("create-badge"):
        badge_path = generate_badge(
            percent=report.total_percent_covered,
            mode=mode,
            filename=get_input("badge-filename", "diff-cover-badge.json"),
        )
        print(f"Badge JSON written to: {badge_path}")

    # Step 8: Write outputs and step summary
    write_outputs(
        report=report,
        threshold_met=threshold_met,
        comment_id=comment_id,
        json_report_path=json_report_path,
        badge_path=badge_path,
        exit_code=result.exit_code,
    )
    write_step_summary(
        report=report,
        mode=mode,
        fail_under=fail_under,
        threshold_met=threshold_met,
    )

    # Step 9: Determine exit code
    if not threshold_met and fail_on_threshold:
        print(
            f"::error::Diff coverage {report.total_percent_covered:.1f}% "
            f"is below the threshold of {fail_under:.1f}%"
        )
        return 1

    if result.exit_code not in (0, 1):
        # exit_code 1 from diff-cover means threshold failed, which we handle above.
        # Any other non-zero exit code is a real error.
        print(f"::error::diff-cover exited with unexpected code {result.exit_code}")
        return result.exit_code

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        traceback.print_exc()
        print(f"::error::Unexpected error: {traceback.format_exc()}")
        sys.exit(1)
