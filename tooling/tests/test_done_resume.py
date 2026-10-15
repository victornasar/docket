from __future__ import annotations

import subprocess
from pathlib import Path

from docket.done_cmd import FRESH_SESSION_LINE, done
from docket.resume_cmd import MAX_LINES, resume
from docket.verify_cmd import verify
from tests.conftest import write_audit, write_ticket


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, check=True
    ).stdout.strip()


def _set_status(ticket: Path, status: str) -> None:
    text = ticket.read_text(encoding="utf-8")
    ticket.write_text(
        text.replace("**Status:** in-progress", f"**Status:** {status}"), encoding="utf-8"
    )


def _commit_all(repo: Path, msg: str = "work") -> None:
    _git(repo, "add", "-A")
    _git(repo, "commit", "-m", msg)


def _text(lines: list[str]) -> str:
    return "\n".join(lines)


# --- docket done ---


def test_done_refuses_ticket_not_done(git_repo: Path):
    ticket = write_ticket(git_repo, files=["README.md"])
    _commit_all(git_repo)
    result = done(ticket, git_repo)
    assert not result.ok
    assert "not 'done'" in _text(result.messages)
    assert FRESH_SESSION_LINE not in result.messages


def test_done_refuses_dirty_tree(git_repo: Path):
    ticket = write_ticket(git_repo, files=["README.md"])
    _set_status(ticket, "done")
    _commit_all(git_repo)
    (git_repo / "README.md").write_text("changed\n", encoding="utf-8")
    result = done(ticket, git_repo)
    assert not result.ok
    assert "not clean" in _text(result.messages) and "README.md" in _text(result.messages)


def test_done_refuses_when_last_commit_skips_ticket(git_repo: Path):
    ticket = write_ticket(git_repo, files=["README.md"])
    _set_status(ticket, "done")
    _commit_all(git_repo)
    (git_repo / "other.txt").write_text("x\n", encoding="utf-8")
    _commit_all(git_repo, "unrelated")
    result = done(ticket, git_repo)
    assert not result.ok
    assert "last commit does not touch" in _text(result.messages)


def test_done_prints_handoff_with_next_ticket(git_repo: Path):
    first = write_ticket(git_repo, files=["README.md"], name="001-first.md")
    second = write_ticket(git_repo, files=["README.md"], name="002-second.md")
    third = write_ticket(git_repo, files=["README.md"], name="003-third.md")
    _set_status(second, "done")
    (git_repo / "tickets" / "README.md").write_text(
        "| 001 | [first](001-first.md) |\n| 002 | [second](002-second.md) |\n"
        "| 003 | [third](003-third.md) |\n",
        encoding="utf-8",
    )
    _set_status(first, "done")
    # .docket/ verify scratch does not count as a dirty tree
    write_audit(git_repo, "true")
    _commit_all(git_repo)
    verify(git_repo, git_repo / "PROJECT_AUDIT.md", first)

    before = _git(git_repo, "status", "--porcelain")
    result = done(first, git_repo)
    assert result.ok, result.messages
    text = _text(result.messages)
    assert "ticket: tickets/001-first.md" in text
    assert "status: done" in text
    assert "next: tickets/003-third.md" in text  # 002 is already done
    assert FRESH_SESSION_LINE in result.messages
    assert _git(git_repo, "status", "--porcelain") == before
    assert third.is_file()


def test_done_without_program_file(git_repo: Path):
    ticket = write_ticket(git_repo, files=["README.md"])
    _set_status(ticket, "done")
    _commit_all(git_repo)
    result = done(ticket, git_repo)
    assert result.ok
    assert "next: (none listed)" in result.messages


# --- docket resume ---


def test_resume_brief_covers_state(git_repo: Path):
    base = _git(git_repo, "rev-parse", "HEAD")
    write_audit(git_repo, "true")
    evidence = """
### Acceptance criteria

```text
id: AC-1
criterion: a
method: command
how: true
result: pass
evidence: log
```
"""
    ticket = write_ticket(
        git_repo, files=["README.md", "new.py"], acs=["AC-1: a", "AC-2: b"],
        baseline=base, evidence=evidence,
    )
    (git_repo / "README.md").write_text("changed\n", encoding="utf-8")
    (git_repo / "new.py").write_text("x = 1\n", encoding="utf-8")
    verify(git_repo, git_repo / "PROJECT_AUDIT.md", ticket)

    result = resume(git_repo, ticket)
    assert result.ok
    assert len(result.lines) < 40
    text = _text(result.lines)
    assert "# Resume: test" in text
    assert "status: in-progress" in text
    assert f"baseline: {base}" in text
    assert "AC-1: pass" in text and "AC-2: blank" in text
    assert "fresh" in text and "STALE" not in text
    assert "  README.md" in text
    assert "new.py (untracked)" in text

    (git_repo / "new.py").write_text("x = 2\n", encoding="utf-8")
    assert "STALE" in _text(resume(git_repo, ticket).lines)


def test_resume_caps_length_and_finds_open_ticket(git_repo: Path):
    base = _git(git_repo, "rev-parse", "HEAD")
    write_ticket(git_repo, files=["gen/"], baseline=base)
    for i in range(80):
        (git_repo / "gen").mkdir(exist_ok=True)
        (git_repo / "gen" / f"f{i:02}.txt").write_text("x\n", encoding="utf-8")
    result = resume(git_repo)  # no ticket given → the open one under tickets/
    assert result.ok
    assert len(result.lines) <= MAX_LINES < 40
    assert "more (git diff --stat" in _text(result.lines)
    assert "attestation: none" in _text(result.lines)


def test_resume_without_open_ticket(git_repo: Path):
    assert not resume(git_repo).ok
