from __future__ import annotations

from pathlib import Path

from docket.lint_ticket import lint_ticket
from docket.pre_review import pre_review
from tests.conftest import write_audit, write_ticket

BASE = "8fcf685198f57ff412caf2a7bea2ebade075fa28"

BAD_METHOD = """
### Acceptance criteria

```text
id: AC-1
criterion: does the thing
method: test + read
how: pytest
result: pass
evidence: log
```
"""


def _text(result) -> str:
    return "\n".join(result.messages)


def test_clean_ticket_passes(git_repo: Path):
    ticket = write_ticket(
        git_repo, files=["README.md", "src/a.py", "app/[slug]/page.tsx"], baseline=BASE
    )
    result = lint_ticket(ticket)
    assert result.ok, result.messages


def test_set_when_placeholder_baseline_passes(git_repo: Path):
    ticket = write_ticket(git_repo, files=["README.md"], baseline="(set when Implement starts)")
    assert lint_ticket(ticket).ok


def test_invalid_method_fails(git_repo: Path):
    ticket = write_ticket(git_repo, files=["README.md"], baseline=BASE, evidence=BAD_METHOD)
    result = lint_ticket(ticket)
    assert not result.ok
    assert "AC-1: invalid method 'test + read'" in _text(result)


def test_comma_separated_files_touched_fails(git_repo: Path):
    ticket = write_ticket(git_repo, files=["src/a.py, src/b.py"], baseline=BASE)
    result = lint_ticket(ticket)
    assert not result.ok
    assert "no commas" in _text(result)


def test_glob_files_touched_fails(git_repo: Path):
    ticket = write_ticket(git_repo, files=["src/*.py"], baseline=BASE)
    assert "globs" in _text(lint_ticket(ticket))


def test_missing_headers_fail(git_repo: Path):
    ticket = write_ticket(git_repo, files=["README.md"], baseline=BASE)
    text = ticket.read_text(encoding="utf-8")
    text = text.replace("## Rollback plan", "## Rollback").replace("**Status:**", "Status:")
    ticket.write_text(text, encoding="utf-8")
    result = lint_ticket(ticket)
    assert not result.ok
    assert "missing '## Rollback plan' section" in _text(result)
    assert "missing **Status:** line" in _text(result)


def test_bad_or_missing_baseline_fails(git_repo: Path):
    assert "Baseline" in _text(lint_ticket(write_ticket(git_repo, files=["README.md"])))
    ticket = write_ticket(git_repo, files=["README.md"], baseline="main")
    assert "commit hash" in _text(lint_ticket(ticket))
    assert lint_ticket(ticket, baseline_override="main").ok


def test_pre_review_runs_lint_before_verify(git_repo: Path):
    # The verify command would leave a marker; lint failing first must stop it.
    write_audit(git_repo, "touch verify-ran")
    ticket = write_ticket(git_repo, files=["a.py, b.py"], baseline=BASE)
    result = pre_review(ticket, git_repo, audit_path=git_repo / "PROJECT_AUDIT.md")
    assert not result.ok
    assert result.messages[0] == "=== docket lint-ticket ==="
    assert any("lint-ticket failed" in m for m in result.messages)
    assert not (git_repo / "verify-ran").exists()
