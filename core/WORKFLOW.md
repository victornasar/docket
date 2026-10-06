# The Workflow

This is the workflow every piece of work moves through, and the set of
handoff points between roles. Nothing moves to the next stage without the
current stage's exit criteria being met. This document defines those
criteria concretely.

```
  TICKET  --->  IMPLEMENT  --->  SELF-REVIEW  --->  REVIEW  --->  DONE
 (Planner)    (Implementer)     (Implementer)     (Reviewer)
```

Trust model in one line: **specify → execute → prove → independently
review evidence → trust.** An agent's claim is not evidence. Evidence is
what allows the system to trust the claim.

**Stage 1** required Evidence by workflow. **Stage 2** added mechanical
tooling. **Stage 3** makes those gates the default Self-review → Review
handoff (`docket pre-review`):

- `docket verify` — runs the Project Audit canonical command; writes log +
  attestation (real exit, `git_head`, `tree_fingerprint`)
- `docket check-scope` — fails if paths changed since Ticket **Baseline**
  are outside Files Touched
- `docket check-evidence` — fails if Evidence is structurally incomplete,
  does not match attestation, or attestation is stale
- `docket pre-review` — runs the three in that order; non-zero **blocks**
  Review handoff
- `docket review-packet` — paths/commands for a fresh-context Reviewer

`check-evidence` / `pre-review` do **not** judge whether evidence proves
an AC — that remains Reviewer judgment. Exit 0 ≠ AC adequacy.

This describes one Ticket at a time — the standard workflow, and almost
always the right choice. An experimental description of running several
Tickets concurrently lives in
[`advanced/PARALLEL_LINE.md`](../advanced/PARALLEL_LINE.md); it has not
been exercised on a single-operator project and is not part of the
standard flow.

## Stage 1 — Ticket

**Owner:** Planner.
**What happens:** The Planner turns a raw request into a Ticket using
[`ticket.template.md`](templates/ticket.template.md): Problem, Approach,
Files Touched, Acceptance Criteria (a checklist, not prose), Rollback Plan.
The Evidence section stays blank until Self-review. If the project hasn't
had a Project Audit run yet, or the request touches an area the Project
Audit didn't cover, that gets done or updated first — including the
Audit's Verification commands.

**Exit criteria (must all be true before moving to Implement):**
- The Ticket has concrete, checkable acceptance criteria — not "works
  correctly" but specific, observable statements (see
  [`recipe-ticket-writing.md`](recipes/recipe-ticket-writing.md)).
- Files Touched is a real list, not "TBD."
- A rollback plan is stated (see [`RULES.md`](RULES.md) §6).
- Nothing in the Ticket requires an action the Rules mark BLOCK.
  If it does, the Ticket is rewritten to avoid it, or the request is
  escalated to the human before a Ticket is even written.
- The human has approved the Ticket. **No code is written before this.**

## Stage 2 — Implement

**Owner:** Implementer.
**What happens:** Starting a Ticket = execute the approved Ticket. The
Implementer implements exactly what the Ticket describes, touching only
the files it lists, within the tool/permission boundaries in
[`implementer.md`](roles/implementer.md).

While implementing, the intended loop is:

```
Implement → Verify → Inspect failures → Fix → Re-verify → (repeat)
```

Do not treat a green run from before the final fix as sufficient proof.
Final evidence is recorded in Self-review against the final state.

**Exit criteria (must all be true before moving to Self-review):**
- Every item in the Ticket's approach has been implemented.
- No files were touched outside the Ticket's Files Touched list. If that
  turned out to be necessary, this is scope creep — see §7 in
  [`RULES.md`](RULES.md) — and gets flagged rather than silently done.
- Any action the Rules mark CONFIRM encountered mid-implementation
  was actually confirmed before it happened, not after.

## Stage 3 — Self-review

**Owner:** Implementer (before handing off).
**What happens:** The Implementer proves the work against the Ticket and
records that proof in the Ticket's Evidence section before anyone else
looks at it — so Review confirms evidence, not discovers missing proof.
Follow [`recipe-self-review.md`](recipes/recipe-self-review.md).

**Never claim an acceptance criterion is satisfied without recording how
it was verified and what evidence supports the claim.**

**Exit criteria (must all be true before moving to Review):**
- Every acceptance criterion has an Evidence record (`method`, `how`,
  `result`, `evidence`) for the **final** implementation state.
- Project verify comes from **`docket verify`** (attestation fields copied
  into the Ticket) — not a hand-typed `exit: 0`.
- **`docket pre-review <ticket> --audit PROJECT_AUDIT.md`** passes (or the
  equivalent verify → check-scope → check-evidence sequence). Non-zero
  blocks Review. Adequacy vs ACs is still for the Reviewer.
- Scope review fields in Evidence are filled to match the check-scope
  result.
- No debug output, commented-out code, or scratch artifacts left in the
  diff.
- The rollback plan from the Ticket is still accurate for what was
  actually built (if the implementation diverged from the plan, the
  rollback plan is updated to match).

## Stage 4 — Review

**Owner:** Reviewer.
**What happens:** The Reviewer — with **read-only** access, it cannot edit
anything — independently audits the Ticket's Evidence and the diff against
the acceptance criteria. This is not a rubber stamp of the Implementer's
self-review, and it is not a second implementation pass. See
[`reviewer.md`](roles/reviewer.md) for the full checklist.

**The Reviewer audits evidence; it does not invent evidence.** Missing or
inadequate evidence is a **Send-back**, not an invitation to reconstruct
the Implementer's verification and silently convert a gap into a Pass.
The Reviewer may independently re-run a critical verification as a
**spot-check**, but that does **not** replace the Implementer's required
Evidence handoff (including a fresh `docket verify` attestation). If
required Evidence is missing → **Send-back**.

**The Reviewer is invoked as a genuinely separate context, not a role
switch.** When the tool in use supports spawning an independent agent
(e.g. Claude Code's Agent/Task tool with a dedicated `reviewer`
definition), Review means actually spawning it — handing it only the
Ticket (including Evidence) and the diff, not the Implement/Self-review
conversation that produced them. A reviewer who remembers writing the code
will defend its own reasoning instead of checking it; a reviewer with no
memory of writing it can't. When the tool has no such mechanism, the
adapter for that tool states its best available approximation explicitly
rather than silently treating a same-context role-switch as equivalent —
see each adapter's own notes on this (Claude Code's is closest to the real
thing; Cursor's is a weaker approximation, documented as such).

**Possible outcomes:**

1. **Pass** — every acceptance criterion is met with adequate evidence,
   project verify recorded as passing where required, scope accounted for,
   no Rules violations. Moves to Done.
2. **Send-back** — one or more acceptance criteria aren't met, evidence is
   missing/inadequate/stale relative to the final diff, scope creep is
   found, or tests/verification are missing/failing. The Reviewer writes
   specific, itemized feedback (which criterion, why it's not met — not
   "doesn't look right") and returns the work to the Implementer. This
   goes back to Stage 2 (Implement) with that feedback attached.
3. **Escalate** — a Rules violation was found (see [`RULES.md`](RULES.md)
   §7), the Ticket itself turns out to be wrong or ambiguous in a way no
   amount of re-implementation fixes, or the retry limit below has been
   hit. Goes to the human, not back to the Implementer.

### Loopback policy (send-back retry limit)

- A send-back counts as one loop. **After 2 send-backs on the same Ticket
  (3 total attempts), the Reviewer escalates to the human instead of
  sending back a 3rd time**, even if the remaining issues look minor.
- The reasoning: two failed attempts at the same Ticket usually means the
  Ticket itself is underspecified or the approach is wrong, not that the
  Implementer needs one more try. That's a planning problem, which routes
  back to the Planner via the human, not another implementation cycle.
- Each send-back's feedback is cumulative context for the next attempt —
  the Implementer sees what previous rounds got flagged for, so the same
  issue doesn't get reintroduced.
- **Re-verification on attempt 2+ scopes to what changed, not everything
  again.** Attempt 1's Review already established the full picture. If
  attempt 2 only touched what the send-back named, re-confirm the fix,
  re-run whatever a full check would need to re-run to trust the result
  (a build, the specific test), **update Evidence for those re-runs**, and
  reconcile the Ticket's own bookkeeping (Files Touched, acceptance
  criteria) against the now-current diff — but don't re-derive the whole
  investigation from zero each round. Full-cost re-verification on every
  attempt turns a cheap fix into an expensive loop for no added rigor. See
  [`reviewer.md`](roles/reviewer.md)'s "Keep the report proportional."

## Stage 5 — Done

**What happens:** Work is Done when the Ticket has **sufficient recorded
evidence** that its acceptance criteria were satisfied, project
verification passed (per the Project Audit), scope is accounted for, an
independent Reviewer has Pass'd the work, and — per
[`RULES.md`](RULES.md) — any CONFIRM-gated action along the way was
actually confirmed, not skipped, with no unresolved ESCALATE.

**Done requires at minimum:**
- Every acceptance criterion has an Evidence record.
- Project verification was actually executed via `docket verify`,
  attestation matches the Ticket, exit is 0, and attestation is not stale
  (`docket check-evidence` passes).
- `docket check-scope` passes.
- Independent Reviewer outcome is Pass (adequacy of evidence vs ACs).
- No unresolved CONFIRM or ESCALATE.

**What Done does not mean:** merged, deployed, shipped, or "the agent says
it works." Deployment remains its own CONFIRM-gated action (Rules §5)
after Done, at the human's direction. A successful deploy with missing
Evidence is still not Done.

**Reaching Done is also a natural session boundary.** Once a Ticket (or a
batch of related Tickets) is Done, the conversation that produced it has
done its job — carrying its full history into unrelated work that follows
costs context and money for no benefit the next piece of work actually
needs. Starting a fresh session for the next distinct chunk of work,
rather than extending an already-long one indefinitely, is the default,
not something to only consider once a session is struggling under its own
size.

## Summary table

| Stage | Owner | Produces | Exit gate |
|---|---|---|---|
| Ticket | Planner | Approved Ticket (Evidence blank) | Human approval |
| Implement | Implementer | Implementation | Matches Ticket scope |
| Self-review | Implementer | Diff + completed Evidence | `docket pre-review` exit 0 (final state) |
| Review | Reviewer | Pass / Send-back / Escalate | Evidence audited; AC adequacy judged |
| Done | — | Evidence-backed Done | Pass + evidence + scope + no open gates |
