from __future__ import annotations

import subprocess
from pathlib import Path

from docket.check_scope import check_scope
from tests.conftest import write_ticket


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        check=True,
    ).stdout


def test_all_in_scope_pass(git_repo: Path):
    baseline = _git(git_repo, "rev-parse", "HEAD").strip()
    (git_repo / "src").mkdir()
    (git_repo / "src" / "export.ts").write_text("a\n", encoding="utf-8")
    (git_repo / "src" / "export.test.ts").write_text("t\n", encoding="utf-8")
    ticket = write_ticket(
        git_repo,
        files=["src/export.ts", "src/export.test.ts"],
        baseline=baseline,
    )
    result = check_scope(ticket, git_repo)
    assert result.ok
    assert not result.extras


def test_out_of_scope_fails(git_repo: Path):
    baseline = _git(git_repo, "rev-parse", "HEAD").strip()
    (git_repo / "src").mkdir()
    (git_repo / "src" / "export.ts").write_text("a\n", encoding="utf-8")
    (git_repo / "src" / "auth.ts").write_text("b\n", encoding="utf-8")
    (git_repo / "package.json").write_text("{}\n", encoding="utf-8")
    ticket = write_ticket(
        git_repo,
        files=["src/export.ts", "src/export.test.ts"],
        baseline=baseline,
    )
    result = check_scope(ticket, git_repo)
    assert not result.ok
    assert "src/auth.ts" in result.extras
    assert "package.json" in result.extras


def test_untracked_out_of_scope_fails(git_repo: Path):
    baseline = _git(git_repo, "rev-parse", "HEAD").strip()
    (git_repo / "secret.env").write_text("x\n", encoding="utf-8")
    ticket = write_ticket(git_repo, files=["src/export.ts"], baseline=baseline)
    result = check_scope(ticket, git_repo)
    assert not result.ok
    assert "secret.env" in result.extras


def test_deleted_file_in_scope(git_repo: Path):
    (git_repo / "src").mkdir()
    (git_repo / "src" / "export.ts").write_text("a\n", encoding="utf-8")
    _git(git_repo, "add", "src/export.ts")
    _git(git_repo, "commit", "-m", "add export")
    baseline = _git(git_repo, "rev-parse", "HEAD").strip()
    (git_repo / "src" / "export.ts").unlink()
    ticket = write_ticket(git_repo, files=["src/export.ts"], baseline=baseline)
    result = check_scope(ticket, git_repo)
    assert result.ok


def test_rename_both_sides_need_scope(git_repo: Path):
    (git_repo / "src").mkdir()
    (git_repo / "src" / "old.ts").write_text("a\n", encoding="utf-8")
    _git(git_repo, "add", "src/old.ts")
    _git(git_repo, "commit", "-m", "old")
    baseline = _git(git_repo, "rev-parse", "HEAD").strip()
    _git(git_repo, "mv", "src/old.ts", "src/new.ts")
    # only new listed → fail on old
    ticket = write_ticket(git_repo, files=["src/new.ts"], baseline=baseline)
    result = check_scope(ticket, git_repo)
    assert not result.ok
    assert "src/old.ts" in result.extras

    ticket2 = write_ticket(
        git_repo,
        files=["src/old.ts", "src/new.ts"],
        baseline=baseline,
        name="002.md",
    )
    result2 = check_scope(ticket2, git_repo)
    assert result2.ok


def test_directory_allowed(git_repo: Path):
    baseline = _git(git_repo, "rev-parse", "HEAD").strip()
    (git_repo / "src" / "export").mkdir(parents=True)
    (git_repo / "src" / "export" / "a.ts").write_text("a\n", encoding="utf-8")
    ticket = write_ticket(git_repo, files=["src/export/"], baseline=baseline)
    result = check_scope(ticket, git_repo)
    assert result.ok


def test_path_normalization(git_repo: Path):
    baseline = _git(git_repo, "rev-parse", "HEAD").strip()
    (git_repo / "src").mkdir()
    (git_repo / "src" / "export.ts").write_text("a\n", encoding="utf-8")
    ticket = write_ticket(git_repo, files=["./src/export.ts"], baseline=baseline)
    result = check_scope(ticket, git_repo)
    assert result.ok


def test_baseline_required(git_repo: Path):
    ticket = write_ticket(git_repo, files=["src/export.ts"], baseline=None)
    from docket.parse import ParseError
    import pytest

    with pytest.raises(ParseError):
        check_scope(ticket, git_repo)
