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
