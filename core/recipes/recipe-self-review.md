# Recipe: Self-Review (evidence handoff)

Owner: Implementer. Run this before handing work to the Reviewer — it's the
Self-review stage in [`WORKFLOW.md`](../WORKFLOW.md). Portable source of
truth for the Evidence contract and **Stage 3 pre-Review gates**.

**Rule:** never claim an acceptance criterion is satisfied without recording
how it was verified and what evidence supports the claim. An agent's claim
is not evidence.

Mechanical facts come from `bin/docket` / `tooling/` — do not hand-type
`exit: 0`.

## Intended loop

```
Implement
  → self-review (fill AC Evidence)
  → docket verify          (authoritative run + attestation)
  → copy Project verify into Ticket
  → docket check-scope
  → docket check-evidence
  → Review (independent)
```

Preferred single command for the gate block:

```bash
docket pre-review <ticket.md> --audit PROJECT_AUDIT.md
# Copy Project verify from that run into the Ticket, then re-check
# scope + evidence without re-executing the Audit command:
docket pre-review <ticket.md> --audit PROJECT_AUDIT.md --skip-verify
```

`--skip-verify` is only for the second pass after a real `verify`
attestation exists — it is not a substitute for running verify. Prefer a
full `pre-review` (no skip) whenever the implementation changed.

`verify` is the authoritative execution record. Attestation binds to
`git_head` + `tree_fingerprint` (Ticket / `.docket/` excluded). Any later
**implementation** change invalidates attestation — re-verify. Reviewer
judgment is still required for AC adequacy; green gates ≠ proven criterion.

**Non-zero from any gate blocks Review handoff.** Fix the cause; do not
report around it.

## Steps

1. **Re-read the Ticket.** Confirm **Baseline:** is set (Ticket start SHA).

2. **Load Project Audit Verification.** Do not invent commands.

3. **Fill per-AC Evidence** (`method`, `how`, `result`, `evidence`). Manual
   is allowed when judgment is genuine — not a substitute for automation.

4. **Run `docket pre-review <ticket> --audit PROJECT_AUDIT.md`** (or
   `verify` alone). Copy the Project verify block into the Ticket
   (`command`, `exit`, `log`, `ran_at`, `git_head`, `tree_fingerprint`,
   `attestation`). Markdown must match the attestation file.

5. **Run check-scope / check-evidence** (via `pre-review --skip-verify` or
   individually). Both must exit 0. Fill Scope review fields to match
   check-scope.

6. **Scan leftovers / secrets** ([`RULES.md`](../RULES.md) §5). Update
   rollback if needed.

7. **Handoff.** Ticket + diff + Evidence. For a fresh-context Reviewer,
   run `docket review-packet <ticket>` and give them that output plus the
   Ticket path — they must not need chat history.

## Evidence schema (Project verify)

```text
command: <from docket verify>
exit: <from attestation>
log: <from attestation>
ran_at: <from attestation>
git_head: <from attestation>
tree_fingerprint: <from attestation>
attestation: <.docket/verify/….json>
```

## Self-review checklist

- [ ] Baseline set; Ticket re-read.
- [ ] Per-AC Evidence filled.
- [ ] `docket pre-review` (verify → check-scope → check-evidence) exit 0.
- [ ] Project verify copied from attestation (not invented).
- [ ] No debug artifacts / secrets; rollback accurate.
- [ ] Review packet available for fresh-context Reviewer.
- [ ] Ready for independent Review — gates do **not** prove AC adequacy.
