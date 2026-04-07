"""Tests for src/comment.py."""

from __future__ import annotations

import json
from pathlib import Path

import responses

from src.comment import (
    _find_existing_comment,
    _is_fork_pr,
    _render_comment_body,
    post_or_update_comment,
)
from src.report_parser import FileReport, Report


@responses.activate
def test_find_existing_comment_found() -> None:
    marker = "<!-- diff-cover-action:test-id -->"
    responses.add(
        responses.GET,
        "https://api.github.com/repos/owner/repo/issues/1/comments",
        json=[
            {"id": 100, "body": "some other comment"},
            {"id": 200, "body": f"Coverage report\n{marker}\nDetails here"},
        ],
        status=200,
    )
    result = _find_existing_comment(
        "fake-token", "https://api.github.com", "owner/repo", 1, "test-id"
    )
    assert result == 200


@responses.activate
def test_find_existing_comment_not_found() -> None:
    responses.add(
        responses.GET,
        "https://api.github.com/repos/owner/repo/issues/1/comments",
        json=[{"id": 100, "body": "unrelated comment"}],
        status=200,
    )
    result = _find_existing_comment(
        "fake-token", "https://api.github.com", "owner/repo", 1, "test-id"
    )
    assert result is None


def test_is_fork_pr_true(tmp_path: Path) -> None:
    event = {
        "pull_request": {
            "head": {"repo": {"full_name": "forker/repo"}},
        }
    }
    event_file = tmp_path / "event.json"
    event_file.write_text(json.dumps(event))
    assert _is_fork_pr(str(event_file), "owner/repo") is True


def test_is_fork_pr_false(tmp_path: Path) -> None:
    event = {
        "pull_request": {
            "head": {"repo": {"full_name": "owner/repo"}},
        }
    }
    event_file = tmp_path / "event.json"
    event_file.write_text(json.dumps(event))
    assert _is_fork_pr(str(event_file), "owner/repo") is False


def test_is_fork_pr_missing_file() -> None:
    assert _is_fork_pr("/nonexistent/event.json", "owner/repo") is False


def test_render_comment_body() -> None:
    report = Report(
        report_name="XML",
        diff_name="origin/main...HEAD",
        files=[
            FileReport(path="src/foo.py", percent_covered=85.0, violation_lines=[13, 27]),
        ],
        total_num_lines=20,
        total_num_violations=2,
        total_percent_covered=90.0,
    )
    body = _render_comment_body(
        report=report,
        mode="coverage",
        fail_under=80.0,
        threshold_met=True,
        identifier="test-id",
        md_report_content="",
    )
    assert "<!-- diff-cover-action:test-id -->" in body
    assert "90.0%" in body
    assert "Meets threshold" in body
    assert "src/foo.py" in body


def test_render_comment_body_below_threshold() -> None:
    report = Report(
        report_name="XML",
        diff_name="",
        files=[],
        total_num_lines=10,
        total_num_violations=5,
        total_percent_covered=50.0,
    )
    body = _render_comment_body(
        report=report,
        mode="coverage",
        fail_under=80.0,
        threshold_met=False,
        identifier="test",
        md_report_content="",
    )
    assert "Below threshold" in body


@responses.activate
def test_post_new_comment(tmp_path: Path) -> None:
    event = {"pull_request": {"number": 42, "head": {"repo": {"full_name": "owner/repo"}}}}
    event_file = tmp_path / "event.json"
    event_file.write_text(json.dumps(event))

    # No existing comments
    responses.add(
        responses.GET,
        "https://api.github.com/repos/owner/repo/issues/42/comments",
        json=[],
        status=200,
    )
    # Create comment
    responses.add(
        responses.POST,
        "https://api.github.com/repos/owner/repo/issues/42/comments",
        json={"id": 999},
        status=201,
    )

    report = Report(
        report_name="XML",
        diff_name="",
        files=[],
        total_num_lines=0,
        total_num_violations=0,
        total_percent_covered=100.0,
    )

    result = post_or_update_comment(
        token="fake-token",
        api_url="https://api.github.com",
        repository="owner/repo",
        event_name="pull_request",
        event_path=str(event_file),
        sha="abc123",
        report=report,
        mode="coverage",
        fail_under=0.0,
        threshold_met=True,
        identifier="test-id",
        md_report_path="/nonexistent/report.md",
    )
    assert result == "999"


@responses.activate
def test_update_existing_comment(tmp_path: Path) -> None:
    event = {"pull_request": {"number": 42, "head": {"repo": {"full_name": "owner/repo"}}}}
    event_file = tmp_path / "event.json"
    event_file.write_text(json.dumps(event))

    marker = "<!-- diff-cover-action:test-id -->"
    responses.add(
        responses.GET,
        "https://api.github.com/repos/owner/repo/issues/42/comments",
        json=[{"id": 555, "body": f"old report\n{marker}"}],
        status=200,
    )
    responses.add(
        responses.PATCH,
        "https://api.github.com/repos/owner/repo/issues/comments/555",
        json={"id": 555},
        status=200,
    )

    report = Report(
        report_name="XML",
        diff_name="",
        files=[],
        total_num_lines=0,
        total_num_violations=0,
        total_percent_covered=100.0,
    )

    result = post_or_update_comment(
        token="fake-token",
        api_url="https://api.github.com",
        repository="owner/repo",
        event_name="pull_request",
        event_path=str(event_file),
        sha="abc123",
        report=report,
        mode="coverage",
        fail_under=0.0,
        threshold_met=True,
        identifier="test-id",
        md_report_path="/nonexistent/report.md",
    )
    assert result == "555"
