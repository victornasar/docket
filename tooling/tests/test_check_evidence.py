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
