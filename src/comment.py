"""Post or update idempotent PR comments with diff-cover results."""

from __future__ import annotations

import contextlib
import json
from pathlib import Path

import requests
from jinja2 import Environment, FileSystemLoader

from src.report_parser import Report

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"


def _get_pr_number(
    event_name: str, event_path: str, token: str, api_url: str, repository: str, sha: str
) -> int | None:
    """Resolve the PR number from the event context.

    For pull_request events: read directly from the event payload.
    For push events: query the API for PRs associated with the commit.
    """
    if event_name in ("pull_request", "pull_request_target"):
        try:
            with open(event_path) as f:
                event_data = json.load(f)
            return int(event_data["pull_request"]["number"])
        except (FileNotFoundError, KeyError, ValueError):
            return None

    if event_name == "push" and repository and sha:
        headers = _auth_headers(token)
        url = f"{api_url}/repos/{repository}/commits/{sha}/pulls"
        headers["Accept"] = "application/vnd.github.v3+json"
        try:
            resp = requests.get(url, headers=headers, timeout=30)
            if resp.status_code == 200:
                pulls = resp.json()
                if pulls:
                    return int(pulls[0]["number"])
        except (requests.RequestException, KeyError, ValueError):
            pass

    return None


def _is_fork_pr(event_path: str, repository: str) -> bool:
    """Check if the PR is from a fork (limited GITHUB_TOKEN permissions)."""
    try:
        with open(event_path) as f:
            event_data = json.load(f)
        head_repo = event_data.get("pull_request", {}).get("head", {}).get("repo", {})
        head_full_name: str = head_repo.get("full_name", "")
        return head_full_name != "" and head_full_name != repository
    except (FileNotFoundError, KeyError):
        return False


def _auth_headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def _find_existing_comment(
    token: str, api_url: str, repository: str, pr_number: int, identifier: str
) -> int | None:
    """Find an existing comment with our hidden marker."""
    marker = f"<!-- diff-cover-action:{identifier} -->"
    headers = _auth_headers(token)
    url = f"{api_url}/repos/{repository}/issues/{pr_number}/comments"
    page = 1

    per_page = 100
    while True:
        resp = requests.get(
            url, headers=headers, params={"page": page, "per_page": per_page}, timeout=30
        )
        if resp.status_code != 200:
            break

        comments = resp.json()
        if not comments:
            break

        for comment in comments:
            if marker in comment.get("body", ""):
                return int(comment["id"])

        # If we got fewer comments than per_page, there are no more pages
        if len(comments) < per_page:
            break

        page += 1

    return None


def _progress_bar(percent: float, width: int = 20) -> str:
    """Generate a Unicode progress bar. Example: ████████████████░░░░ for 80%."""
    filled = round(percent / 100 * width)
    filled = max(0, min(width, filled))
    return "\u2588" * filled + "\u2591" * (width - filled)


def _status_icon(percent: float) -> str:
    """Return a colored circle emoji based on coverage percentage."""
    if percent >= 90:
        return "\U0001f7e2"  # 🟢
    if percent >= 70:
        return "\U0001f7e1"  # 🟡
    return "\U0001f534"  # 🔴


def _badge_color(percent: float) -> str:
    """Map a coverage percentage to a shields.io color name."""
    if percent >= 90:
        return "brightgreen"
    if percent >= 80:
        return "green"
    if percent >= 70:
        return "yellowgreen"
    if percent >= 60:
        return "yellow"
    if percent >= 40:
        return "orange"
    return "red"


def _render_comment_body(
    *,
    report: Report,
    mode: str,
    fail_under: float,
    threshold_met: bool,
    identifier: str,
    md_report_content: str,
) -> str:
    """Render the PR comment body from a Jinja2 template."""
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=False,
        keep_trailing_newline=True,
    )
    env.filters["progress_bar"] = _progress_bar
    env.filters["status_icon"] = _status_icon
    env.filters["badge_color"] = _badge_color

    template_name = f"comment_{mode}.md.j2"
    template = env.get_template(template_name)

    return template.render(
        report=report,
        mode=mode,
        fail_under=fail_under,
        threshold_met=threshold_met,
        identifier=identifier,
        md_report_content=md_report_content,
    )


def post_or_update_comment(
    *,
    token: str,
    api_url: str,
    repository: str,
    event_name: str,
    event_path: str,
    sha: str,
    report: Report,
    mode: str,
    fail_under: float,
    threshold_met: bool,
    identifier: str,
    md_report_path: str,
) -> str:
    """Post a new PR comment or update an existing one. Returns the comment ID as a string."""
    pr_number = _get_pr_number(event_name, event_path, token, api_url, repository, sha)
    if pr_number is None:
        print("No PR found for this event. Skipping comment.")
        return ""

    if _is_fork_pr(event_path, repository):
        print(
            "::notice::PR is from a fork. GITHUB_TOKEN has read-only permissions. "
            "Skipping comment. Use pull_request_target event for fork PR comments."
        )
        return ""

    # Read the markdown report if available
    md_report_content = ""
    with contextlib.suppress(FileNotFoundError):
        md_report_content = Path(md_report_path).read_text()

    body = _render_comment_body(
        report=report,
        mode=mode,
        fail_under=fail_under,
        threshold_met=threshold_met,
        identifier=identifier,
        md_report_content=md_report_content,
    )

    headers = _auth_headers(token)

    # Check for existing comment
    existing_id = _find_existing_comment(token, api_url, repository, pr_number, identifier)

    if existing_id:
        # Update existing comment
        url = f"{api_url}/repos/{repository}/issues/comments/{existing_id}"
        resp = requests.patch(url, headers=headers, json={"body": body}, timeout=30)
        if resp.status_code == 200:
            print(f"Updated existing PR comment (ID: {existing_id}).")
            return str(existing_id)
        else:
            print(f"::warning::Failed to update comment {existing_id}: {resp.status_code}")
    else:
        # Create new comment
        url = f"{api_url}/repos/{repository}/issues/{pr_number}/comments"
        resp = requests.post(url, headers=headers, json={"body": body}, timeout=30)
        if resp.status_code == 201:
            comment_id = str(resp.json()["id"])
            print(f"Created new PR comment (ID: {comment_id}).")
            return comment_id
        else:
            print(f"::warning::Failed to create comment: {resp.status_code}")

    return ""
