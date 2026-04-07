"""Execute diff-cover/diff-quality subprocess with streaming output."""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass


@dataclass
class RunResult:
    exit_code: int
    stdout: str
    stderr: str


def run_diff_cover(cmd: list[str]) -> RunResult:
    """Execute a diff-cover or diff-quality command.

    Streams stdout in real time so users see progress in the Actions log.
    Captures both stdout and stderr for later processing.

    Returns a RunResult with the exit code, full stdout, and full stderr.
    Does NOT raise on non-zero exit codes — the caller handles threshold logic.
    """
    stdout_lines: list[str] = []
    stderr_lines: list[str] = []

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )

    assert process.stdout is not None
    assert process.stderr is not None

    # Stream stdout line-by-line
    for line in process.stdout:
        line_stripped = line.rstrip("\n")
        stdout_lines.append(line_stripped)
        print(line_stripped, file=sys.stdout, flush=True)

    # Read remaining stderr after stdout is done
    stderr_output = process.stderr.read()
    if stderr_output:
        for line in stderr_output.splitlines():
            stderr_lines.append(line)
            print(line, file=sys.stderr, flush=True)

    process.wait()

    return RunResult(
        exit_code=process.returncode,
        stdout="\n".join(stdout_lines),
        stderr="\n".join(stderr_lines),
    )
