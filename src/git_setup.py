"""Handle shallow clone repair for GitHub Actions runners.

GitHub's actions/checkout defaults to --depth=1. diff-cover needs the merge-base
between HEAD and the compare branch to compute the diff. This module progressively
fetches history until the merge-base is available, avoiding a full unshallow on large repos.
"""

from __future__ import annotations

import subprocess


def _run_git(args: list[str], check: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git"] + args,
        capture_output=True,
        text=True,
        check=check,
    )


def _is_shallow() -> bool:
    result = _run_git(["rev-parse", "--is-shallow-repository"])
    return result.stdout.strip() == "true"


def _has_merge_base(compare_branch: str) -> bool:
    result = _run_git(["merge-base", "HEAD", compare_branch])
    return result.returncode == 0


def _fetch_compare_branch(compare_branch: str) -> None:
    """Fetch the compare branch ref so it's available locally."""
    # Extract the remote and branch name
    if "/" in compare_branch:
        remote, branch = compare_branch.split("/", 1)
    else:
        remote = "origin"
        branch = compare_branch

    result = _run_git([
        "fetch", remote, f"{branch}:refs/remotes/{remote}/{branch}", "--depth=1"
    ])
    if result.returncode != 0:
        # Try fetching without depth restriction
        _run_git(["fetch", remote, f"{branch}:refs/remotes/{remote}/{branch}"])


def ensure_git_history(compare_branch: str) -> None:
    """Ensure sufficient git history for diff-cover to compute the merge-base.

    Uses a progressive deepening strategy to avoid fetching the entire repo:
    1. Check if already not shallow -> done
    2. Fetch the compare branch ref
    3. Try merge-base -> done if it works
    4. Progressively deepen (100, 500, 2000 commits)
    5. Last resort: full unshallow
    """
    if not _is_shallow():
        print("Repository is not shallow, git history is sufficient.")
        return

    print(f"Shallow repository detected. Fetching history for compare branch: {compare_branch}")

    # Fetch the compare branch so it's available as a ref
    _fetch_compare_branch(compare_branch)

    # Check if merge-base already works
    if _has_merge_base(compare_branch):
        print("Merge-base found after fetching compare branch.")
        return

    # Progressive deepening
    depths = [100, 500, 2000]
    for depth in depths:
        print(f"Deepening fetch by {depth} commits...")
        _run_git(["fetch", "--deepen", str(depth), "origin"])
        if _has_merge_base(compare_branch):
            print(f"Merge-base found after deepening by {depth} commits.")
            return

    # Last resort: full unshallow
    print("Performing full unshallow fetch (this may take a while on large repos)...")
    result = _run_git(["fetch", "--unshallow", "origin"])
    if result.returncode != 0:
        print(f"::warning::git fetch --unshallow failed: {result.stderr}")

    if _has_merge_base(compare_branch):
        print("Merge-base found after full unshallow.")
        return

    print(
        "::error::Could not find merge-base between HEAD and "
        f"{compare_branch}. Please ensure your checkout step uses "
        "'fetch-depth: 0' or that the compare branch exists."
    )
