from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


class ParseError(ValueError):
    pass


@dataclass
class AcEvidence:
    id: str
    criterion: str = ""
    method: str = ""
    how: str = ""
    result: str = ""
    evidence: str = ""
    notes: str = ""


@dataclass
class ProjectVerify:
    command: str = ""
    exit: str = ""
    log: str = ""
    ran_at: str = ""
    git_head: str = ""
    tree_fingerprint: str = ""
    attestation: str = ""


@dataclass
class ScopeReview:
    diff_vs_files_touched: str = ""
    extras: str = ""
    justified: str = ""
    notes: str = ""


@dataclass
class Ticket:
    path: Path
    raw: str
    title: str = ""
    baseline: str = ""
    files_touched: list[str] = field(default_factory=list)
    ac_ids: list[str] = field(default_factory=list)
    project_verify: ProjectVerify = field(default_factory=ProjectVerify)
    ac_evidence: list[AcEvidence] = field(default_factory=list)
    scope_review: ScopeReview = field(default_factory=ScopeReview)


_KV = re.compile(r"^([A-Za-z0-9_]+):\s*(.*)$")


def load_ticket(path: Path) -> Ticket:
    raw = path.read_text(encoding="utf-8")
    ticket = Ticket(path=path, raw=raw)
    ticket.title = _first_heading(raw)
    ticket.baseline = _meta_field(raw, "Baseline")
    ticket.files_touched = _parse_files_touched(raw)
    ticket.ac_ids = _parse_ac_ids(raw)
    evidence_src = _section_body(raw, "Evidence")
    if evidence_src:
        ticket.project_verify = _parse_project_verify(evidence_src)
        ticket.ac_evidence = _parse_ac_evidence(evidence_src)
        ticket.scope_review = _parse_scope_review(evidence_src)
    return ticket


def _first_heading(raw: str) -> str:
    for line in raw.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return ""


def _meta_field(raw: str, name: str) -> str:
    pat = re.compile(rf"^\*\*{re.escape(name)}:\*\*\s*(.+)$", re.MULTILINE)
    m = pat.search(raw)
    if not m:
        # also allow **Baseline:** <value> on same patterns without bold close weirdness
        pat2 = re.compile(rf"^\*\*{re.escape(name)}:\*\*\s*(.*)$", re.MULTILINE)
        m = pat2.search(raw)
    if not m:
        return ""
    val = m.group(1).strip()
    if val.startswith("<") and val.endswith(">"):
        return ""
    return val


def _section_body(raw: str, heading: str) -> str:
    # Match ## Heading at line start
    pat = re.compile(
        rf"^## {re.escape(heading)}\s*\n(.*?)(?=^## |\Z)",
        re.MULTILINE | re.DOTALL,
    )
    m = pat.search(raw)
    return m.group(1) if m else ""


def _fenced_text_blocks(section: str) -> list[str]:
    return re.findall(r"```text\n(.*?)```", section, flags=re.DOTALL)


def _parse_files_touched(raw: str) -> list[str]:
    body = _section_body(raw, "Files touched")
    if not body:
        raise ParseError("Ticket missing '## Files touched' section")
    paths: list[str] = []
    for line in body.splitlines():
        line = line.strip()
        if not line.startswith("-"):
            continue
        item = line.lstrip("-").strip()
        if not item or item.startswith("<"):
            continue
        # strip trailing notes like "(new)"
        item = re.sub(r"\s*\(.*?\)\s*$", "", item).strip()
        item = item.strip("`")
        # take first path token if commentary after
        if " " in item and not item.endswith("/"):
            # keep paths with spaces; only split on ' — ' or ' - ' commentary
            for sep in (" — ", " - ", " #"):
                if sep in item:
                    item = item.split(sep, 1)[0].strip()
                    break
        if item:
            paths.append(item.replace("\\", "/"))
    if not paths:
        raise ParseError("Files touched list is empty")
    return paths


def _parse_ac_ids(raw: str) -> list[str]:
    body = _section_body(raw, "Acceptance criteria")
    ids: list[str] = []
    for line in body.splitlines():
        m = re.match(r"^- \[[ xX]\]\s*(AC-\d+)\b", line.strip())
        if m:
            ids.append(m.group(1))
            continue
        m = re.match(r"^- \[[ xX]\]\s*.*\b(AC-\d+)\b", line.strip())
        if m:
            ids.append(m.group(1))
    # also allow bare AC-N: at start of checklist without brackets content before
    if not ids:
        for line in body.splitlines():
            m = re.search(r"\b(AC-\d+)\b", line)
            if m and line.strip().startswith("-"):
                ids.append(m.group(1))
    # unique preserve order
    seen: set[str] = set()
    out: list[str] = []
    for i in ids:
        if i not in seen:
            seen.add(i)
            out.append(i)
    return out


def _parse_kv_block(text: str) -> dict[str, str]:
    data: dict[str, str] = {}
    for line in text.splitlines():
        m = _KV.match(line.strip())
        if m:
            data[m.group(1)] = m.group(2).strip()
    return data


def _parse_project_verify(evidence_src: str) -> ProjectVerify:
    # Prefer block under ### Project verify
    m = re.search(
        r"### Project verify\s*\n(.*?)(?=^### |\Z)",
        evidence_src,
        flags=re.MULTILINE | re.DOTALL,
    )
    region = m.group(1) if m else evidence_src
    blocks = _fenced_text_blocks(region)
    if not blocks:
        # allow unfenced kv in region
        kv = _parse_kv_block(region)
    else:
        kv = _parse_kv_block(blocks[0])
    return ProjectVerify(
        command=kv.get("command", ""),
        exit=kv.get("exit", ""),
        log=kv.get("log", ""),
        ran_at=kv.get("ran_at", ""),
        git_head=kv.get("git_head", ""),
        tree_fingerprint=kv.get("tree_fingerprint", ""),
        attestation=kv.get("attestation", ""),
    )


def _parse_ac_evidence(evidence_src: str) -> list[AcEvidence]:
    m = re.search(
        r"### Acceptance criteria\s*\n(.*?)(?=^### |\Z)",
        evidence_src,
        flags=re.MULTILINE | re.DOTALL,
    )
    region = m.group(1) if m else ""
    if not region:
        return []
    blocks = _fenced_text_blocks(region)
    text = blocks[0] if blocks else region
    # split on id: AC-
    chunks = re.split(r"(?m)^(?=id:\s*AC-\d+)", text)
    out: list[AcEvidence] = []
    for chunk in chunks:
        chunk = chunk.strip()
        if not chunk:
            continue
        kv = _parse_kv_block(chunk)
        if "id" not in kv:
            continue
        out.append(
            AcEvidence(
                id=kv.get("id", "").strip(),
                criterion=kv.get("criterion", ""),
                method=kv.get("method", ""),
                how=kv.get("how", ""),
                result=kv.get("result", ""),
                evidence=kv.get("evidence", ""),
                notes=kv.get("notes", ""),
            )
        )
    return out


def _parse_scope_review(evidence_src: str) -> ScopeReview:
    m = re.search(
        r"### Scope review\s*\n(.*?)(?=^### |\Z)",
        evidence_src,
        flags=re.MULTILINE | re.DOTALL,
    )
    region = m.group(1) if m else ""
    if not region:
        return ScopeReview()
    blocks = _fenced_text_blocks(region)
    kv = _parse_kv_block(blocks[0] if blocks else region)
    return ScopeReview(
        diff_vs_files_touched=kv.get("diff_vs_files_touched", ""),
        extras=kv.get("extras", ""),
        justified=kv.get("justified", ""),
        notes=kv.get("notes", ""),
    )


def parse_canonical_verify_command(audit_text: str) -> str:
    """Extract preferred canonical verification command from Project Audit."""
    # Prefer ### Canonical (preferred if present)
    sections = [
        ("Canonical (preferred if present)", True),
        ("Canonical", True),
        ("Test", False),
    ]
    body = _section_body(audit_text, "Verification")
    if not body:
        raise ParseError("Project Audit missing '## Verification' section")

    for heading, preferred in sections:
        m = re.search(
            rf"### {re.escape(heading)}\s*\n(.*?)(?=^### |\Z)",
            body,
            flags=re.MULTILINE | re.DOTALL,
        )
        if not m:
            continue
        region = m.group(1)
        blocks = _fenced_text_blocks(region)
        kv = _parse_kv_block(blocks[0] if blocks else region)
        cmd = kv.get("command", "").strip()
        if not cmd:
            continue
        if cmd.upper() == "N/A" or cmd.startswith("<"):
            if preferred:
                continue
            continue
        return cmd

    # fallback: any command: under Verification that isn't N/A
    for block in _fenced_text_blocks(body):
        kv = _parse_kv_block(block)
        cmd = kv.get("command", "").strip()
        if cmd and cmd.upper() != "N/A" and not cmd.startswith("<"):
            return cmd

    raise ParseError(
        "Project Audit Verification defines no runnable canonical command "
        "(all missing or N/A). Add a Canonical or Test command."
    )


def path_allowed(path: str, allowed: list[str]) -> bool:
    from .gitutil import normalize_repo_path

    norm = normalize_repo_path(path)
    for a in allowed:
        a_norm = normalize_repo_path(a)
        if a_norm.endswith("/"):
            if norm == a_norm.rstrip("/") or norm.startswith(a_norm):
                return True
        elif norm == a_norm:
            return True
        # allow directory listed without trailing slash
        elif norm.startswith(a_norm.rstrip("/") + "/"):
            return True
    return False
