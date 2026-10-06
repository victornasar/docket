from __future__ import annotations

import json
import subprocess
from pathlib import Path

from docket.pre_review import pre_review
from docket.review_packet import build_review_packet
from docket.verify_cmd import verify
from tests.conftest import write_audit, write_ticket


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


def _fill_evidence(ticket: Path, repo: Path, att, latest: dict) -> None:
    base = _git(repo, "rev-parse", "HEAD")
    # keep existing baseline from ticket if present
    text = ticket.read_text(encoding="utf-8")
    for line in text.splitlines():
        if line.startswith("**Baseline:**"):
            base = line.split(":**", 1)[1].strip()
            break
    evidence = f"""
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
method: command
how: true
result: pass
evidence: {att.log}
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
    write_ticket(
        repo,
        files=["README.md"],
        acs=["AC-1: does the thing"],
        baseline=base,
        evidence=evidence,
        name=ticket.name,
    )


def test_pre_review_blocks_until_evidence_filled(git_repo: Path):
    write_audit(git_repo, "true")
    base = _git(git_repo, "rev-parse", "HEAD")
    ticket = write_ticket(
        git_repo, files=["README.md"], acs=["AC-1: does the thing"], baseline=base
    )
    # First pass: verify ok but evidence empty → blocked at check-evidence
    result = pre_review(
        ticket, git_repo, audit_path=git_repo / "PROJECT_AUDIT.md"
    )
    assert not result.ok
    assert any("check-evidence" in m for m in result.messages)
    assert any("BLOCKED" in m for m in result.messages)

    att = verify(git_repo, git_repo / "PROJECT_AUDIT.md", ticket)
    latest = json.loads((git_repo / ".docket/verify/latest.json").read_text())
    _fill_evidence(ticket, git_repo, att, latest)

    result2 = pre_review(
        ticket,
        git_repo,
        audit_path=git_repo / "PROJECT_AUDIT.md",
        skip_verify=True,
    )
    assert result2.ok, result2.messages


def test_pre_review_fails_on_verify_nonzero(git_repo: Path):
    write_audit(git_repo, "false")
    base = _git(git_repo, "rev-parse", "HEAD")
    ticket = write_ticket(
        git_repo, files=["README.md"], acs=["AC-1: x"], baseline=base
    )
    result = pre_review(
        ticket, git_repo, audit_path=git_repo / "PROJECT_AUDIT.md"
    )
    assert not result.ok
    assert result.exit_code == 1
    assert any("verify exited non-zero" in m for m in result.messages)


def test_review_packet_lists_fresh_context_paths(git_repo: Path):
    write_audit(git_repo, "true")
    base = _git(git_repo, "rev-parse", "HEAD")
    ticket = write_ticket(
        git_repo, files=["README.md"], acs=["AC-1: x"], baseline=base
    )
    att = verify(git_repo, git_repo / "PROJECT_AUDIT.md", ticket)
    latest = json.loads((git_repo / ".docket/verify/latest.json").read_text())
    _fill_evidence(ticket, git_repo, att, latest)

    # Attach fake docket kit pointer
    docket = git_repo / "docket"
    docket.mkdir()
    (docket / "core").mkdir()
    (docket / "core" / "WORKFLOW.md").write_text("# wf\n", encoding="utf-8")

    packet = build_review_packet(ticket, git_repo)
    text = "\n".join(packet.lines)
    assert "ticket:" in text
    assert f"baseline: {base}" in text
    assert "PROJECT_AUDIT.md (found)" in text
    assert "reviewer_role:" in text
    assert "diff_command:" in text
    assert "do NOT establish" in text.lower() or "do NOT establish" in text or "They do NOT" in text
