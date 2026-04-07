"""Tests for src/git_setup.py."""

from __future__ import annotations

from unittest.mock import patch, MagicMock
import subprocess

from src.git_setup import ensure_git_history, _is_shallow, _has_merge_base


class TestIsShallow:
    @patch("src.git_setup._run_git")
    def test_shallow_repo(self, mock_run: MagicMock) -> None:
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="true\n", stderr=""
        )
        assert _is_shallow() is True

    @patch("src.git_setup._run_git")
    def test_not_shallow_repo(self, mock_run: MagicMock) -> None:
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="false\n", stderr=""
        )
        assert _is_shallow() is False


class TestHasMergeBase:
    @patch("src.git_setup._run_git")
    def test_merge_base_found(self, mock_run: MagicMock) -> None:
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="abc123\n", stderr=""
        )
        assert _has_merge_base("origin/main") is True

    @patch("src.git_setup._run_git")
    def test_merge_base_not_found(self, mock_run: MagicMock) -> None:
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=1, stdout="", stderr="fatal: no merge base"
        )
        assert _has_merge_base("origin/main") is False


class TestEnsureGitHistory:
    @patch("src.git_setup._has_merge_base", return_value=True)
    @patch("src.git_setup._fetch_compare_branch")
    @patch("src.git_setup._is_shallow", return_value=True)
    def test_shallow_with_merge_base_after_fetch(
        self, mock_shallow: MagicMock, mock_fetch: MagicMock, mock_merge: MagicMock
    ) -> None:
        ensure_git_history("origin/main")
        mock_fetch.assert_called_once_with("origin/main")

    @patch("src.git_setup._is_shallow", return_value=False)
    def test_not_shallow_skips(self, mock_shallow: MagicMock) -> None:
        ensure_git_history("origin/main")
        # Should return early with no errors

    @patch("src.git_setup._run_git")
    @patch("src.git_setup._has_merge_base")
    @patch("src.git_setup._fetch_compare_branch")
    @patch("src.git_setup._is_shallow", return_value=True)
    def test_progressive_deepening(
        self,
        mock_shallow: MagicMock,
        mock_fetch: MagicMock,
        mock_merge: MagicMock,
        mock_run: MagicMock,
    ) -> None:
        # First call after fetch: no merge-base
        # Second call after deepen 100: no merge-base
        # Third call after deepen 500: found!
        mock_merge.side_effect = [False, False, True]
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="", stderr=""
        )

        ensure_git_history("origin/main")

        # Should have deepened twice (100 and 500)
        deepen_calls = [
            c for c in mock_run.call_args_list
            if "--deepen" in c[0][0]
        ]
        assert len(deepen_calls) == 2
