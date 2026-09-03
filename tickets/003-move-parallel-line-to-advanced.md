# Ticket: Move `PARALLEL_LINE.md` out of the frozen spine into `advanced/`

**Status:** done
**Owner (Implementer):** Claude (this session)
**Retry count:** 0
**Related project Mise en Place:** N/A — Tabouleh's own repo
**Worktree:** (blank)

**Depends on:** 001 (needs post-rename `core/WORKFLOW.md` and the
vocab-updated `PARALLEL_LINE.md`).

## Problem

`core/PARALLEL_LINE.md` describes running several Ticket pipelines at once
with claiming, worktree isolation, and merge-back. The grilling session
fixed Tabouleh as single-operator first (Q1); one operator cannot
meaningfully run three concurrent implement→self-review→review pipelines,
and the coordination machinery is a team mechanism. It was a deliberate
build, not an incident fix, but the premise it was built on changed. The
decision (Q17) is to move it out of the frozen spine into an `advanced/`
area, clearly marked as team / heavy-multi-agent use that has not been
exercised on a solo operator — without deleting the thinking.

## Approach

1. `git mv core/PARALLEL_LINE.md advanced/PARALLEL_LINE.md`.
2. Add a note block at the top of the moved file: "Status: advanced /
   unproven. This describes running multiple Tickets concurrently and
   assumes either multiple human operators or aggressive multi-subagent
   use. It has not been exercised on a single-operator project. The
   standard workflow is one Ticket at a time (see
   `../core/WORKFLOW.md`). Not part of the frozen spine — may change or
   be removed."
3. In `core/WORKFLOW.md`, find the paragraph that points at
   `PARALLEL_LINE.md` (currently near the top, "When there's an actual
   backlog of independent, already-approved Tickets, see…"). Reword it to:
   the workflow is one Ticket at a time; an experimental description of
   concurrent Tickets lives in `advanced/PARALLEL_LINE.md` and is not part
   of the standard flow. Keep the link, change the framing from "here's
   the other mode" to "here's an experiment."
4. Grep `core/` and `README.md`-adjacent files for other `PARALLEL_LINE`
   references. Any in `core/**` get repointed to `advanced/`. (References
   in `README.md` / `setup/` are ticket 005's problem — note them in
   handoff, don't touch them here.)
5. Do not edit the body of `PARALLEL_LINE.md` beyond the status note —
   its content moves as-is.

## Files touched

- `core/PARALLEL_LINE.md` → `advanced/PARALLEL_LINE.md` (move + status note)
- `core/WORKFLOW.md` (reword the one referencing paragraph)
- Any other `core/**` file with a `PARALLEL_LINE` reference (grep to confirm; expected: only `WORKFLOW.md`)

## Acceptance criteria

- [ ] `advanced/PARALLEL_LINE.md` exists; `core/PARALLEL_LINE.md` does not;
      `git status` shows it as a rename (`R`).
- [ ] The moved file has the "advanced / unproven / not frozen spine"
      status note at the top and its original body otherwise unchanged
      (diff shows only the added note).
- [ ] `core/WORKFLOW.md` no longer presents concurrent Tickets as a
      supported mode — the reference now frames it as an experiment in
      `advanced/` and the link resolves.
- [ ] `grep -rn "PARALLEL_LINE" core/` returns only the repointed
      reference(s) in `WORKFLOW.md`, all pointing at `advanced/`.
- [ ] Handoff notes list any `PARALLEL_LINE` references found in
      `README.md` / `setup/` for ticket 005 to handle.

## Rollback plan

Single commit. `git revert <sha>` moves the file back to `core/` and
restores the `WORKFLOW.md` wording.

## Rules check

- No BLOCK action. `git mv` within the repo; editing `core/` is
  CONFIRM-gated (§2) and this ticket's approval covers it. No file
  overwritten without reading.

## Notes for the Reviewer

<Filled during Self-review.>
