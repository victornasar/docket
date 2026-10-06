---
name: verify-with-evidence
description: >-
  Close Docket Self-review with mandatory mechanical gates before Review.
  Use when approaching Self-review, finishing a Docket Ticket, or when asked
  to verify with evidence / run pre-review gates.
---

# Verify with evidence

Thin Skill: invoke Docket tooling; do not reimplement verification.

**Source of truth:** `<DOCKET_PATH>/core/recipes/recipe-self-review.md`

## When to use

Self-review / before any Reviewer handoff for a Docket Ticket.

## Mandatory before Review

These gates are **required**. Non-zero exit **blocks** Review handoff — fix
the underlying problem; do not narrate past the failure.

Correct order (`verify` before `check-evidence` — attestation must exist):

```bash
# Normal path (always runs verify first):
./bin/docket pre-review <ticket.md> --audit PROJECT_AUDIT.md

# Second pass only — after copying Project verify from a real verify run:
./bin/docket pre-review <ticket.md> --audit PROJECT_AUDIT.md --skip-verify
```

Equivalent explicit sequence:

```bash
./bin/docket verify --audit PROJECT_AUDIT.md --ticket <ticket.md>
# copy Project verify block into Ticket; finish per-AC Evidence
./bin/docket check-scope <ticket.md>
./bin/docket check-evidence <ticket.md>
```

CLI: `<DOCKET_PATH>/bin/docket` or
`PYTHONPATH=<DOCKET_PATH>/tooling python3 -m docket`.

## What to do

1. Read Ticket ACs; confirm **Baseline:** is set.
2. Confirm Project Audit **Verification** has a canonical command.
3. Fill per-AC Evidence rows (`method`, `how`, `result`, `evidence`).
4. Run `docket pre-review <ticket> --audit PROJECT_AUDIT.md`.
5. If verify printed a Project verify block, copy it into the Ticket.
6. Re-run `docket pre-review … --skip-verify` (or full pre-review) until exit 0.
7. On any non-zero: fix implementation/scope/Evidence, then re-run — never
   hand off with a verbal “tests passed.”
8. Hand off Ticket + diff + Evidence. For a fresh Reviewer chat, also run:
   `docket review-packet <ticket.md>` and paste that packet.

## What not to do

- Do not hand-type `exit: 0` or invent attestation fields.
- Do not skip gates because the code “looks right.”
- Do not treat gate pass as “ACs proven” — Reviewer judges adequacy.
- Do not invent verify commands absent from the Project Audit.
- Do not redefine Ticket / Reviewer / Done.
