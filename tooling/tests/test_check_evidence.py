from __future__ import annotations

import json
import subprocess
from pathlib import Path

from docket.check_evidence import check_evidence
from docket.verify_cmd import verify
from tests.conftest import write_audit, write_ticket


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        check=True,
    ).stdout


def _complete_evidence(
    *,
    command: str,
    exit_code: str,
    log: str,
    ran_at: str,
    git_head: str,
    tree_fingerprint: str,
    attestation: str,
    ac_how: str = "true",
    ac_result: str = "pass",
    method: str = "command",
    missing_how: bool = False,
) -> str:
    how_line = "" if missing_how else f"how: {ac_how}"
    return f"""
### Project verify

```text
command: {command}
exit: {exit_code}
log: {log}
ran_at: {ran_at}
git_head: {git_head}
tree_fingerprint: {tree_fingerprint}
attestation: {attestation}
```

### Acceptance criteria

```text
id: AC-1
criterion: does the thing
method: {method}
{how_line}
result: {ac_result}
evidence: {log}
notes:
```

### Scope review

```text
diff_vs_files_touched: match
extras: none
justified: n/a
notes: none
```
"""


def test_complete_evidence_pass(git_repo: Path):
    write_audit(git_repo, "true")
    ticket = write_ticket(
        git_repo, files=["README.md"], acs=["AC-1: does the thing"]
    )
    att = verify(git_repo, git_repo / "PROJECT_AUDIT.md", ticket)
    latest = json.loads((git_repo / ".docket/verify/latest.json").read_text())
    evidence = _complete_evidence(
        command=att.command,
        exit_code=str(att.exit),
        log=att.log,
        ran_at=att.ran_at,
        git_head=att.git_head,
        tree_fingerprint=att.tree_fingerprint,
        attestation=latest["attestation"],
    )
    ticket = write_ticket(
        git_repo,
        files=["README.md"],
        acs=["AC-1: does the thing"],
        evidence=evidence,
    )
    result = check_evidence(ticket, git_repo)
    assert result.ok, result.messages


def test_missing_ac_fails(git_repo: Path):
    write_audit(git_repo, "true")
    ticket = write_ticket(
        git_repo, files=["README.md"], acs=["AC-1: a", "AC-2: b"]
    )
    att = verify(git_repo, git_repo / "PROJECT_AUDIT.md", ticket)
    latest = json.loads((git_repo / ".docket/verify/latest.json").read_text())
    evidence = _complete_evidence(
        command=att.command,
        exit_code="0",
        log=att.log,
        ran_at=att.ran_at,
        git_head=att.git_head,
        tree_fingerprint=att.tree_fingerprint,
        attestation=latest["attestation"],
    )
    # Ticket has AC-1 and AC-2 but evidence only AC-1
    ticket = write_ticket(
        git_repo,
        files=["README.md"],
        acs=["AC-1: a", "AC-2: b"],
        evidence=evidence,
    )
    result = check_evidence(ticket, git_repo)
    assert not result.ok
    assert any("AC-2" in m for m in result.messages)


def test_missing_how_fails(git_repo: Path):
    write_audit(git_repo, "true")
    ticket = write_ticket(git_repo, files=["README.md"], acs=["AC-1: a"])
    att = verify(git_repo, git_repo / "PROJECT_AUDIT.md", ticket)
    latest = json.loads((git_repo / ".docket/verify/latest.json").read_text())
    evidence = _complete_evidence(
        command=att.command,
        exit_code="0",
        log=att.log,
        ran_at=att.ran_at,
        git_head=att.git_head,
        tree_fingerprint=att.tree_fingerprint,
        attestation=latest["attestation"],
        missing_how=True,
    )
    ticket = write_ticket(
        git_repo, files=["README.md"], acs=["AC-1: a"], evidence=evidence
    )
    result = check_evidence(ticket, git_repo)
    assert not result.ok
    assert any("how" in m for m in result.messages)


def test_invalid_method_fails(git_repo: Path):
    write_audit(git_repo, "true")
    ticket = write_ticket(git_repo, files=["README.md"], acs=["AC-1: a"])
    att = verify(git_repo, git_repo / "PROJECT_AUDIT.md", ticket)
    latest = json.loads((git_repo / ".docket/verify/latest.json").read_text())
    evidence = _complete_evidence(
        command=att.command,
        exit_code="0",
        log=att.log,
        ran_at=att.ran_at,
        git_head=att.git_head,
        tree_fingerprint=att.tree_fingerprint,
        attestation=latest["attestation"],
        method="vibes",
    )
    ticket = write_ticket(
        git_repo, files=["README.md"], acs=["AC-1: a"], evidence=evidence
    )
    result = check_evidence(ticket, git_repo)
    assert not result.ok


def test_result_fail_fails(git_repo: Path):
    write_audit(git_repo, "true")
    ticket = write_ticket(git_repo, files=["README.md"], acs=["AC-1: a"])
    att = verify(git_repo, git_repo / "PROJECT_AUDIT.md", ticket)
    latest = json.loads((git_repo / ".docket/verify/latest.json").read_text())
    evidence = _complete_evidence(
        command=att.command,
        exit_code="0",
        log=att.log,
        ran_at=att.ran_at,
        git_head=att.git_head,
        tree_fingerprint=att.tree_fingerprint,
        attestation=latest["attestation"],
        ac_result="fail",
    )
    ticket = write_ticket(
        git_repo, files=["README.md"], acs=["AC-1: a"], evidence=evidence
    )
    result = check_evidence(ticket, git_repo)
    assert not result.ok


def test_project_exit_nonzero_fails(git_repo: Path):
    write_audit(git_repo, "false")
    ticket = write_ticket(git_repo, files=["README.md"], acs=["AC-1: a"])
    att = verify(git_repo, git_repo / "PROJECT_AUDIT.md", ticket)
    latest = json.loads((git_repo / ".docket/verify/latest.json").read_text())
    evidence = _complete_evidence(
        command=att.command,
        exit_code=str(att.exit),
        log=att.log,
        ran_at=att.ran_at,
        git_head=att.git_head,
        tree_fingerprint=att.tree_fingerprint,
        attestation=latest["attestation"],
    )
    ticket = write_ticket(
        git_repo, files=["README.md"], acs=["AC-1: a"], evidence=evidence
    )
    result = check_evidence(ticket, git_repo)
    assert not result.ok
    assert any("exit must be 0" in m for m in result.messages)


def test_fake_exit_does_not_match_attestation(git_repo: Path):
    write_audit(git_repo, "false")  # real exit nonzero
    ticket = write_ticket(git_repo, files=["README.md"], acs=["AC-1: a"])
    att = verify(git_repo, git_repo / "PROJECT_AUDIT.md", ticket)
    latest = json.loads((git_repo / ".docket/verify/latest.json").read_text())
    evidence = _complete_evidence(
        command=att.command,
        exit_code="0",  # forged
        log=att.log,
        ran_at=att.ran_at,
        git_head=att.git_head,
        tree_fingerprint=att.tree_fingerprint,
        attestation=latest["attestation"],
    )
    ticket = write_ticket(
        git_repo, files=["README.md"], acs=["AC-1: a"], evidence=evidence
    )
    result = check_evidence(ticket, git_repo)
    assert not result.ok
    assert any("does not match attestation" in m for m in result.messages)


def test_stale_after_edit(git_repo: Path):
    write_audit(git_repo, "true")
    ticket = write_ticket(git_repo, files=["README.md"], acs=["AC-1: a"])
    att = verify(git_repo, git_repo / "PROJECT_AUDIT.md", ticket)
    latest = json.loads((git_repo / ".docket/verify/latest.json").read_text())
    evidence = _complete_evidence(
        command=att.command,
        exit_code="0",
        log=att.log,
        ran_at=att.ran_at,
        git_head=att.git_head,
        tree_fingerprint=att.tree_fingerprint,
        attestation=latest["attestation"],
    )
    ticket = write_ticket(
        git_repo, files=["README.md"], acs=["AC-1: a"], evidence=evidence
    )
    assert check_evidence(ticket, git_repo).ok, check_evidence(ticket, git_repo).messages
    # modify implementation after verify
    (git_repo / "README.md").write_text("changed\n", encoding="utf-8")
    result = check_evidence(ticket, git_repo)
    assert not result.ok
    assert any("STALE" in m for m in result.messages)


# --- `tests:` evidence (verified against the attested verify log) ---

from docket.check_evidence import title_problems  # noqa: E402

PLAYWRIGHT_LOG = """\
Running 4 tests using 2 workers
  ✓  1 [chromium] › tests/login.spec.ts:5:3 › auth › logs in with email (1.2s)
  ✘  2 [chromium] › tests/login.spec.ts:20:3 › auth › rejects bad password (3.0s)
  -  3 [chromium] › tests/login.spec.ts:31:3 › auth › signs up with SSO
  ✓  4 [chromium] › tests/cart.spec.ts:8:3 › cart › adds an item (0.8s)
  1 failed
"""

PYTEST_LOG = """\
tests/test_cart.py::test_add_item PASSED                                 [ 25%]
tests/test_cart.py::test_remove_item FAILED                              [ 50%]
tests/test_cart.py::test_discount SKIPPED (no coupon service)            [ 75%]
tests/test_cart.py::test_total PASSED                                    [100%]
FAILED tests/test_cart.py::test_remove_item - AssertionError: 1 != 0
"""


def test_title_problems_playwright():
    assert title_problems(["logs in with email", "adds an item"], PLAYWRIGHT_LOG) == []
    problems = title_problems(
        ["rejects bad password", "signs up with SSO", "logs out"], PLAYWRIGHT_LOG
    )
    assert "FAILED" in problems[0] and "rejects bad password" in problems[0]
    assert "SKIPPED" in problems[1] and "signs up with SSO" in problems[1]
    assert "not found" in problems[2] and "logs out" in problems[2]


def test_title_problems_pytest():
    assert title_problems(["test_add_item", "test_total"], PYTEST_LOG) == []
    problems = title_problems(["test_remove_item", "test_discount", "test_gone"], PYTEST_LOG)
    assert "FAILED" in problems[0]
    assert "SKIPPED" in problems[1]
    assert "not found" in problems[2]


def _tests_evidence(att, latest, tests: list[str], with_prose: bool = False) -> str:
    titles = "\n".join(f"- {t}" for t in tests)
    prose = f"evidence: {att.log}\n" if with_prose else ""
    return f"""
### Project verify

```text
command: {att.command}
exit: {att.exit}
log: {att.log}
ran_at: {att.ran_at}
git_head: {att.git_head}
tree_fingerprint: {att.tree_fingerprint}
attestation: {latest["attestation"]}
```

### Acceptance criteria

```text
id: AC-1
criterion: does the thing
method: test
how: npx playwright test
result: pass
{prose}tests:
{titles}
notes:
```

### Scope review

```text
diff_vs_files_touched: match
extras: none
justified: n/a
notes: none
```
"""


def _run_with_log(git_repo: Path, log_text: str, tests: list[str]):
    # Exit 0 even with a failed line in the log: the title check must catch it.
    (git_repo / "run.log").write_text(log_text, encoding="utf-8")
    _git(git_repo, "add", "run.log")
    _git(git_repo, "commit", "-m", "fixture")
    write_audit(git_repo, "cat run.log")
    ticket = write_ticket(git_repo, files=["README.md"])
    att = verify(git_repo, git_repo / "PROJECT_AUDIT.md", ticket)
    latest = json.loads((git_repo / ".docket/verify/latest.json").read_text())
    ticket = write_ticket(
        git_repo, files=["README.md"], evidence=_tests_evidence(att, latest, tests)
    )
    return check_evidence(ticket, git_repo)


def test_tests_evidence_passes_without_prose(git_repo: Path):
    result = _run_with_log(git_repo, PLAYWRIGHT_LOG, ["logs in with email", "adds an item"])
    assert result.ok, result.messages


def test_tests_evidence_fails_naming_title(git_repo: Path):
    result = _run_with_log(git_repo, PYTEST_LOG, ["test_add_item", "test_remove_item"])
    assert not result.ok
    assert any("AC-1" in m and "test_remove_item" in m for m in result.messages)
    assert not any("test_add_item" in m for m in result.messages if m.startswith("FAIL"))


def test_tests_evidence_missing_title_fails(git_repo: Path):
    result = _run_with_log(git_repo, PYTEST_LOG, ["test_never_ran"])
    assert not result.ok
    assert any("test_never_ran" in m and "not found" in m for m in result.messages)
