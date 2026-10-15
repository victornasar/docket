from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from .parse import VALID_METHODS, _meta_field, _parse_ac_evidence, _section_body

REQUIRED_SECTIONS = (
    "Problem",
    "Approach",
    "Files touched",
    "Acceptance criteria",
    "Rollback plan",
    "Rules check",
    "Evidence",
)

_SHA = re.compile(r"^[0-9a-f]{7,40}$")
_GLOB = re.compile(r"[*?]")  # not [ ]: Next.js routes use app/[slug]/


@dataclass
class LintResult:
    ok: bool
    messages: list[str] = field(default_factory=list)


def lint_ticket(ticket_path: Path, *, baseline_override: str | None = None) -> LintResult:
    """Structural Ticket checks that need no diff and no verify run."""
    raw = ticket_path.read_text(encoding="utf-8")
    problems: list[str] = []

    if not re.search(r"^# ", raw, flags=re.MULTILINE):
        problems.append("missing '# Ticket: <title>' heading")
    if not re.search(r"^\*\*Status:\*\*", raw, flags=re.MULTILINE):
        problems.append("missing **Status:** line")
    for heading in REQUIRED_SECTIONS:
        if not re.search(rf"^## {re.escape(heading)}\s*$", raw, flags=re.MULTILINE):
            problems.append(f"missing '## {heading}' section")

    for line in _section_body(raw, "Files touched").splitlines():
        item = line.strip()
        if not item.startswith("-"):
            continue
        item = item.lstrip("-").strip().strip("`")
        if not item or item.startswith("<"):
            continue
        if "," in item:
            problems.append(f"Files touched: one path per line, no commas: {item!r}")
        elif _GLOB.search(item):
            problems.append(f"Files touched: globs are not allowed: {item!r}")

    if baseline_override is None:
        baseline = _meta_field(raw, "Baseline")
        if not baseline:
            problems.append("**Baseline:** is missing or still the template placeholder")
        elif not (_SHA.match(baseline) or baseline.startswith("(set when")):
            problems.append(
                f"**Baseline:** must be a commit hash or '(set when …)': {baseline!r}"
            )

    evidence = _section_body(raw, "Evidence")
    for ev in _parse_ac_evidence(evidence) if evidence else []:
        method = ev.method.strip().lower()
        if method and not method.startswith("<") and method not in VALID_METHODS:
            problems.append(
                f"{ev.id}: invalid method {ev.method!r} "
                f"(one of {', '.join(sorted(VALID_METHODS))})"
            )

    messages = [f"FAIL: {p}" for p in problems]
    if not problems:
        messages.append("lint-ticket PASSED (structure only)")
    return LintResult(ok=not problems, messages=messages)
