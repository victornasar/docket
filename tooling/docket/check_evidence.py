from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from .gitutil import rev_parse, tree_fingerprint
from .parse import VALID_METHODS, load_ticket


@dataclass
class EvidenceResult:
    ok: bool
    messages: list[str] = field(default_factory=list)


def _normalize_result(value: str) -> str:
    v = value.strip().lower().replace(" ", "")
    if v in {"n/a", "na"}:
        return "n/a"
    return v


def check_evidence(
    ticket_path: Path,
    repo: Path,
    *,
    require_attestation: bool = True,
    require_fresh: bool = True,
    attestation_path: Path | None = None,
) -> EvidenceResult:
    """Mechanical Evidence checks only — does not judge AC adequacy."""
    ticket = load_ticket(ticket_path)
    messages: list[str] = []
    ok = True

    def fail(msg: str) -> None:
        nonlocal ok
        ok = False
        messages.append(f"FAIL: {msg}")

    if not ticket.ac_ids:
        fail("No AC-N ids found under Acceptance criteria")
    evidence_by_id = {e.id: e for e in ticket.ac_evidence}

    for ac_id in ticket.ac_ids:
        ev = evidence_by_id.get(ac_id)
        if ev is None:
            fail(f"{ac_id}: missing Evidence record")
            continue
        required = ("criterion", "method", "how", "result")
        if not ev.tests:
            required += ("evidence",)
        for field_name in required:
            val = getattr(ev, field_name).strip()
            if not val or val.startswith("<"):
                fail(f"{ac_id}: '{field_name}' is empty")
        method = ev.method.strip().lower()
        if method and method not in VALID_METHODS:
            fail(f"{ac_id}: invalid method '{ev.method}' (want {sorted(VALID_METHODS)})")
        result = _normalize_result(ev.result)
        if result == "fail":
            fail(f"{ac_id}: result is fail")
        elif result and result not in {"pass", "n/a"}:
            fail(f"{ac_id}: invalid result '{ev.result}'")

    for ev in ticket.ac_evidence:
        if ticket.ac_ids and ev.id not in ticket.ac_ids:
            messages.append(
                f"WARN: Evidence id {ev.id} not listed in Acceptance criteria"
            )

    pv = ticket.project_verify
    for field_name in ("command", "exit", "log", "ran_at"):
        val = getattr(pv, field_name).strip()
        if not val or val.startswith("<"):
            fail(f"Project verify: '{field_name}' is empty")
    if pv.exit.strip() and pv.exit.strip() != "0":
        fail(f"Project verify: exit must be 0 for Done eligibility (got {pv.exit!r})")

    if require_attestation:
        for field_name in ("git_head", "tree_fingerprint", "attestation"):
            val = getattr(pv, field_name).strip()
            if not val or val.startswith("<"):
                fail(f"Project verify: '{field_name}' is empty (required by Stage 2)")

    sr = ticket.scope_review
    if not sr.diff_vs_files_touched.strip() or sr.diff_vs_files_touched.startswith("<"):
        fail("Scope review: 'diff_vs_files_touched' is empty")
    if not sr.extras.strip():
        fail("Scope review: 'extras' is empty (use 'none' if no extras)")
    if not sr.justified.strip():
        fail("Scope review: 'justified' is empty")

    if require_attestation:
        if not pv.attestation.strip():
            fail("Project verify: attestation path required")
        else:
            att_path = attestation_path or (repo / pv.attestation.strip())
            if not att_path.is_file():
                alt = ticket_path.parent / pv.attestation.strip()
                att_path = alt if alt.is_file() else att_path
            if not att_path.is_file():
                fail(f"Attestation file not found: {pv.attestation}")
            else:
                try:
                    data = json.loads(att_path.read_text(encoding="utf-8"))
                except json.JSONDecodeError as e:
                    fail(f"Attestation JSON invalid: {e}")
                    data = None
                if data is not None:
                    _cross_check_attestation(
                        data,
                        pv,
                        repo,
                        require_fresh=require_fresh,
                        fail=fail,
                        ticket_path=ticket_path,
                    )
                    _check_tests_evidence(ticket.ac_evidence, data, repo, fail=fail)
    elif any(ev.tests for ev in ticket.ac_evidence):
        messages.append(
            "WARN: `tests:` evidence not checked against a verify log "
            "(--skip-attestation)"
        )

    if ok:
        messages.append(
            "Evidence check PASSED (structural + attestation). "
            "Adequacy of evidence vs ACs remains Reviewer judgment."
        )
    return EvidenceResult(ok=ok, messages=messages)


def _cross_check_attestation(
    data, pv, repo, *, require_fresh, fail, ticket_path: Path | None = None
) -> None:
    if data.get("schema") != "docket.verify.v1":
        fail(f"Attestation schema unsupported: {data.get('schema')!r}")
        return
    # Markdown must match authoritative attestation — agent cannot type exit.
    if str(data.get("exit")) != str(pv.exit.strip()):
        fail(
            f"Project verify exit {pv.exit!r} does not match "
            f"attestation exit {data.get('exit')!r}"
        )
    if data.get("command", "").strip() != pv.command.strip():
        fail("Project verify command does not match attestation")
    if data.get("log", "").strip() != pv.log.strip():
        fail("Project verify log does not match attestation")
    if data.get("git_head", "").strip() != pv.git_head.strip():
        fail("Project verify git_head does not match attestation")
    if data.get("tree_fingerprint", "").strip() != pv.tree_fingerprint.strip():
        fail("Project verify tree_fingerprint does not match attestation")
    if data.get("ran_at", "").strip() != pv.ran_at.strip():
        fail("Project verify ran_at does not match attestation")

    if require_fresh:
        exclude_paths: set[str] = set()
        for candidate in (data.get("ticket"), str(ticket_path) if ticket_path else None):
            if not candidate:
                continue
            try:
                tpath = Path(candidate)
                if tpath.is_absolute():
                    exclude_paths.add(
                        str(tpath.resolve().relative_to(repo.resolve()))
                    )
                else:
                    exclude_paths.add(str(tpath))
            except (ValueError, OSError):
                continue
        try:
            current_fp = tree_fingerprint(repo, exclude_paths=exclude_paths)
            current_head = rev_parse(repo, "HEAD")
        except Exception as e:  # noqa: BLE001
            fail(f"Could not compute current tree state: {e}")
            return
        if data.get("tree_fingerprint") != current_fp:
            fail(
                "Attestation is STALE: tree_fingerprint does not "
                "match current worktree (re-run `docket verify`)"
            )
        if data.get("git_head") != current_head:
            fail(
                "Attestation is STALE: git_head does not match "
                "current HEAD (re-run `docket verify`)"
            )


# Per-runner adapters: classify a log line that mentions a test title.
# Playwright list reporter: "  ✓  3 [chromium] › a.spec.ts:4:5 › suite › title (1.2s)"
#   failed "  ✘  …", skipped "  -  …". pytest -v: "path::name PASSED [ 50%]";
#   pytest -rA summary: "PASSED path::name", "FAILED path::name - msg".
_FAILED = re.compile(r"^\s*[✘✗×]\s|\b(FAILED|ERROR)\b")
_SKIPPED = re.compile(r"^\s*-\s+\d+\s|\b(SKIPPED|XFAIL)\b")
_PASSED = re.compile(r"^\s*[✓✔]\s|\bPASSED\b")


def classify_test_line(line: str) -> str | None:
    if _FAILED.search(line):
        return "failed"
    if _SKIPPED.search(line):
        return "skipped"
    if _PASSED.search(line):
        return "passed"
    return None


def title_problems(titles: list[str], log_text: str) -> list[str]:
    """One message per title that is missing, failed, or skipped in the log."""
    lines = log_text.splitlines()
    problems: list[str] = []
    for title in titles:
        states = {
            classify_test_line(line) for line in lines if title in line
        } - {None}
        if "failed" in states:
            problems.append(f"test {title!r} FAILED in verify log")
        elif "skipped" in states:
            problems.append(f"test {title!r} was SKIPPED in verify log")
        elif "passed" not in states:
            problems.append(f"test {title!r} not found as passed in verify log")
    return problems


def _check_tests_evidence(ac_evidence, data, repo: Path, *, fail) -> None:
    with_tests = [ev for ev in ac_evidence if ev.tests]
    if not with_tests:
        return
    log_rel = str(data.get("log", "")).strip()
    log_path = Path(log_rel) if Path(log_rel).is_absolute() else repo / log_rel
    if not log_rel or not log_path.is_file():
        fail(f"`tests:` evidence needs the attested verify log (not found: {log_rel!r})")
        return
    log_text = log_path.read_text(encoding="utf-8", errors="replace")
    for ev in with_tests:
        for problem in title_problems(ev.tests, log_text):
            fail(f"{ev.id}: {problem}")
