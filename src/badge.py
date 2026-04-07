"""Generate shields.io endpoint badge JSON for coverage/quality percentage."""

from __future__ import annotations

import json


def _color_for_percent(percent: float) -> str:
    """Return a shields.io color string based on the coverage percentage."""
    if percent >= 90:
        return "brightgreen"
    elif percent >= 80:
        return "green"
    elif percent >= 70:
        return "yellowgreen"
    elif percent >= 60:
        return "yellow"
    elif percent >= 40:
        return "orange"
    else:
        return "red"


def generate_badge(
    *,
    percent: float,
    mode: str,
    filename: str = "diff-cover-badge.json",
) -> str:
    """Generate a shields.io endpoint badge JSON file.

    The JSON follows the shields.io endpoint badge schema:
    https://shields.io/badges/endpoint-badge

    Returns the path where the file was written.
    """
    label = "diff coverage" if mode == "coverage" else "diff quality"

    badge = {
        "schemaVersion": 1,
        "label": label,
        "message": f"{percent:.1f}%",
        "color": _color_for_percent(percent),
    }

    with open(filename, "w") as f:
        json.dump(badge, f, indent=2)

    return filename
