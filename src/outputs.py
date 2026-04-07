"""Write GITHUB_OUTPUT and GITHUB_STEP_SUMMARY for the action."""

from __future__ import annotations

import os
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from src.report_parser import Report

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"


def _append_to_github_file(env_var: str, content: str) -> None:
    """Append content to a file path specified by a GitHub Actions env var."""
    path = os.environ.get(env_var)
    if not path:
        return
    with open(path, "a") as f:
        f.write(content)


def _set_output(name: str, value: str) -> None:
    """Write a single key=value pair to GITHUB_OUTPUT."""
    _append_to_github_file("GITHUB_OUTPUT", f"{name}={value}\n")


def write_outputs(
    *,
    report: Report,
    threshold_met: bool,
    comment_id: str,
    json_report_path: str,
    badge_path: str,
    exit_code: int,
) -> None:
    """Write all action outputs to GITHUB_OUTPUT."""
    _set_output("total-percent", str(int(report.total_percent_covered)))
    _set_output("total-percent-float", f"{report.total_percent_covered:.2f}")
    _set_output("total-lines", str(report.total_num_lines))
    _set_output("total-violations", str(report.total_num_violations))
    _set_output("files-changed", str(len(report.files)))
    _set_output("threshold-met", str(threshold_met).lower())
    _set_output("comment-id", comment_id)
    _set_output("report-json", json_report_path)
    _set_output("badge-json", badge_path)
    _set_output("exit-code", str(exit_code))


def write_step_summary(
    *,
    report: Report,
    mode: str,
    fail_under: float,
    threshold_met: bool,
) -> None:
    """Write a markdown step summary to GITHUB_STEP_SUMMARY."""
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=False,
        keep_trailing_newline=True,
    )
    template = env.get_template("step_summary.md.j2")

    if report.total_percent_covered >= 90:
        icon = "white_check_mark"
    elif report.total_percent_covered >= 70:
        icon = "large_orange_diamond"
    else:
        icon = "red_circle"

    content = template.render(
        report=report,
        mode=mode,
        fail_under=fail_under,
        threshold_met=threshold_met,
        icon=icon,
    )
    _append_to_github_file("GITHUB_STEP_SUMMARY", content)
