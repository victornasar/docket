# Ticket: Say that "approved Ticket" includes an eligible fast-path Ticket

**Status:** approved
**Owner (Implementer):** Claude
**Retry count:** 0
**Related project audit:** N/A — this repo
**Baseline:** (set when the Ticket starts)
**Worktree:**

## Problem

Ticket 015 added the fast path, but six places still say "approved Ticket" as if approval were the only way in: `core/WORKFLOW.md` Stage 2 ("execute the approved Ticket") and its summary table, `core/roles/implementer.md` and `core/roles/planner.md` (each role's Purpose line), and two lines in the Claude Code adapter (`CLAUDE.md.template`, `README.md`). An Implementer reading only its role could conclude a fast-path Ticket may not be started. Ticket 015's independent Review flagged this as a Standards note.

## Approach

1. In `core/WORKFLOW.md` Stage 1, right after the fast-path paragraph, add one sentence: wherever Docket says "approved Ticket", that includes a fast-path Ticket that met all four criteria. One definition, instead of editing six places.
2. In `core/WORKFLOW.md` Stage 2, change "execute the approved Ticket" to "execute the approved Ticket (see Stage 1 for the fast path)", since it is the line an Implementer reads when starting.
3. Add Ticket 016 to `tickets/README.md`.
4. Add a short `core/CHANGELOG.md` entry that references Ticket 015's entry and says it completes that change's wording.

Out of scope: the role files and adapters (step 1's definition covers them); `adapters/claude-code/README.md:82` (it concerns large or ambiguous requests, which can never take the fast path). Also out of scope: recording approval in the Ticket. A Ticket that skips approval *without* declaring the fast path can be caught only by the Reviewer's general Rules check, because no Ticket field records that approval happened. That would be a structural change and needs its own incident.

## Files touched

- core/WORKFLOW.md
- core/CHANGELOG.md
- tickets/README.md

## Acceptance criteria

- [ ] AC-1: WORKFLOW.md Stage 1 says "approved Ticket" includes an eligible fast-path Ticket, in one sentence after the fast-path paragraph. (manual)
- [ ] AC-2: WORKFLOW.md Stage 2's opening line points to Stage 1 for the fast path. (manual)
- [ ] AC-3: CHANGELOG.md has an entry referencing Ticket 015, and tickets/README.md lists Ticket 016. (manual)
- [ ] AC-4: No file other than the three in Files touched (and this Ticket) changed. (command: `docket check-scope`)
- [ ] AC-5: The tooling suite passes unchanged. (test: Project verify)

## Rollback plan

Revert the commit.

## Rules check

- Editing `core/` is gated by `LINE_MEETING.md`. This is wording that completes the 2026-11-25 fast-path exception (Ticket 015: "matching role, template, adapter, README, and GUIDE text"); it adds no rule. Approving this Ticket is the owner's sign-off for that.
- Nothing CONFIRM or BLOCK. Work goes on a branch.
- Not eligible for the fast path: this repo has no Project Audit opting in.

## Evidence

### Project verify

```text
command:
exit:
log:
ran_at:
git_head:
tree_fingerprint:
attestation:
```

### Acceptance criteria

```text
id: AC-1
criterion:
method:
how:
result:
evidence:
notes:
```

### Scope review

```text
diff_vs_files_touched:
extras:
justified:
notes:
```

## Notes for the Reviewer

Follows Ticket 015's Review Standards notes 1 and 4. Note 2 (undeclared skips) is deliberately out of scope; see Approach.
