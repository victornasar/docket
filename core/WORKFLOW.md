# The Workflow

This is the workflow every piece of work moves through, and the set of
handoff points between roles. Nothing moves to the next stage without the
current stage's exit criteria being met. This document defines those
criteria concretely.

```
  TICKET  --->  IMPLEMENT  --->  SELF-REVIEW  --->  REVIEW  --->  DONE
 (Planner)    (Implementer)     (Implementer)     (Reviewer)
```

This describes one Ticket at a time — the default, and almost always the
right choice. When there's an actual backlog of independent, already-
approved Tickets, see [`PARALLEL_LINE.md`](PARALLEL_LINE.md) for running
several of these pipelines at once; it adds claiming, isolation, and a
merge-back step around the same five stages below, unchanged.

## Stage 1 — Ticket

**Owner:** Planner.
**What happens:** The Planner turns a raw request into a Ticket using
[`ticket.template.md`](templates/ticket.template.md): Problem, Approach,
Files Touched, Acceptance Criteria (a checklist, not prose), Rollback Plan.
If the project hasn't had a Project Audit run yet, or the request touches
an area the Project Audit didn't cover, that gets done or updated first.

**Exit criteria (must all be true before moving to Implement):**
- The Ticket has concrete, checkable acceptance criteria — not "works
  correctly" but specific, verifiable statements.
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

**Exit criteria (must all be true before moving to Self-review):**
- Every item in the Ticket's approach has been implemented.
- No files were touched outside the Ticket's Files Touched list. If that
  turned out to be necessary, this is scope creep — see §7 in
  [`RULES.md`](RULES.md) — and gets flagged rather than silently done.
- Any action the Rules mark CONFIRM encountered mid-implementation
  was actually confirmed before it happened, not after.

## Stage 3 — Self-review

**Owner:** Implementer (before handing off).
**What happens:** The Implementer checks its own work against the Ticket
before anyone else looks at it — the goal is to catch what the Reviewer
would catch, so the Review stage is confirmation, not discovery. Follow
[`recipe-self-review.md`](recipes/recipe-self-review.md).

**Exit criteria (must all be true before moving to Review):**
- Every acceptance criterion on the Ticket has been checked, one by one,
  against the actual result — not assumed.
- Tests relevant to the change exist and pass locally.
- No debug output, commented-out code, or scratch artifacts left in the
  diff.
- The diff matches the Files Touched list exactly.
- The rollback plan from the Ticket is still accurate for what was
  actually built (if the implementation diverged from the plan, the
  rollback plan is updated to match).

## Stage 4 — Review

**Owner:** Reviewer.
**What happens:** The Reviewer — with **read-only** access, it cannot edit
anything — checks the self-reviewed work against the Ticket's acceptance
criteria one item at a time. This is an independent check, not a rubber
stamp of the Implementer's self-review. See [`reviewer.md`](roles/reviewer.md)
for the full checklist.

**The Reviewer is invoked as a genuinely separate context, not a role
switch.** When the tool in use supports spawning an independent agent
(e.g. Claude Code's Agent/Task tool with a dedicated `reviewer`
definition), Review means actually spawning it — handing it only the
Ticket and the diff, not the Implement/Self-review conversation that
produced them. A reviewer who remembers writing the code will defend its
own reasoning instead of checking it; a reviewer with no memory of writing
it can't. When the tool has no such mechanism, the adapter for that tool
states its best available approximation explicitly rather than silently
treating a same-context role-switch as equivalent — see each adapter's own
notes on this (Claude Code's is closest to the real thing; Cursor's is a
weaker approximation, documented as such).

**Possible outcomes:**

1. **Pass** — every acceptance criterion is met, no Rules violations, diff
   matches scope. Moves to Done.
2. **Send-back** — one or more acceptance criteria aren't met, or the diff
   has scope creep, or tests are missing/failing. The Reviewer writes
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
  (a build, the specific test), and reconcile the Ticket's own bookkeeping
  (Files Touched, acceptance criteria) against the now-current diff — but
  don't re-derive the whole investigation from zero each round. Full-cost
  re-verification on every attempt turns a cheap fix into an expensive
  loop for no added rigor. See [`reviewer.md`](roles/reviewer.md)'s
  "Keep the report proportional."

## Stage 5 — Done

**What happens:** Work is done. This means: acceptance criteria verifiably
met, tests passing, no unresolved Reviewer feedback, and — per
[`RULES.md`](RULES.md) — any CONFIRM-gated action along the way was
actually confirmed, not skipped. "Done" is the state where a human can
merge/deploy without re-checking the Reviewer's work from scratch.

**What "done" does not mean:** it does not mean deployed to production.
Deployment is its own CONFIRM-gated action (Rules §5) that happens after
Done, at the human's direction.

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
| Ticket | Planner | Approved Ticket | Human approval |
| Implement | Implementer | Implementation | Matches Ticket scope |
| Self-review | Implementer | Self-reviewed diff | Self-checklist passed |
| Review | Reviewer | Pass / Send-back / Escalate | Acceptance criteria independently verified |
| Done | — | Done | No open Reviewer feedback |
