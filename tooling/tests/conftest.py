from __future__ import annotations

import subprocess
from pathlib import Path

import pytest


@pytest.fixture
def git_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test")
    (repo / "README.md").write_text("hi\n", encoding="utf-8")
    _git(repo, "add", "README.md")
    _git(repo, "commit", "-m", "init")
    return repo


def _git(repo: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        check=True,
    )
    return proc.stdout


def write_ticket(
    repo: Path,
    *,
    files: list[str],
    acs: list[str] | None = None,
    baseline: str | None = None,
    evidence: str = "",
    name: str = "001-test.md",
) -> Path:
    tickets = repo / "tickets"
    tickets.mkdir(exist_ok=True)
    acs = acs or ["AC-1: does the thing"]
    ac_block = []
    for i, a in enumerate(acs):
        if a.startswith("AC-"):
            ac_block.append(f"- [ ] {a}")
        else:
            ac_block.append(f"- [ ] AC-{i+1}: {a}")
    base_line = f"**Baseline:** {baseline}\n" if baseline else ""
    body = f"""# Ticket: test

**Status:** in-progress
{base_line}
## Problem

Test problem.

## Approach

1. Do it.

## Files touched

{chr(10).join(f'- {p}' for p in files)}

## Acceptance criteria

{chr(10).join(ac_block)}

## Rollback plan

Revert the commit.

## Rules check

None.

## Evidence

{evidence}

## Notes for the Reviewer

—
"""
    path = tickets / name
    path.write_text(body, encoding="utf-8")
    return path


def write_audit(repo: Path, command: str = "true") -> Path:
    path = repo / "PROJECT_AUDIT.md"
    path.write_text(
        f"""# Project Audit: test

## Stack

test

## Structure

—

## Conventions

—

## Test setup

—

## Verification

### Canonical (preferred if present)

```text
command: {command}
purpose: stage2 test verify
```

### Test

```text
command: N/A
purpose:
```

## Build / run / deploy commands

—

## Risky areas

—

## Environments

—

## Existing Rules exceptions or additions

None.
""",
        encoding="utf-8",
    )
    return path
