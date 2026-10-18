from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from .check_evidence import check_evidence
from .check_scope import check_scope
from .lint_ticket import lint_ticket
from .verify_cmd import DIGEST_LINES, failure_digest, format_evidence_block, verify


@dataclass
class PreReviewResult:
    ok: bool
    exit_code: int
    messages: list[str] = field(default_factory=list)


def pre_review(
    ticket_path: Path,
    repo: Path,
    *,
    audit_path: Path | None,
    skip_verify: bool = False,
    baseline: str | None = None,
    digest_lines: int = DIGEST_LINES,
) -> PreReviewResult:
    """Run mechanical gates in the only valid order before Review.

    Order: lint-ticket → verify (unless skipped) → check-scope → check-evidence.

    `lint-ticket` runs first so format errors surface before the (possibly
    slow) verify command.

    `verify` must precede `check-evidence` because Evidence must match a
    real attestation. Non-zero from any step blocks Review handoff.
    Does not judge AC adequacy.
    """
    messages: list[str] = []
    ticket_path = ticket_path.resolve()

    messages.append("=== docket lint-ticket ===")
    lint = lint_ticket(ticket_path, baseline_override=baseline)
    messages.extend(lint.messages)
    if not lint.ok:
        messages.append("")
        messages.append(
            "BLOCKED: lint-ticket failed. Fix the Ticket's structure, "
            "then re-run — do not hand off to Review."
        )
        return PreReviewResult(ok=False, exit_code=1, messages=messages)
    messages.append("")

    if not skip_verify:
        if audit_path is None:
            return PreReviewResult(
                ok=False,
                exit_code=2,
                messages=[
                    "error: --audit is required unless --skip-verify "
                    "(Project Audit defines the canonical verify command)"
                ],
            )
        messages.append("=== docket verify ===")
        att = verify(repo, audit_path.resolve(), ticket_path=ticket_path)
        latest = repo / ".docket" / "verify" / "latest.json"
        data = json.loads(latest.read_text(encoding="utf-8"))
        attest_rel = str(data.get("attestation", ".docket/verify/latest.json"))
        messages.append(f"command: {att.command}")
        messages.append(f"exit: {att.exit}")
        messages.append(f"attestation: {attest_rel}")
        messages.append("")
        messages.append("Copy into Ticket Evidence → Project verify (if not already):")
        messages.append(format_evidence_block(att, attest_rel))
        if att.exit != 0:
            messages.append("")
            messages.extend(failure_digest(repo / att.log, digest_lines))
            messages.append("")
            messages.append(
                "BLOCKED: verify exited non-zero. Fix the underlying failure, "
                "re-run pre-review — do not hand off to Review."
            )
            return PreReviewResult(ok=False, exit_code=1, messages=messages)
        messages.append("")
    else:
        messages.append("=== docket verify (skipped) ===")
        messages.append("")

    messages.append("=== docket check-scope ===")
    scope = check_scope(ticket_path, repo, baseline=baseline)
    messages.extend(scope.messages)
    if not scope.ok:
        messages.append("")
        messages.append(
            "BLOCKED: check-scope failed. Fix Files Touched / revert extras, "
            "then re-run — do not hand off to Review."
        )
        return PreReviewResult(ok=False, exit_code=1, messages=messages)
    messages.append("")

    messages.append("=== docket check-evidence ===")
    evidence = check_evidence(ticket_path, repo)
    messages.extend(evidence.messages)
    if not evidence.ok:
        messages.append("")
        messages.append(
            "BLOCKED: check-evidence failed. If Project verify is stale/empty, "
            "copy the verify attestation block into the Ticket, fill every AC "
            "Evidence row, then re-run: docket pre-review <ticket> --audit … "
            "(or --skip-verify if attestation is already fresh). "
            "Do not hand off to Review."
        )
        return PreReviewResult(ok=False, exit_code=1, messages=messages)

    messages.append("")
    messages.append(
        "PRE-REVIEW GATES PASSED (mechanical). "
        "Hand off Ticket + diff + Evidence to an independent Reviewer. "
        "Gates do not prove AC adequacy — Reviewer judges that."
    )
    return PreReviewResult(ok=True, exit_code=0, messages=messages)
