from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from .gitutil import GitError, changed_paths_since, rev_parse, run_git, tree_fingerprint
from .parse import _meta_field, load_ticket

MAX_LINES = 39
OPEN_STATUSES = ("send-back", "in-progress", "in-review", "approved")


@dataclass
class ResumeResult:
    ok: bool
    lines: list[str] = field(default_factory=list)


def find_open_ticket(repo: Path) -> Path | None:
    """Most recently modified Ticket under tickets/ in an open status."""
    folder = repo / "tickets"
    if not folder.is_dir():
        return None
    open_tickets = [
        p
        for p in folder.glob("*.md")
        if _meta_field(p.read_text(encoding="utf-8"), "Status").lower() in OPEN_STATUSES
    ]
    if not open_tickets:
        return None
    return max(open_tickets, key=lambda p: p.stat().st_mtime)


def _attestation_line(ticket, ticket_rel: str, repo: Path) -> str:
    att_rel = ticket.project_verify.attestation.strip()
    att_path = repo / (att_rel or ".docket/verify/latest.json")
    if not att_path.is_file():
        return "attestation: none (run `docket verify`)"
    try:
        data = json.loads(att_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return f"attestation: {att_rel or '.docket/verify/latest.json'} (unreadable)"
    if data.get("ticket") and data["ticket"] != ticket_rel:
        return f"attestation: latest is for {data['ticket']}, none for this Ticket"
    try:
        fresh = (
            data.get("git_head") == rev_parse(repo, "HEAD")
            and data.get("tree_fingerprint")
            == tree_fingerprint(repo, exclude_paths={ticket_rel})
        )
    except GitError:
        fresh = False
    state = "fresh" if fresh else "STALE (re-run `docket verify`)"
    return f"attestation: exit {data.get('exit')} at {data.get('ran_at')}, {state}"


def resume(repo: Path, ticket_path: Path | None = None) -> ResumeResult:
    """Compact brief for a fresh session — read this, not the old transcript."""
    if ticket_path is None:
        ticket_path = find_open_ticket(repo)
        if ticket_path is None:
            return ResumeResult(ok=False, lines=["error: no open Ticket under tickets/"])
    ticket = load_ticket(ticket_path)
    try:
        ticket_rel = str(ticket_path.resolve().relative_to(repo.resolve()))
    except ValueError:
        ticket_rel = str(ticket_path)

    head = [
        f"# Resume: {ticket.title.removeprefix('Ticket: ')}",
        f"ticket: {ticket_rel}",
        f"status: {ticket.status or '(missing)'}",
        f"baseline: {ticket.baseline or '(not set)'}",
        "acceptance criteria:",
    ]
    results = {e.id: e.result.strip().lower() for e in ticket.ac_evidence}
    for ac_id in ticket.ac_ids:
        state = results.get(ac_id, "")
        head.append(f"  {ac_id}: {state if state and not state.startswith('<') else 'blank'}")
    head.append(_attestation_line(ticket, ticket_rel, repo))

    changed: list[str] = []
    if ticket.baseline:
        try:
            untracked = set(
                run_git(repo, "ls-files", "--others", "--exclude-standard").splitlines()
            )
            changed = [
                f"{p} (untracked)" if p in untracked else p
                for p in changed_paths_since(repo, ticket.baseline)
                if not p.startswith(".docket/")
            ]
        except GitError as e:
            changed = [f"(cannot diff vs Baseline: {e})"]
        head.append(f"changed since baseline: {len(changed)}" if changed else "changed since baseline: none")
    else:
        head.append("changed since baseline: (no Baseline)")

    room = MAX_LINES - len(head) - 1
    if len(changed) > room:
        shown = changed[: max(room - 1, 0)]
        shown.append(f"… +{len(changed) - len(shown)} more (git diff --stat {ticket.baseline})")
        changed = shown
    lines = head + [f"  {p}" for p in changed]
    lines.append("Next: read the Ticket, then continue from the first blank AC.")
    return ResumeResult(ok=True, lines=lines[:MAX_LINES])
