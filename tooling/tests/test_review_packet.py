from __future__ import annotations

import subprocess
from pathlib import Path

from docket.review_packet import build_review_packet
from tests.conftest import write_ticket


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, check=True
    ).stdout.strip()


def test_packet_lists_untracked_in_scope_and_diff_stat(git_repo: Path):
    base = _git(git_repo, "rev-parse", "HEAD")
    ticket = write_ticket(
        git_repo, files=["README.md", "src/new.py", "pkg/"], baseline=base
    )
    (git_repo / "README.md").write_text("changed\nmore\n", encoding="utf-8")
    (git_repo / "src").mkdir()
    (git_repo / "src" / "new.py").write_text("x = 1\n", encoding="utf-8")
    (git_repo / "pkg").mkdir()
    (git_repo / "pkg" / "mod.py").write_text("y = 1\n", encoding="utf-8")
    (git_repo / "stray.txt").write_text("not in scope\n", encoding="utf-8")

    lines = build_review_packet(ticket, git_repo).lines
    text = "\n".join(lines)
    assert "diff_stat: 1 file changed" in text
    assert "  - src/new.py" in lines
    assert "  - pkg/mod.py" in lines
    assert "stray.txt" not in text
    assert "001-test.md" not in text.split("untracked:", 1)[1].split("docket_root")[0]


def test_packet_without_untracked(git_repo: Path):
    base = _git(git_repo, "rev-parse", "HEAD")
    ticket = write_ticket(git_repo, files=["README.md"], baseline=base)
    _git(git_repo, "add", "-A")
    _git(git_repo, "commit", "-m", "ticket")
    text = "\n".join(build_review_packet(ticket, git_repo).lines)
    assert "untracked: none" in text
    assert "diff_stat: 1 file changed" in text
