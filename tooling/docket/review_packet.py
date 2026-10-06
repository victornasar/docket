from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .parse import load_ticket


@dataclass
class ReviewPacket:
    lines: list[str] = field(default_factory=list)


def find_docket_root(repo: Path) -> Path | None:
    """Locate attached Docket kit (./docket) or this tooling's parent repo."""
    candidate = repo / "docket"
    if (candidate / "core" / "WORKFLOW.md").is_file():
        return candidate
    # Running from inside the Docket kit itself
    tooling = Path(__file__).resolve().parents[1]  # tooling/
    kit = tooling.parent
    if (kit / "core" / "WORKFLOW.md").is_file():
        return kit
    return None


def build_review_packet(ticket_path: Path, repo: Path) -> ReviewPacket:
    """Paths and commands a fresh-context Reviewer needs — no chat history."""
    ticket = load_ticket(ticket_path)
    docket = find_docket_root(repo)
    audit = repo / "PROJECT_AUDIT.md"
    pv = ticket.project_verify

    try:
        ticket_rel = str(ticket_path.resolve().relative_to(repo.resolve()))
    except ValueError:
        ticket_rel = str(ticket_path)

    lines = [
        "# Review packet (fresh context)",
        "# Discover everything below from the repository — do not rely on chat history.",
        "",
        f"ticket: {ticket_rel}",
        f"baseline: {ticket.baseline or '(missing — Implementer must set **Baseline:**)'}",
        f"project_audit: PROJECT_AUDIT.md ({'found' if audit.is_file() else 'MISSING'})",
        f"attestation: {pv.attestation or '(missing in Ticket Evidence)'}",
        f"verify_log: {pv.log or '(missing in Ticket Evidence)'}",
        f"git_head: {pv.git_head or '(missing)'}",
        f"tree_fingerprint: {pv.tree_fingerprint or '(missing)'}",
        "",
    ]

    if ticket.baseline:
        lines.append(f"diff_command: git diff {ticket.baseline}")
    else:
        lines.append("diff_command: git diff <Baseline from Ticket>")

    lines.append("")
    if docket:
        try:
            drel = str(docket.resolve().relative_to(repo.resolve()))
        except ValueError:
            drel = str(docket)
        lines.extend(
            [
                f"docket_root: {drel}",
                f"reviewer_role: {drel}/core/roles/reviewer.md",
                f"workflow: {drel}/core/WORKFLOW.md",
                f"self_review_recipe: {drel}/core/recipes/recipe-self-review.md",
                f"tooling: {drel}/tooling/README.md",
            ]
        )
    else:
        lines.append(
            "docket_root: (not found — expect ./docket or open the kit paths manually)"
        )

    lines.extend(
        [
            "",
            "mechanical_gates_expected:",
            "  Implementer must have passed before handoff:",
            "    docket pre-review <ticket> --audit PROJECT_AUDIT.md",
            "  (verify → check-scope → check-evidence). Spot-check if needed;",
            "  do not invent Evidence. Missing Evidence → SEND-BACK.",
            "",
            "boundary: Mechanical gates establish execution/scope/evidence integrity.",
            "They do NOT establish that each AC is adequate or that Evidence proves it.",
        ]
    )
    return ReviewPacket(lines=lines)
