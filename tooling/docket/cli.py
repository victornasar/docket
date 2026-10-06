from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .check_evidence import check_evidence
from .check_scope import check_scope
from .gitutil import GitError, is_git_repo
from .parse import ParseError
from .pre_review import pre_review
from .review_packet import build_review_packet
from .verify_cmd import format_evidence_block, verify


def _add_repo_arg(p: argparse.ArgumentParser) -> None:
    p.add_argument(
        "--repo",
        type=Path,
        default=Path.cwd(),
        help="Git repository root (default: cwd)",
    )


def _resolve_audit(repo: Path, audit: Path) -> Path:
    if not audit.is_absolute():
        return (repo / audit).resolve()
    return audit.resolve()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="docket",
        description="Docket deterministic trust gates (Stage 2/3)",
    )
    parser.add_argument("--version", action="version", version=f"docket {__version__}")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_scope = sub.add_parser("check-scope", help="Fail if diff paths ⊄ Files Touched")
    _add_repo_arg(p_scope)
    p_scope.add_argument("ticket", type=Path)
    p_scope.add_argument(
        "--baseline",
        default=None,
        help="Git ref/sha at Ticket start (or set **Baseline:** on Ticket)",
    )

    p_ev = sub.add_parser(
        "check-evidence",
        help="Mechanical Evidence + attestation checks (not AC adequacy)",
    )
    _add_repo_arg(p_ev)
    p_ev.add_argument("ticket", type=Path)
    p_ev.add_argument(
        "--attestation",
        type=Path,
        default=None,
        help="Override attestation JSON path",
    )
    p_ev.add_argument(
        "--allow-stale",
        action="store_true",
        help="Do not fail when attestation fingerprint ≠ current worktree",
    )
    p_ev.add_argument(
        "--skip-attestation",
        action="store_true",
        help="Structural Evidence only (not for Done)",
    )

    p_ver = sub.add_parser(
        "verify",
        help="Run Project Audit canonical verify; write log + attestation",
    )
    _add_repo_arg(p_ver)
    p_ver.add_argument(
        "--audit",
        type=Path,
        required=True,
        help="Path to PROJECT_AUDIT.md",
    )
    p_ver.add_argument(
        "--ticket",
        type=Path,
        default=None,
        help="Optional Ticket path (for log naming / evidence hint)",
    )
    p_ver.add_argument(
        "--json",
        action="store_true",
        help="Print attestation JSON only",
    )

    p_pre = sub.add_parser(
        "pre-review",
        help="Mandatory gate sequence before Review: verify → check-scope → check-evidence",
    )
    _add_repo_arg(p_pre)
    p_pre.add_argument("ticket", type=Path)
    p_pre.add_argument(
        "--audit",
        type=Path,
        default=None,
        help="PROJECT_AUDIT.md (required unless --skip-verify)",
    )
    p_pre.add_argument(
        "--skip-verify",
        action="store_true",
        help="Skip verify (use after copying fresh attestation into the Ticket)",
    )
    p_pre.add_argument(
        "--baseline",
        default=None,
        help="Override Ticket Baseline for check-scope",
    )

    p_pkt = sub.add_parser(
        "review-packet",
        help="Print paths/commands for a fresh-context Reviewer (no chat history)",
    )
    _add_repo_arg(p_pkt)
    p_pkt.add_argument("ticket", type=Path)

    args = parser.parse_args(argv)
    repo = args.repo.resolve()

    if not is_git_repo(repo):
        print(f"error: not a git repository: {repo}", file=sys.stderr)
        return 2

    try:
        if args.cmd == "check-scope":
            result = check_scope(args.ticket.resolve(), repo, baseline=args.baseline)
            for line in result.messages:
                print(line)
            return 0 if result.ok else 1

        if args.cmd == "check-evidence":
            result = check_evidence(
                args.ticket.resolve(),
                repo,
                require_attestation=not args.skip_attestation,
                require_fresh=not args.allow_stale,
                attestation_path=args.attestation.resolve() if args.attestation else None,
            )
            for line in result.messages:
                print(line)
            return 0 if result.ok else 1

        if args.cmd == "verify":
            audit = _resolve_audit(repo, args.audit)
            ticket = args.ticket.resolve() if args.ticket else None
            att = verify(repo, audit, ticket_path=ticket)
            latest = repo / ".docket" / "verify" / "latest.json"
            data = json.loads(latest.read_text(encoding="utf-8"))
            if args.json:
                print(json.dumps(data, indent=2))
            else:
                print(f"command: {att.command}")
                print(f"exit: {att.exit}")
                print(f"log: {att.log}")
                print(f"ran_at: {att.ran_at}")
                print(f"git_head: {att.git_head}")
                print(f"tree_fingerprint: {att.tree_fingerprint}")
                print(f"attestation: {data.get('attestation')}")
                print()
                print("Copy into Ticket Evidence → Project verify:")
                print(
                    format_evidence_block(
                        att, str(data.get("attestation", ".docket/verify/latest.json"))
                    )
                )
            return 0 if att.exit == 0 else 1

        if args.cmd == "pre-review":
            audit = _resolve_audit(repo, args.audit) if args.audit else None
            result = pre_review(
                args.ticket.resolve(),
                repo,
                audit_path=audit,
                skip_verify=args.skip_verify,
                baseline=args.baseline,
            )
            for line in result.messages:
                print(line)
            return result.exit_code

        if args.cmd == "review-packet":
            packet = build_review_packet(args.ticket.resolve(), repo)
            for line in packet.lines:
                print(line)
            return 0

    except (ParseError, GitError, FileNotFoundError, OSError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
