from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .gitutil import changed_paths_since, normalize_repo_path
from .parse import ParseError, load_ticket, path_allowed


@dataclass
class ScopeResult:
    ok: bool
    baseline: str
    allowed: list[str]
    actual: list[str]
    extras: list[str]
    messages: list[str]


def check_scope(
    ticket_path: Path,
    repo: Path,
    baseline: str | None = None,
) -> ScopeResult:
    ticket = load_ticket(ticket_path)
    base = (baseline or ticket.baseline or "").strip()
    if not base:
        raise ParseError(
            "Baseline required: pass --baseline <git-ref> or set "
            "**Baseline:** <sha> on the Ticket (commit at Ticket start)."
        )

    allowed = [normalize_repo_path(p) for p in ticket.files_touched]
    # Non-implementation paths Docket/agents routinely touch during a Ticket.
    for extra in ("tickets/", ".docket/", "PROJECT_AUDIT.md"):
        if extra not in allowed:
            allowed.append(extra)
    try:
        ticket_rel = normalize_repo_path(
            str(ticket_path.resolve().relative_to(repo.resolve()))
        )
        if ticket_rel not in allowed:
            allowed.append(ticket_rel)
    except ValueError:
        pass

    actual = changed_paths_since(repo, base)
    extras = [p for p in actual if not path_allowed(p, allowed)]
    messages: list[str] = []
    if extras:
        messages.append("Scope check FAILED: paths outside Files Touched:")
        for p in extras:
            messages.append(f"  - {p}")
        messages.append(f"Baseline: {base}")
        messages.append("Allowed:")
        for p in allowed:
            messages.append(f"  - {p}")
    else:
        messages.append("Scope check PASSED")
        messages.append(f"Baseline: {base}")
        messages.append(f"Changed paths: {len(actual)}")
    return ScopeResult(
        ok=not extras,
        baseline=base,
        allowed=allowed,
        actual=actual,
        extras=extras,
        messages=messages,
    )
