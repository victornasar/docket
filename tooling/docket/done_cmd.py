from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from .gitutil import normalize_repo_path, run_git
from .parse import _meta_field

FRESH_SESSION_LINE = "Start a fresh session (/clear) before the next Ticket."

_TICKET_NAME = re.compile(r"\b(\d{3,}-[A-Za-z0-9._-]+\.md)\b")


@dataclass
class DoneResult:
    ok: bool
    messages: list[str] = field(default_factory=list)


def _rel(path: Path, repo: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo.resolve()))
    except ValueError:
        return str(path)


def _status(path: Path) -> str:
    return _meta_field(path.read_text(encoding="utf-8"), "Status").lower()


def dirty_paths(repo: Path) -> list[str]:
    """Uncommitted paths, ignoring `.docket/` (verify logs are scratch)."""
    out = []
    for line in run_git(repo, "status", "--porcelain=v1", "-uall").splitlines():
        path = normalize_repo_path(line[3:].split(" -> ")[-1])
        if path and not path.startswith(".docket/"):
            out.append(path)
    return out


def next_ticket(ticket_path: Path, program: Path | None = None) -> Path | None:
    """The first not-done Ticket listed after this one in a program file.

    A program file is `program` if given, else any non-Ticket `*.md` beside
    the Ticket (e.g. tickets/README.md) that mentions the Ticket's filename.
    """
    folder = ticket_path.parent
    if program is not None:
        candidates = [program]
    else:
        candidates = sorted(
            p for p in folder.glob("*.md") if not _TICKET_NAME.fullmatch(p.name)
        )
    for candidate in candidates:
        if not candidate.is_file():
            continue
        names = list(dict.fromkeys(_TICKET_NAME.findall(candidate.read_text(encoding="utf-8"))))
        if ticket_path.name not in names:
            continue
        for name in names[names.index(ticket_path.name) + 1 :]:
            nxt = folder / name
            if nxt.is_file() and _status(nxt) != "done":
                return nxt
        return None
    return None


def done(ticket_path: Path, repo: Path, *, program: Path | None = None) -> DoneResult:
    """Confirm a Ticket is closed out and print the session handoff. Writes nothing."""
    rel = _rel(ticket_path, repo)
    problems: list[str] = []

    status = _status(ticket_path)
    if status != "done":
        problems.append(f"Ticket status is {status or '(missing)'!r}, not 'done'")

    dirty = dirty_paths(repo)
    if dirty:
        shown = ", ".join(dirty[:5]) + (f" (+{len(dirty) - 5} more)" if len(dirty) > 5 else "")
        problems.append(f"working tree is not clean: {shown}")

    last = run_git(repo, "show", "--name-only", "--format=", "-m", "--first-parent", "HEAD").split()
    if rel not in {normalize_repo_path(p) for p in last}:
        problems.append(f"the last commit does not touch {rel}")

    if problems:
        return DoneResult(ok=False, messages=[f"FAIL: {p}" for p in problems])

    nxt = next_ticket(ticket_path, program)
    messages = [
        f"ticket: {rel}",
        f"status: {status}",
        f"next: {_rel(nxt, repo) if nxt else '(none listed)'}",
        "",
        FRESH_SESSION_LINE,
    ]
    if nxt:
        messages.append(f"Then: docket resume {_rel(nxt, repo)}")
    return DoneResult(ok=True, messages=messages)
