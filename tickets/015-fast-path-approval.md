# Ticket: Let no-runtime-change Tickets skip approval before code, per project

**Status:** approved
**Owner (Implementer):** Claude
**Retry count:** 0
**Related project audit:** N/A — this repo
**Baseline:** (set when the Ticket starts)
**Worktree:**

## Problem

Stage 1 requires the human to approve every Ticket before any code, however small. For a change with no runtime effect (a README typo, a comment, a doc link), that approval adds a round trip of the human's attention while protecting almost nothing: the Ticket, evidence, the three gates, and the independent Reviewer still run, and the human still decides the merge. The human's attention goes where it buys the least. This has been deferred since grill Q6 ("a real checkpoint at Ticket-approval with a trivial-ticket fast path"; `tickets/README.md`).

No project incident triggered it. The owner grants a narrow freeze exception for it (step 7).

## Approach

1. **Eligibility.** A Ticket may take the fast path only when all four hold:
   - (a) the project has turned the fast path on in `PROJECT_AUDIT.md` (default off);
   - (b) the change has no runtime effect: docs, comments, or content nothing executes or reads at runtime;
   - (c) nothing in the approach is CONFIRM, BLOCK, or ESCALATE under `RULES.md`;
   - (d) the rollback plan is "Revert the commit."
   When any of these is unclear, the Ticket is not eligible.
2. **`core/WORKFLOW.md` Stage 1.** Keep "The human has approved the Ticket. No code is written before this." as the rule, and add the fast path as its one exception: an eligible Ticket goes from `draft` to `in-progress` without `approved`. Everything else is unchanged: the Ticket, Baseline, Evidence, `docket pre-review`, the independent Review, and the human's merge decision. Update the summary table's Ticket row to say "Human approval, or fast path (eligible Tickets only)".
3. **`core/WORKFLOW.md` Stage 4.** The Reviewer checks fast-path eligibility first. A fast-path Ticket that fails any criterion is **Escalate**, not Send-back: the human never approved it, so there is nothing for the Implementer to fix.
4. **`core/roles/planner.md`.** The Planner may declare the fast path only when every criterion holds, by writing in `## Rules check` one line `Fast path: yes` followed by a reason for each criterion (a)–(d). Otherwise it presents the Ticket for approval as today. The Planner tells the human, in the same message, that the Ticket is proceeding on the fast path, so the human can stop it.
5. **`core/roles/reviewer.md`.** Add the eligibility check as the first checklist item, with the Escalate outcome from step 3.
6. **Templates.**
   - `core/templates/project-audit.template.md`: add a `## Workflow options` section with `Fast path (no-runtime-change Tickets skip approval before code): off`.
   - `core/templates/ticket.template.md`: in the `## Rules check` comment, describe the `Fast path: yes` line and its four reasons.
7. **`core/LINE_MEETING.md`.** Add a named freeze exception, dated, in the same form as the Stage 1–3 exceptions. Permitted: the Stage 1 fast-path exception, the Stage 4 eligibility check, the matching role, template, adapter, README, and GUIDE text. Not permitted: skipping Evidence, gates, or Review; any eligibility beyond (a)–(d); tooling changes. The spine is frozen again after.
8. **`core/CHANGELOG.md`.** Entry: date, "no triggering incident; owner exception (LINE_MEETING.md)", what changed, files.
9. **Adapters, README, GUIDE.** Where they say no code before approval without exception (`adapters/claude-code/CLAUDE.md.template`, `adapters/cursor/cursorrules.template`, `README.md` rule 1, `GUIDE.md` Walkthrough 1 and "Who does what"), add the fast-path exception in one clause and point to WORKFLOW.md Stage 1. GUIDE.md Walkthrough 1 shows the typo taking the fast path when the project has it on.
10. **`tickets/README.md`.** Add Ticket 015. Remove the fast-path half of the deferred grill Q6 item; the tiered Review half (Q7) stays deferred.

Out of scope: tooling (`lint-ticket` already accepts a Ticket that never had Status `approved`; AC-7 confirms this), the tiered independent Review (grill Q7), any change to Evidence or gates, and Hechent's side (see Notes).

## Files touched

- core/WORKFLOW.md
- core/roles/planner.md
- core/roles/reviewer.md
- core/templates/project-audit.template.md
- core/templates/ticket.template.md
- core/LINE_MEETING.md
- core/CHANGELOG.md
- adapters/claude-code/CLAUDE.md.template
- adapters/cursor/cursorrules.template
- README.md
- GUIDE.md
- tickets/README.md

## Acceptance criteria

- [ ] AC-1: WORKFLOW.md Stage 1 states the fast path as the only exception to approval before code, lists criteria (a)–(d), says unclear means ineligible, and says Ticket, Baseline, Evidence, pre-review, Review, and the human's merge are unchanged. (manual: read Stage 1)
- [ ] AC-2: WORKFLOW.md Stage 4 and reviewer.md make eligibility the Reviewer's first check, with Escalate for an ineligible fast-path Ticket. (manual)
- [ ] AC-3: planner.md requires the `Fast path: yes` line in Rules check with a reason for each of (a)–(d), and requires telling the human the Ticket is proceeding on the fast path. (manual)
- [ ] AC-4: The Project Audit template has the fast-path option, set to off by default. (manual)
- [ ] AC-5: No adapter template, README.md, or GUIDE.md states approval before code without mentioning the fast-path exception. (command: `grep -n -i "before code\|before a ticket is approved\|before any code" README.md GUIDE.md adapters/*/*.template core/WORKFLOW.md`, each hit read in context)
- [ ] AC-6: LINE_MEETING.md has the named exception with permitted and not-permitted lists, and CHANGELOG.md has the entry. (manual)
- [ ] AC-7: A sample Ticket with Status `in-progress`, a `Fast path: yes` Rules check, and no approval passes `docket lint-ticket`, and the tooling suite passes unchanged. (command + Project verify)

## Rollback plan

Revert the commit. Projects that turned the option on fall back to approval before code, which is today's behavior.

## Rules check

- Editing `core/` is gated by `LINE_MEETING.md`. This Ticket names the freeze exception (step 7); approving it is the owner's sign-off, and step 8 is the changelog entry.
- No deletions, dependencies, CI, or production. Nothing CONFIRM or BLOCK.
- Work goes on a branch, not `main` (RULES §1).
- This Ticket is not itself eligible for the fast path: it changes how the kit behaves, and this repo has no Project Audit opting in.

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

External follow-up, not part of this Ticket: Hechent's `assess` (Docket approval boundary) and `DOCKET-INTEGRATION.md` step 2 assume every Ticket waits for approval. Hechent will need a matching change to honor the fast path when a project opts in; until then, Hechent keeps asking for approval, which is the stricter behavior.
