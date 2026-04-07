"""Generate GitHub annotations for uncovered or violating lines.

Uses workflow commands (::warning, ::error, ::notice) which appear inline on PR diffs.
"""

from __future__ import annotations

from src.report_parser import Report


def _group_consecutive_lines(lines: list[int]) -> list[tuple[int, int]]:
    """Group consecutive line numbers into (start, end) ranges.

    Example: [1, 2, 3, 7, 8, 12] -> [(1, 3), (7, 8), (12, 12)]
    """
    if not lines:
        return []

    sorted_lines = sorted(set(lines))
    groups: list[tuple[int, int]] = []
    start = sorted_lines[0]
    end = start

    for line in sorted_lines[1:]:
        if line == end + 1:
            end = line
        else:
            groups.append((start, end))
            start = line
            end = line

    groups.append((start, end))
    return groups


def create_annotations(
    *,
    report: Report,
    mode: str,
    annotation_type: str = "warning",
    limit: int = 50,
) -> None:
    """Emit GitHub workflow command annotations for uncovered/violating lines.

    Prioritizes files with the lowest coverage first. Groups consecutive lines
    into ranges to maximize information density.

    Args:
        report: Parsed diff-cover report.
        mode: "coverage" or "quality".
        annotation_type: One of "warning", "error", "notice".
        limit: Maximum annotations to emit.
    """
    if annotation_type not in ("warning", "error", "notice"):
        annotation_type = "warning"

    label = "not covered by tests" if mode == "coverage" else "has quality violations"

    # Sort files by coverage ascending (worst first)
    sorted_files = sorted(report.files, key=lambda f: f.percent_covered)

    count = 0
    for file_report in sorted_files:
        if count >= limit:
            break

        if not file_report.violation_lines:
            continue

        groups = _group_consecutive_lines(file_report.violation_lines)

        for start, end in groups:
            if count >= limit:
                break

            if start == end:
                msg = f"Line {start} is {label}"
                line_spec = f"line={start}"
            else:
                msg = f"Lines {start}-{end} are {label}"
                line_spec = f"line={start},endLine={end}"

            title = "Uncovered Line" if mode == "coverage" else "Quality Violation"
            print(f"::{annotation_type} file={file_report.path},{line_spec},title={title}::{msg}")
            count += 1

    if count > 0:
        print(f"Created {count} annotation(s).")
    else:
        print("No annotations needed.")
