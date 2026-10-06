from __future__ import annotations

import json
import os
import shlex
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from .gitutil import rev_parse, tree_fingerprint
from .parse import ParseError, parse_canonical_verify_command


@dataclass
class Attestation:
    schema: str
    command: str
    exit: int
    log: str
    ran_at: str
    git_head: str
    tree_fingerprint: str
    repo: str
    ticket: str | None


def verify(
    repo: Path,
    audit_path: Path,
    ticket_path: Path | None = None,
    out_dir: Path | None = None,
) -> Attestation:
    """Run Project Audit canonical command; write log + attestation JSON.

    The Project Audit command is treated as trusted project configuration.
    It is executed with cwd=repo root via argv from shlex.split when possible,
    falling back to shell only if the command string requires it.
    """
    audit_text = audit_path.read_text(encoding="utf-8")
    command = parse_canonical_verify_command(audit_text)

    out = out_dir or (repo / ".docket" / "verify")
    out.mkdir(parents=True, exist_ok=True)

    ran_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    head = rev_parse(repo, "HEAD")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    slug = ticket_path.stem if ticket_path else "no-ticket"
    log_path = out / f"{slug}-{stamp}.log"
    attest_path = out / f"{slug}-{stamp}.json"
    latest_path = out / "latest.json"

    env = os.environ.copy()
    # Predictable locale for logs
    env.setdefault("LC_ALL", "C")

    use_shell = _needs_shell(command)
    argv: list[str] | str = command if use_shell else shlex.split(command)
    started = datetime.now(timezone.utc).isoformat()
    try:
        proc = subprocess.run(
            argv,
            cwd=str(repo),
            capture_output=True,
            text=True,
            env=env,
            shell=use_shell,
        )
        exit_code = proc.returncode
        stdout = proc.stdout or ""
        stderr = proc.stderr or ""
    except OSError as e:
        exit_code = 127
        stdout = ""
        stderr = f"failed to execute command: {e}\n"

    ended = datetime.now(timezone.utc).isoformat()
    exclude_paths: set[str] = set()
    if ticket_path is not None:
        try:
            exclude_paths.add(
                str(ticket_path.resolve().relative_to(repo.resolve()))
            )
        except ValueError:
            pass
    fp = tree_fingerprint(repo, exclude_paths=exclude_paths)

    log_body = "\n".join(
        [
            f"command: {command}",
            f"argv: {argv!r}",
            f"cwd: {repo}",
            f"started: {started}",
            f"ended: {ended}",
            f"ran_at: {ran_at}",
            f"exit: {exit_code}",
            f"git_head: {head}",
            f"tree_fingerprint: {fp}",
            "",
            "----- stdout -----",
            stdout,
            "----- stderr -----",
            stderr,
        ]
    )
    log_path.write_text(log_body, encoding="utf-8")

    # Relative log path when under repo
    try:
        log_rel = str(log_path.resolve().relative_to(repo.resolve()))
    except ValueError:
        log_rel = str(log_path)

    try:
        attest_rel = str(attest_path.resolve().relative_to(repo.resolve()))
    except ValueError:
        attest_rel = str(attest_path)

    ticket_rel: str | None = None
    if ticket_path is not None:
        try:
            ticket_rel = str(ticket_path.resolve().relative_to(repo.resolve()))
        except ValueError:
            ticket_rel = str(ticket_path)

    att = Attestation(
        schema="docket.verify.v1",
        command=command,
        exit=exit_code,
        log=log_rel,
        ran_at=ran_at,
        git_head=head,
        tree_fingerprint=fp,
        repo=str(repo.resolve()),
        ticket=ticket_rel,
    )
    payload = asdict(att)
    payload["attestation"] = attest_rel
    attest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    latest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return Attestation(
        schema=att.schema,
        command=att.command,
        exit=att.exit,
        log=log_rel,
        ran_at=att.ran_at,
        git_head=att.git_head,
        tree_fingerprint=att.tree_fingerprint,
        repo=att.repo,
        ticket=att.ticket,
    )


def format_evidence_block(att: Attestation, attestation_path: str) -> str:
    return "\n".join(
        [
            "### Project verify",
            "",
            "```text",
            f"command: {att.command}",
            f"exit: {att.exit}",
            f"log: {att.log}",
            f"ran_at: {att.ran_at}",
            f"git_head: {att.git_head}",
            f"tree_fingerprint: {att.tree_fingerprint}",
            f"attestation: {attestation_path}",
            "```",
        ]
    )


def _needs_shell(command: str) -> bool:
    # Shell features that shlex.split alone cannot express safely as argv.
    shell_tokens = [">", "<", "|", "&&", "||", ";", "*", "?", "$(", "`", "\n"]
    return any(tok in command for tok in shell_tokens)
