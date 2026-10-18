from __future__ import annotations

import json
from pathlib import Path

import pytest

from docket.parse import ParseError
from docket.verify_cmd import verify
from tests.conftest import write_audit


def test_verify_success_records_exit_0(git_repo: Path):
    write_audit(git_repo, "true")
    att = verify(git_repo, git_repo / "PROJECT_AUDIT.md")
    assert att.exit == 0
    assert att.git_head
    assert att.tree_fingerprint
    assert (git_repo / att.log).is_file()
    latest = json.loads((git_repo / ".docket/verify/latest.json").read_text())
    assert latest["exit"] == 0
    assert latest["schema"] == "docket.verify.v1"
    log = (git_repo / att.log).read_text()
    assert "----- stdout -----" in log
    assert "----- stderr -----" in log


def test_verify_failure_records_nonzero(git_repo: Path):
    write_audit(git_repo, "false")
    att = verify(git_repo, git_repo / "PROJECT_AUDIT.md")
    assert att.exit != 0


def test_missing_canonical_command_fails(git_repo: Path):
    (git_repo / "PROJECT_AUDIT.md").write_text(
        """# Project Audit: x

## Verification

### Canonical (preferred if present)

```text
command: N/A
purpose:
```
""",
        encoding="utf-8",
    )
    with pytest.raises(ParseError):
        verify(git_repo, git_repo / "PROJECT_AUDIT.md")


def test_stdout_captured(git_repo: Path):
    write_audit(git_repo, "echo hello-docket")
    att = verify(git_repo, git_repo / "PROJECT_AUDIT.md")
    assert att.exit == 0
    log = (git_repo / att.log).read_text()
    assert "hello-docket" in log


# --- failure digest (Ticket 013) ---

from docket.verify_cmd import failure_digest  # noqa: E402


def test_failing_verify_digest_points_at_failures(git_repo: Path):
    write_audit(git_repo, "sh -c 'for i in $(seq 1 200); do echo ok $i; done; echo \"  ✘ checkout › rejects an expired card\"; for i in $(seq 1 30); do echo more $i; done; exit 1'")
    att = verify(git_repo, git_repo / "PROJECT_AUDIT.md")
    assert att.exit != 0
    log_lines = (git_repo / att.log).read_text().splitlines()
    digest = failure_digest(git_repo / att.log)
    assert len(digest) <= 40
    hit = next(line for line in digest if "rejects an expired card" in line)
    number = int(hit.split(":", 1)[0])
    assert "rejects an expired card" in log_lines[number - 1]
    assert digest[-1].startswith(f"{len(log_lines)}: ")


def test_digest_is_capped(git_repo: Path):
    write_audit(git_repo, "sh -c 'for i in $(seq 1 500); do echo FAIL $i; done; exit 1'")
    att = verify(git_repo, git_repo / "PROJECT_AUDIT.md")
    assert len(failure_digest(git_repo / att.log, 25)) == 25
    assert failure_digest(git_repo / att.log, 0) == []


def test_cli_digest_only_on_failure_and_switchable(git_repo: Path, capsys):
    from docket.cli import main

    write_audit(git_repo, "true")
    main(["verify", "--repo", str(git_repo), "--audit", str(git_repo / "PROJECT_AUDIT.md")])
    assert "failure digest" not in capsys.readouterr().out

    write_audit(git_repo, "sh -c 'echo Error: boom; exit 1'")
    main(["verify", "--repo", str(git_repo), "--audit", str(git_repo / "PROJECT_AUDIT.md")])
    out = capsys.readouterr().out
    assert "failure digest" in out and "Error: boom" in out

    main(["verify", "--repo", str(git_repo), "--audit", str(git_repo / "PROJECT_AUDIT.md"), "--digest-lines", "0"])
    assert "failure digest" not in capsys.readouterr().out
    latest = json.loads((git_repo / ".docket/verify/latest.json").read_text())
    assert set(latest) == {"schema", "command", "exit", "log", "ran_at", "git_head", "tree_fingerprint", "repo", "ticket", "attestation"}
